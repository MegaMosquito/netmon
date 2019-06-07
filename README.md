# netmon

A Local Area Network (LAN) monitor daemon that uses nmap. It periodically scans the network and compares the MAC addresses found against a list of known host MAC addresses. It works to detect when infrastructure hosts (hosts which are expected to always be online) have gone offline. It also works to detect unexpected arrivals of hosts on the network. Keeping this daemon online on my network gives me visibility into the set of machines that are connected to my network plumbing.

This network monitor stores its data into a couchdb instance that must also be running locally. This is the one I use:
 * [https://github.com/MegaMosquito/couchdb.git](https://github.com/MegaMosquito/couchdb.git)
Clone it; cd into it; run `make`, and you're done. If you want to get all fancy about it you could change the password to be different from the one in this very public repo. You will need to use the same one in the couchdb container and in the netmon container, of course.

If you wish to provide a list of your known hosts, you will want to edit the `src/known_hosts.py` file. There are some comments in that file to guide you. Doing this is not strictly necessary, but if you do this the monitor daemon will provide a much more satisfying picture of what's up in your network.

Note that when nmap runs it tends to disrupt network connections (my ssh sessions typically freeze for somethin like 5 seconds then resume). This is annoying if you set the scanning rate high, but less so if the scans are less frequent.

