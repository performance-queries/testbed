#!/bin/bash

size=$1
sizem1=$((size-1))

cmdfile="read_register_CLI_cmds.txt"
rm -r $cmdfile
for i in `seq 1 $sizem1`
do
    echo "register_read $2 $i" >> $cmdfile
    if [ -n $3 ]; then
        echo "register_read $3 $i" >> $cmdfile
    fi
done

j=0
rm -rf register_values
mkdir register_values
while [ $j -ge 0 ]
do
    outFile="register_values/${j}.txt"
    cat $cmdfile | ~/behavioral-model/targets/simple_switch/sswitch_CLI > $outFile
    echo "Recorded $j snapshots"
    j=$((j+1))
    sleep 2
done
