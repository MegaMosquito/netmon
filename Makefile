#
# A convenience Makefile with commonly used commands for the LAN monitor
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


# Configure all of these "MY_" variables for your personal situation

MY_SUBNET_CIDR            := '192.168.123.0/24'

MY_NETMON_HOST_ADDRESS    := '192.168.123.3'
MY_NETMON_HOST_MAC        := 'B8:27:EB:81:F4:79'
MY_NETMON_HOST_COMMENT    := '(Network Monitor)'

MY_COUCHDB_ADDRESS        := '192.168.123.3'
MY_COUCHDB_PORT           := 5984
MY_COUCHDB_USER           := 'admin'
MY_COUCHDB_PASSWORD       := 'p4ssw0rd'
MY_COUCHDB_DATABASE       := 'lan_hosts'
MY_COUCHDB_TIME_FORMAT    := '%Y-%m-%d %H:%M:%S'

MY_BETWEEN_SCANS_SECONDS  := 300
MY_IP_PERSISTS_MINUTES    := 0
MY_FORGET_AFTER_DAYS      := 0


# Running `make` with no target builds and runs netmon as a restarting daemon
all: build run

# Build the container and tag it, "netmon".
build:
	docker build -t netmon .

# Running `make dev` will setup a working environment, just the way I like it.
# On entry to the container's bash shell, run `cd /outside/src` to work here.
dev: build
	-docker rm -f netmon 2> /dev/null || :
	docker run -it --privileged --net=host \
	    --name netmon \
	    -e MY_SUBNET_CIDR=$(MY_SUBNET_CIDR) \
	    -e MY_NETMON_HOST_ADDRESS=$(MY_NETMON_HOST_ADDRESS) \
	    -e MY_NETMON_HOST_MAC=$(MY_NETMON_HOST_MAC) \
	    -e MY_NETMON_HOST_COMMENT=$(MY_NETMON_HOST_COMMENT) \
	    -e MY_COUCHDB_ADDRESS=$(MY_COUCHDB_ADDRESS) \
	    -e MY_COUCHDB_PORT=$(MY_COUCHDB_PORT) \
	    -e MY_COUCHDB_USER=$(MY_COUCHDB_USER) \
	    -e MY_COUCHDB_PASSWORD=$(MY_COUCHDB_PASSWORD) \
	    -e MY_COUCHDB_DATABASE=$(MY_COUCHDB_DATABASE) \
	    -e MY_COUCHDB_TIME_FORMAT=$(MY_COUCHDB_TIME_FORMAT) \
	    -e MY_BETWEEN_SCANS_SECONDS=$(MY_BETWEEN_SCANS_SECONDS) \
	    -e MY_IP_PERSISTS_MINUTES=$(MY_IP_PERSISTS_MINUTES) \
	    -e MY_FORGET_AFTER_DAYS=$(MY_FORGET_AFTER_DAYS) \
	    --volume `pwd`:/outside netmon /bin/sh

# Run the container as a daemon (build not forecd here, sp must build it first)
run:
	-docker rm -f netmon 2>/dev/null || :
	docker run -d --privileged --net=host \
	    --name netmon --restart unless-stopped \
	    -e MY_SUBNET_CIDR=$(MY_SUBNET_CIDR) \
	    -e MY_NETMON_HOST_ADDRESS=$(MY_NETMON_HOST_ADDRESS) \
	    -e MY_NETMON_HOST_MAC=$(MY_NETMON_HOST_MAC) \
	    -e MY_NETMON_HOST_COMMENT=$(MY_NETMON_HOST_COMMENT) \
	    -e MY_COUCHDB_ADDRESS=$(MY_COUCHDB_ADDRESS) \
	    -e MY_COUCHDB_PORT=$(MY_COUCHDB_PORT) \
	    -e MY_COUCHDB_USER=$(MY_COUCHDB_USER) \
	    -e MY_COUCHDB_PASSWORD=$(MY_COUCHDB_PASSWORD) \
	    -e MY_COUCHDB_DATABASE=$(MY_COUCHDB_DATABASE) \
	    -e MY_COUCHDB_TIME_FORMAT=$(MY_COUCHDB_TIME_FORMAT) \
	    -e MY_BETWEEN_SCANS_SECONDS=$(MY_BETWEEN_SCANS_SECONDS) \
	    -e MY_IP_PERSISTS_MINUTES=$(MY_IP_PERSISTS_MINUTES) \
	    -e MY_FORGET_AFTER_DAYS=$(MY_FORGET_AFTER_DAYS) \
	    netmon

# Enter the context of the daemon container
exec:
	docker exec -it netmon /bin/sh

# Stop the daemon container
stop:
	-docker rm -f netmon 2>/dev/null || :

# Stop the daemon container, and cleanup
clean: stop
	-docker rmi netmon 2>/dev/null || :

# Declare all non-file-system targets as .PHONY
.PHONY: all build dev run exec stop clean

