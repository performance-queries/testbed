#!/bin/bash

if [ -z $1 ]
then
    echo "Usage: thrift-port size reg_name [second reg_name]"
    exit 1
fi


size=$2
sizem1=$((size-1))

cmdfile="read_register_CLI_cmds_$1.txt"
rm -r $cmdfile
for i in `seq 1 $sizem1`
do
    echo "register_read $3 $i" >> $cmdfile
    if [ -n $4 ]; then
        echo "register_read $4 $i" >> $cmdfile
    fi
done

j=0
init_regen_plot_counter=1
snapshot_time_sec=2 # how frequently to read registers from switch
max_snaphots=1000
# Plots are re-generated every init_regen_plot_counter*snapshot_time_sec seconds.
regen_plot_counter=$init_regen_plot_counter
reg_dir=register_values_$1
rm -rf $reg_dir
mkdir $reg_dir
while [ $j -ne 1000 ]
do
    outFile="$reg_dir/${j}.txt"
    cat $cmdfile | ~/behavioral-model/targets/simple_switch/sswitch_CLI --thrift-port $1 > $outFile
    echo "Recorded $j snapshots"
    j=$((j+1))
    # Figure out if full time series should be reparsed and updated
	python parse_all_register_values.py $reg_dir > parsed_all_registers_$1.txt
	echo "Plotting all registers snapshot"
	gnuplot -e "infile='parsed_all_registers_$1.txt'; outfile='data/qlens_series_full_$1.png'" plot_qlens.gplt
    sleep $snapshot_time_sec
done
