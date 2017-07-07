#!/bin/bash

size=$1
sizem1=$((size-1))

cmdfile="read_register_CLI_cmds.txt"
rm -f $cmdfile
for i in `seq 1 $sizem1`
do
    echo "register_read $2 $i" >> $cmdfile
done

mkdir -p results

cat $cmdfile | ~/behavioral-model/targets/simple_switch/sswitch_CLI > results/$2
