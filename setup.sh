#! /bin/bash
sudo apt-get install git vim linux-generic-lts-vivid default-jdk default-jre

# reboot here for the new kernel to take effect

# edit /etc/hosts to include the hostname of the EC2 instance.
# Spark doesn't work otherwise; mininet whines

# Mininet installation
git clone git://github.com/mininet/mininet
git checkout -b 2.2.1 2.2.1
cd ..
mininet/util/install.sh -a

# Spark installation
wget http://d3kbcqa49mib13.cloudfront.net/spark-2.1.0-bin-hadoop2.7.tgz
tar xvzf spark-2.1.0-bin-hadoop2.7.tgz 
cd spark-2.1.0-bin-hadoop2.7/
./bin/run-example --master local[2] streaming.NetworkWordCount localhost 9999

# Apache installation
sudo apt-get install apache2

# Rust installation
curl https://sh.rustup.rs -sSf | sh
