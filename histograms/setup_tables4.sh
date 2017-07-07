#!/bin/bash

# Suppose there are S senders and R receivers.
# IP addresses 10.0.{0-(S-1)}}.10 correspond to the senders.
# Any packets routed to them are routed through the corresponding port on the switch,
# which has MAC 00:aa:bb:00:00:$i. The MAC of the host's receiving port
# is 00:04:00:00:00:$i
# All packets to other hosts are routed through switch 2 or 3 depending on the parity
# of the hosts ID.
# Switch 2 has IP 10.1.0.10 and Switch 3 has IP 10.2.0.10.

cmdfile="table_commands4.txt"
re='^[0-9]+$'
if ! [[ $1 =~ $re ]]
then
    echo "error: Requires two integer arguments" >&2
    exit 1
fi
if ! [[ $2 =~ $re ]]
then
    echo "error: Requires two integer arguments" >&2
    exit 1
fi
senders=$1
rcvrs=$2
sp1=$((senders+1))
spr=$((senders+rcvrs))
rm -f $cmdfile
echo "set_queue_rate 1000" > $cmdfile
for i in `seq 1 $senders`
do
    im1=$((i-1))
    choice=$((2 + i % 2))
    port=$((rcvrs+choice - 1))
    echo "table_add ipv4_match Set_nhop 10.0.${im1}.10/32 => 10.${choice}.0.1 $port" >> $cmdfile
done
echo "table_add dmac Set_dmac 10.2.0.1 => 00:aa:bb:00:01:01" >> $cmdfile
echo "table_add smac Set_smac $((rcvrs+1)) => 00:aa:bb:00:03:$(printf %02x $rcvrs)" >> $cmdfile
echo "table_add dmac Set_dmac 10.3.0.1 => 00:04:00:00:02:01" >> $cmdfile
echo "table_add smac Set_smac $((rcvrs+2)) => 00:aa:bb:00:03:$(printf %02x $((rcvrs+1)))" >> $cmdfile

# These are receivers and need to be routed through the two adjacent switches.
for i in `seq $sp1 $spr`
do
    im1=$((i-1))
    ims=$((i-senders))
    echo "table_add ipv4_match Set_nhop 10.0.${im1}.10/32 => 10.0.${im1}.10 $ims" >> $cmdfile
    echo "table_add dmac Set_dmac 10.0.${im1}.10 => 00:04:00:00:00:$(printf %02x $im1)" >> $cmdfile
    echo "table_add smac Set_smac $ims => 00:aa:bb:00:03:$(printf %02x $ims)" >> $cmdfile
done

if [[ -z $3 ]];
then
    echo "error: Requires third argument (thrift port)"
    exit 1
fi
cat $cmdfile | ~/behavioral-model/targets/simple_switch/sswitch_CLI --thrift-port $3
