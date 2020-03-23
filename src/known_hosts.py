#
# Known Hosts
#
# Provide information here about the machines you know about on your network.
# You can can the netmon as-is (with no `known_hosts` defined) and then use
# the information it provides to figure out which machines are which, then
# come back and add them here later (then rebuild/restart the network monitor).
#
# For each host you must provide all except the "optional" fields below:
#
#   "mac"     MAC address, in colon-delimited capital letter format
#   "infra"   (optionL) is this host "infrastructure"? (always online)
#   "octet"   (optional) provides last address octet for static address hosts
#   "info"    description of the host (any string can go here)
#
# Some example host records are shown below.
#
# {"mac":'3C:37:86:5F:EC:39', "infra":True, "octet":1, "info":"Gateway"},
# {"mac":'10:A4:BE:4C:8C:3C', "infra":True, "info":"Security Cam #1, Porch"},
# {"mac":'18:FE:34:DD:CB:62', "info":"Purple Air ESP_DDBA54"},
#


known_hosts = [

]

