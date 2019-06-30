#!/usr/bin/python3
#
# A network monitor daemon container that uses nmap, and feeds data
# into couchdb. If you provide information about the hosts you know
# then it will use this information to paint a more rich picture of
# what's happening on your network.
#
# Note that when nmap runs it tends to disrupt network connections (my ssh
# sessions typically freeze for somethin like 5 seconds then resume). This
# is annoying if you set the scanning rate high, but less so if the scans
# are less frequent.
#
# Written by Glen Darling (mosquito@darlingevil.com), December 2018.
#


import os



# Configure all of these "MY_" environment variables for your situation

MY_SUBNET_CIDR            = os.environ['MY_SUBNET_CIDR']

MY_NETMON_HOST_ADDRESS    = os.environ['MY_NETMON_HOST_ADDRESS']
MY_NETMON_HOST_MAC        = os.environ['MY_NETMON_HOST_MAC']
MY_NETMON_HOST_COMMENT    = os.environ['MY_NETMON_HOST_COMMENT']

MY_COUCHDB_ADDRESS        = os.environ['MY_COUCHDB_ADDRESS']
MY_COUCHDB_PORT           = int(os.environ['MY_COUCHDB_PORT'])
MY_COUCHDB_USER           = os.environ['MY_COUCHDB_USER']
MY_COUCHDB_PASSWORD       = os.environ['MY_COUCHDB_PASSWORD']
MY_COUCHDB_DATABASE       = os.environ['MY_COUCHDB_DATABASE']
MY_COUCHDB_TIME_FORMAT    = os.environ['MY_COUCHDB_TIME_FORMAT']

MY_BETWEEN_SCANS_SECONDS  = int(os.environ['MY_BETWEEN_SCANS_SECONDS'])
MY_IP_PERSISTS_MINUTES    = int(os.environ['MY_IP_PERSISTS_MINUTES'])
MY_FORGET_AFTER_DAYS      = int(os.environ['MY_FORGET_AFTER_DAYS'])



import sys
import signal
import subprocess
import threading
import time
import datetime
import json
import traceback
import urllib.parse


# Get my manually-edited list of known hosts' MAC addresses
from known_hosts import known_hosts

# Get the Host and DB classes
from db import Host, DB

# Get the LAN2json class (for its scan and portscan static methods)
from LAN2json.LAN2json import LAN2json



# Instantiate the db object (i.e., connect to CouchDB, and open our DB)
db = DB( \
  MY_COUCHDB_ADDRESS,
  MY_COUCHDB_PORT,
  MY_COUCHDB_USER,
  MY_COUCHDB_PASSWORD,
  MY_COUCHDB_DATABASE,
  MY_COUCHDB_TIME_FORMAT)


# Output control (yeah, there are better ways to do this)
def show(str):
  # print(str)
  pass

# Run the 'nmap' scan...
def scan():
  try:
    show("\nScanning...")
    scanned_hosts = LAN2json.scan( \
      MY_SUBNET_CIDR, \
      MY_NETMON_HOST_ADDRESS, \
      MY_NETMON_HOST_MAC, \
      MY_NETMON_HOST_COMMENT)
    show(str(len(scanned_hosts)) + " hosts were found on the LAN...")
    i = 0
    for h in scanned_hosts:
      # show(json.dumps(h))
      # Force MAC address to use uppercase hexadecimal
      mac = h['mac'].upper()
      ip = h['ip']
      comment = h['comment']
      host = db.get(mac)
      if host:
        host['ip'] = ip
        if not ('first_seen' in host):
          host['first_seen'] = db.now()
        host['last_seen'] = db.now()
      else:
        host = Host.new_unknown_host(mac, ip, comment, db.now())
      if not host['known']:
        i += 1
      db.put(host)
    show(str(i) + " of those hosts have *unknown* MAC addresses.")
  except Exception as e:
    print("*** Exception during scanning:")
    traceback.print_exc()
  sys.stdout.flush()


# Walk the DB to cleanup old IP addresses and old unknown hosts, if appropriate
def cleanup():
  try:
    show("Reviewing...")
    db_hosts = db.get_all()
    i = 0
    u = 0
    for h in db_hosts:
      # show(json.dumps(h))
      if 'last_seen' in h:
        last_seen = h['last_seen']
        how_long_ago_seconds = db.seconds_since(last_seen)

        # Wipe IP addresses from any hosts not seen in MY_IP_PERSISTS_MINUTES
        if MY_IP_PERSISTS_MINUTES > 0 and last_seen and 'ip' in h:
          if how_long_ago_seconds > (MY_IP_PERSISTS_MINUTES * 60):
            show("Removing IP address " + h['ip'] + " from " + h['mac'] + " in the DB.")
            h['ip'] = None
            db.put(h)
            i += 1

        # Forget any unknown hosts not seen for MY_FORGET_AFTER_DAYS
        if MY_FORGET_AFTER_DAYS > 0 and last_seen and not h['known']:
          if how_long_ago_seconds > (MY_FORGET_AFTER_DAYS * 24 * 60 * 60):
            show("Deleting *unknown* host " + h['mac'] + " from the DB.")
            db.delete(h['mac'])
            u += 1

    if i > 0:
      show("Cleared IP addresses from " + str(i) + " hosts in the DB.")
    if u > 0:
      show("Deleted " + str(i) + " *unknown* hosts from the DB.")
  except Exception as e:
    print("*** Exception during cleaning:")
    traceback.print_exc()
  sys.stdout.flush()


if __name__ == '__main__':

  print("Found " + str(len(known_hosts)) + " hosts in known_hosts.py.")
  for kh in known_hosts:
    # Force MAC address to use uppercase hexadecimal
    kh['mac'] = kh['mac'].upper()
    h = Host.new_host_from_known_hosts(known_hosts, kh)
    db.put(h)
  print(str(db))
  sys.stdout.flush()

  print("Starting LAN monitor daemon...")
  while True:
    scan()
    cleanup()
    show("Sleeping...")
    time.sleep(MY_BETWEEN_SCANS_SECONDS)

