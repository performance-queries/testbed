#!/bin/bash

cmdfile="table_commands.txt"
re='^[0-9]+$'
if ! [[ $1 =~ $re ]]
then
    echo "error: Requires an integer argument" >&2
    exit 1
fi

rm -f $cmdfile
echo "set_queue_rate 1000" > $cmdfile
for i in `seq 1 $1`
do
    im1=$((i-1))
    echo "table_add ipv4_match Set_nhop 10.0.${im1}.10/32 => 10.0.${im1}.10 $i" >> $cmdfile
    echo "table_add dmac Set_dmac 10.0.${im1}.10 => 00:04:00:00:00:$(printf %02x $im1)" >> $cmdfile
    echo "table_add smac Set_smac $i => 00:aa:bb:00:00:$(printf %02x $im1)" >> $cmdfile
done

cat $cmdfile | ~/behavioral-model/targets/simple_switch/sswitch_CLI
