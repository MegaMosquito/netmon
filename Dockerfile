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

# This should build and run on any Raspberry Pi0W, Pi2*, Pi3*, and other ARM.
FROM arm32v6/python:3-alpine

# Install required modules and tools
RUN apk --no-cache --update add nmap git

# Install couchdb interface
RUN pip install couchdb

# Install convenience tools (may omit these in production)
RUN apk --no-cache --update add vim curl jq

# Copy over the netmon files
RUN mkdir netmon
WORKDIR /netmon
COPY ./src/*.py /netmon/

# Install LAN2json and rfc1340
RUN git clone https://github.com/MegaMosquito/LAN2json.git
RUN cd LAN2json; git clone https://github.com/MegaMosquito/rfc1340.git

# Start up the daemon process
CMD python netmon.py >/dev/null 2>&1

