# netmon

A Local Area Network (LAN) monitor daemon that uses nmap. It periodically scans the network and compares the MAC addresses found against a list of known host MAC addresses. It works to detect when infrastructure hosts (hosts which are expected to always be online) have gone offline. It also works to detect unexpected arrivals of hosts on the network. Keeping this daemon online on my network gives me visibility into the set of machines that are connected to my network plumbing.
