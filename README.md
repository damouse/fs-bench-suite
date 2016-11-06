# Filesystem Comparison Benchmarks

- Compilation
    + Golang
    + Apache
- Webserver (using pg, mongo)
    + Go
    + Node
- Image Server
    + Nginx 
    + Apache


## Setup 

### zfs

See here for all the information you could want to know about setting up zfs: https://pthree.org/2012/12/04/zfs-administration-part-i-vdevs/

Install zfs: 

    sudo apt install zfsutils-linux

To use a disk: 

    sudo fdisk -l

To use a file:

    mkdir zfs
    
    for i in {1..4}; do dd if=/dev/zero of=./zfs/vdev$i bs=1G count=4 &> /dev/null; done

Create a pool from files: 

    zpool create tank /home/damouse/code/python/fsbench/zfs/vdev1 /home/damouse/code/python/fsbench/zfs/vdev2 /home/damouse/code/python/fsbench/zfs/vdev3 /home/damouse/code/python/fsbench/zfs/vdev4

Destroy a pool:

    zpool destroy tank


### pg

Find installtion instructions for postgres online. Once installed, you need to change the data directory for the postgres database.

    sudo systemctl stop postgresql
    sudo mv postgresql postgresql.bak
    sudo cp -aRv /var/lib/postgresql/ /media/damouse/fsb/
    ln -s /media/damouse/fsb/postgresql/ postgresql
    sudo chown postgres /var/lib/postgresql
    sudo systemctl start postgresql



## Compilation

Download go source:

    git clone git@github.com:golang/go.git
    # export GOROOT_BOOTSTRAP=$(which go)
    export GOROOT_BOOTSTRAP=/usr/local/go/
    ./src/all.bash


## Webserver

Install postgres:

    (in progress)

Install webserver deps:

    go get github.com/jinzhu/gorm
    go get github.com/lib/pq
    go get github.com/ant0ine/go-json-rest/rest



Instructions on building go from source: https://golang.org/doc/install/source


## Misc

What do we need here?

- Reporting and Numbers system set up with pyplot
- Webserver test
- Install databases (mongo is already up, right?)
- Setup webserver
