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

Commands written here are not meant to be instructive; this isn't a tutorial. They're a history of the steps @damouse carried out to set up the tests. 

### zfs

See here for all the information you could want to know about setting up zfs: https://pthree.org/2012/12/04/zfs-administration-part-i-vdevs/

Install zfs: 

    sudo apt install zfsutils-linux

To use a disk: 

    sudo zpool create fsb sda -f

To use a file:

    mkdir zfs
    
    for i in {1..4}; do dd if=/dev/zero of=./zfs/vdev$i bs=1G count=4 &> /dev/null; done

Create a pool from files: 

    zpool create tank /home/damouse/code/python/fsbench/zfs/vdev1 /home/damouse/code/python/fsbench/zfs/vdev2 /home/damouse/code/python/fsbench/zfs/vdev3 /home/damouse/code/python/fsbench/zfs/vdev4

Destroy a pool:

    zpool destroy fsb


### pg

Find installtion instructions for postgres online. Once installed, you need to change the data directory for the postgres database.

    sudo systemctl stop postgresql
    sudo mv postgresql postgresql.bak
    sudo cp -aRv /var/lib/postgresql/ /media/damouse/fsb/
    ln -s /media/damouse/fsb/postgresql/ postgresql
    sudo chown postgres /var/lib/postgresql
    sudo systemctl start postgresql


### apache

- Remove the restriction on root access from 'etc/apache2/apache2.conf'
- Configure static serving from the new directory. Check the files in ./config. These are copies of config files that belong in /etc/apache2


Restart the apache service:

    sudu systemctl restart apache2

Note that apache caching is turned off with the following:

<filesMatch ".jpg">
  FileETag None
  <ifModule mod_headers.c>
     Header unset ETag
     Header set Cache-Control "max-age=0, no-cache, no-store, must-revalidate"
     Header set Pragma "no-cache"
     Header set Expires "Wed, 11 Jan 1984 05:00:00 GMT"
  </ifModule>
</filesMatch>

On windows you'll have to a) map the drive to the webserver b) make the webserver allow all requests.

In Apache/conf/httpd.conf: 

    DocumentRoot "E:/"

Also change the permissions on the root directory element from "Require all denied" to "Require all granted"


## Compilation

Download go source:

    git clone git@github.com:golang/go.git
    # export GOROOT_BOOTSTRAP=$(which go)
    export GOROOT_BOOTSTRAP=/usr/local/go/
    ./src/all.bash

Or for windows:

    SET GOROOT_BOOTSTRAP=C:\Go

The windows compilation test was also tested using the built in Measure-Command utility.

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

## Conditions

Tested on:

- i7 6700k (8 threads@4.2gHz, 8MB)
- 32GB DDR4
- SM951 Nvme 512GB (system drive)
- WD 500GB HDD (testing drive)