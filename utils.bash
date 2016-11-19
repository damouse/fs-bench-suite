#!/bin/bash

# Ext4 to zfs
zfs() {
  echo 'hi'
  rm -rf /media/damouse/fsb

  systemctl stop postgresql
  mv /var/lib/postgresql.bak /var/lib/postgresql
  cp -aRv /var/lib/postgresql /fsb
  ln -s /fsb/postgresql /var/lib/postgresql
  systemctl start postgresql
}

# ZFS to ext4
ext() {
  fuser -km /fsb
  zpool destroy fsb

  mkfs.ext4 /def/sda
  mkdir /fsb
  mount /dev/sda /fsb
  mkdir /fsb/images
  mkdir /fsb/scratch

  chown -R damouse:damouse /fsb

  systemctl stop postgresql
  cp -aRv /var/lib/postgresql /fsb
  mv /var/lib/postgresql /var/lib/postgresql.bak
  ln -s /fsb/postgresql /var/lib/postgresql
  systemctl start postgresql
}

reset() {
  systemctl stop postgresql
  rm /var/lib/postgresql
  mv /var/lib/postgresql.bak /var/lib/postgresql
  systemctl start postgresql
}

case "$1" in
    "ext") ext;;
    "zfs") zfs;;
    "reset") reset;;
    *) echo "Unknown input $1"
   ;;
esac