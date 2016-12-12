# Filesystem Comparison Benchmarks

Commands written here and in utils.sh are not meant to be instructive; this isn't a tutorial. Its a history of the commands @damouse carried out to set up and run the tests.

## zfs

See here for all the information you could want to know about setting up zfs: https://pthree.org/2012/12/04/zfs-administration-part-i-vdevs/. The file utils.sh list the steps taken to setup the environment. 


## apache

- Remove the restriction on root access from 'etc/apache2/apache2.conf'
- Configure static serving from the new directory. Check the files in ./config. These are copies of config files that belong in /etc/apache2


Restart the apache service:

    sudo systemctl restart apache2

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

## Webserver

Install webserver deps:

    go get github.com/jinzhu/gorm
    go get github.com/lib/pq
    go get github.com/ant0ine/go-json-rest/rest

Instructions on building go from source: https://golang.org/doc/install/source

## Conditions

Tested on:

- i7 6700k (8 threads@4.2gHz, 8MB)
- 32GB DDR4
- SM951 Nvme 512GB (system drive)
- WD 500GB HDD (testing drive)

## Strange Behavior

Most of these are present only in NTFS. 

### Bad Times

Originally, we used Go's built in timer which defaults to gettimeofday on Linux. It has 1ms precision on Windows, so I switched to Window's reccomended method for high-precision timing: QueryPerformanceCounter. 

QPC drifts very badly between mutliple cores, which likely accounted for the strange slicing seen on Windows before. 

### Missing Results
Error seen under heavy load in Windows for go: 

    panic: Get http://localhost:8080/reminders: dial tcp [::1]:8080: connectex: Only one usage of each socket address (protocol/network address/port) is normally permitted.

The first time I saw these errors on Windows I dropped the times entirely, but I didn't realize how many of them there actually are. 

This is "TCP/IP Port Exhaustion," as documented [here](https://msdn.microsoft.com/en-us/library/aa560610%28v=bts.20%29.aspx?f=255&MSPPError=-2147217396). Editting the registry increases the headroom available but does not remove it. 

It is possible to reduce the time that a port stays "in use" through another registry edit, but you can't set it less than 30s, so no dice. 

Experimenting with changing the port number between tests seems to work. Try this next. 

