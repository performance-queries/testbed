#! /bin/bash
# Clone mininet
sudo apt-get install git vim linux-generic-lts-vivid
# reboot here
git clone git://github.com/mininet/mininet
git checkout -b 2.2.1 2.2.1
cd ..
mininet/util/install.sh -a
