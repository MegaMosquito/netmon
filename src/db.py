#!/usr/bin/python3


import sys
import time
import datetime
import traceback


# Don't forget to `pip install couchdb`
import couchdb


# A simple class for host objects
class Host:

  # Generic pseudo-constructor
  @staticmethod
  def new_host(id, rev, mac, known, ip, static, octet, infra, info, first_seen, last_seen):
    host = dict()
    host['_id'] = id
    host['_rev'] = rev
    host['mac'] = mac
    host['known'] = known
    host['ip'] = ip
    host['static'] = static
    host['octet'] = octet
    host['infra'] = infra
    host['info'] = info
    host['first_seen'] = first_seen
    host['last_seen'] = last_seen
    return host

  # Pseudo-constructor for known hosts
  @staticmethod
  def new_host_from_known_hosts(known_hosts, kh):
    host = dict()
    host['_id'] = kh['mac']
    host['mac'] = kh['mac']
    host['known'] = True
    host['static'] = kh['static']
    octet = 999
    if 'octet' in kh: octet = kh['octet']
    host['octet'] = octet
    host['infra'] = kh['infra']
    host['info'] = kh['info']
    host['ip'] = ''
    return host

  # Pseudo-constructor for discovered unknown hosts
  @staticmethod
  def new_unknown_host(mac, ip, info, now):
    host = dict()
    host['_id'] = mac
    host['mac'] = mac
    host['known'] = False
    host['ip'] = ip
    host['octet'] = ip.split('.')[-1]
    host['info'] = info
    host['first_seen'] = now
    host['last_seen'] = now
    return host

  # Static method for stringification
  @staticmethod
  def to_str(host):
    return 'Host(' + str(host['_id']) + ',"' + host['info'] + '")'
    #ip = "None"
    #if 'ip' in host: ip = host['ip']
    #return("Host( " + \
    #  "_id:" + host['_id'] + \
    #  ", _rev:" + host['_rev'] + \
    #  ", mac:" + host['mac'] + \
    #  ", ip:" + str(ip) + \
    #  " )")


# A class for our database of "host" documents
class DB:

  def __init__(self, address, port, user, password, database, time_format):
    self.db = None
    self.name = database
    self.time_format = time_format

    # Try forever to connect
    while True:
      print("Attempting to connect to CouchDB server at " + address + ":" + str(port) + "...")
      couchdbserver = couchdb.Server('http://%s:%s@%s:%d/' % ( \
        user, \
        password, \
        address, \
        port))
      if couchdbserver:
        break
      print("CouchDB server not accessible. Will retry...")
      time.sleep(10)

    # Connected!
    print("Connected to CouchDB server.")

    # Open or create our database
    print("Attempting to open the \"" + database + "\" DB...")
    if database in couchdbserver:
      self.db = couchdbserver[database]
    else:
      self.db = couchdbserver.create(database)

    # Done!
    print('CouchDB database "' + database + '" is open and ready for use.')
    sys.stdout.flush()

  # Instance method to get all the DB "host" documents
  def get_all(self):
    return self.db.view('_all_docs')

  # Instance method to get an appropriately formatted string representing "now"
  def now(self):
    return datetime.datetime.now().strftime(self.time_format)

  # Instance method to get seconds since a specified datetime
  def seconds_since(self, t):
    then = datetime.datetime.strptime(t, self.time_format)
    now = datetime.datetime.now()
    return (now - then).total_seconds()

  # Instance method to delete a "host" document from the DB using MAC as '_id'
  def delete(self, mac):
    h = self.db.get(mac)
    if h:
      # print("DB.delete():  mac=" + mac + " *X* " + str(doc))
      self.db.delete(h)
    else:
      # print("DB.delete():  mac=" + mac + " <-- NOT FOUND! **********")
      pass

  # Instance method to read a DB "host" document using MAC as '_id'
  def get(self, mac):
    doc = None
    try:
      doc = self.db.get(mac)
      if doc:
        # print("DB.get():  mac=" + mac + " --> " + Host.to_str(doc))
        pass
      else:
        # print("DB.get():  mac=" + mac + " <-- NOT FOUND! **********")
        doc = None
    except Exception as e:
      print("*** Exception during DB.get(" + mac + "):")
      traceback.print_exc()
      doc = None
    return doc

  # Instance method to compute the older of two dates
  def older(self, date0, date1):
    if not date0: return date1
    if not date1: return date0
    d0 = datetime.datetime.now() - datetime.datetime.strptime(date0, self.time_format)
    d1 = datetime.datetime.now() - datetime.datetime.strptime(date1, self.time_format)
    if d0.total_seconds() > d1.total_seconds():
      return date0
    else:
      return date1

  # Instance method to compute the younger of two dates
  def younger(self, date0, date1):
    if not date0: return date1
    if not date1: return date0
    d0 = datetime.datetime.now() - datetime.datetime.strptime(date0, self.time_format)
    d1 = datetime.datetime.now() - datetime.datetime.strptime(date1, self.time_format)
    if d0.total_seconds() < d1.total_seconds():
      return date0
    else:
      return date1

  # Instance method to merge an existing host with some updated data in an other
  def merge(self, existing, other):
    assert(existing['mac'] == other['mac'])
    if other['known'] and not existing['known']:
      existing['known'] = True
      existing['static'] = other['static']
      existing['octet'] = other['octet']
      existing['infra'] = other['infra']
      existing['info'] = other['info']
    if 'ip' in other:
      existing['ip'] = other['ip']
      existing['octet'] = other['ip'].split('.')[-1]
    if 'first_seen' in other:
      if 'first_seen' in existing:
        existing['first_seen'] = self.older(existing['first_seen'], other['first_seen'])
      else:
        existing['first_seen'] = other['first_seen']
    if 'last_seen' in other:
      if 'last_seen' in existing:
        existing['last_seen'] = self.younger(existing['last_seen'], other['last_seen'])
      else:
        existing['last_seen'] = other['last_seen']
    return existing

  # Instance method to write one DB "host" document using MAC as '_id'
  def put(self, host):
    try:
      id = host['_id']
      doc = host
      # Does it exist in the DB already?
      existing = self.get(id)
      if existing:
        doc = self.merge(existing, host)
        # print("DB.put: [update] " + Host.to_str(doc))
        self.db[id] = doc
      else:
        # print("DB.put: [new] " + Host.to_str(doc))
        self.db.save(doc)
    except Exception as e:
      print("*** Exception during DB.put(" + host['_id'] + "):")
      traceback.print_exc()
      doc = None

  # Instance method for stringification
  def __str__(self):
    return "DB( name:" + self.name + ", docs:" + str(len(self.db.view('_all_docs'))) + " )"



