#
# Known Hosts
#
# Provide information here about the machines you know about on your network.
# You can can the netmon as-is (with no `known_hosts` defined) and then use
# the information it provides to figure out which machines are which, then
# come back and add them here later (then rebuild/restart the network monitor).
#
# For each host you must provide these fields:
#
#   "mac"     MAC address, in colon-delimited capital letter format
#   "info"    description of the host (any string can go here)
#   "infra"   is this host "infrastructure" (and expected to always be online)
#   "static"  is this host assigned a static IP address (unchanging, not dynamic)
#   "octet"   (only if "static" is true) provide the last octet of the address
#
# Some example host records are shown below.
#
# {"static":True,  "infra":True,  "mac":'3C:37:86:5F:EC:39', "octet":1,   "info":'Gateway'},
# {"static":False, "infra":True,  "mac":'10:A4:BE:4C:8C:3C', "info":'Security Camera #1, Driveway'},
# {"static":False, "infra":False, "mac":'18:FE:34:DD:CB:62', "info":'Purple Air ESP_DDBA54'},
#


known_hosts = [

#     *** Put Your Known Hosts In Here! ***

]

