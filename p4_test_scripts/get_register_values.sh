#!/bin/sh

# First argument should be register name
if [ -z $1 ]
then
    echo "Requires register name as an argument"
    exit 1
fi

f=CLI_commands.txt
rm -f $f
for i in `seq 0 1023`
do
    echo "register_read $1 $i" >> $f
done

~/p4c/behavioral-model/tools/runtime_CLI.py < CLI_commands.txt | grep -o -e "$1.*[1-9][0-9]*$"
