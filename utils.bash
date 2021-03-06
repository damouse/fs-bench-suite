#!/bin/bash

# Call with: sudo bash utils.bash [command]

# Ext4 to zfs
zfs() {
  fuser -km /fsb
  reset
  zpool create fsb sda -f 

  mkdir /fsb/images
  mkdir /fsb/scratch
  chown -R damouse:damouse /fsb

  # systemctl stop postgresql
  # cp -aRv /var/lib/postgresql /fsb
  # mv /var/lib/postgresql /var/lib/postgresql.bak
  # ln -s /fsb/postgresql /var/lib/postgresql
  # chown postgres /var/lib/postgresql
  # systemctl start postgresql
  # systemctl restart apache2
}

# ZFS to ext4
ext() {
  fuser -km /fsb
  zpool destroy fsb
  reset

  mkfs.ext4 /dev/sda
  mkdir /fsb
  mount /dev/sda /fsb
  mkdir /fsb/images
  mkdir /fsb/scratch

  chown -R damouse:damouse /fsb

  systemctl stop postgresql
  cp -aRv /var/lib/postgresql /fsb
  mv /var/lib/postgresql /var/lib/postgresql.bak
  ln -s /fsb/postgresql /var/lib/postgresql
  chown postgres /var/lib/postgresql
  systemctl start postgresql
  systemctl restart apache2
}

reset() {
  systemctl stop postgresql
  rm /var/lib/postgresql
  mv /var/lib/postgresql.bak /var/lib/postgresql
  systemctl start postgresql

  rm -rf /fsb
  umount /dev/sda
}

case "$1" in
    "ext") ext;;
    "zfs") zfs;;
    "reset") reset;;
    *) echo "Unknown input $1"
   ;;
esac