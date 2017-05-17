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
init_regen_plot_counter=1
snapshot_time_sec=2 # how frequently to read registers from switch
max_snaphots=1000
# Plots are re-generated every init_regen_plot_counter*snapshot_time_sec seconds.
regen_plot_counter=$init_regen_plot_counter
rm -rf register_values
mkdir register_values
while [ $j -ne 1000 ]
do
    outFile="register_values/${j}.txt"
    cat $cmdfile | ~/behavioral-model/targets/simple_switch/sswitch_CLI > $outFile
    echo "Recorded $j snapshots"
    j=$((j+1))
    # Plot latest file
    python parse_latest_register_values.py $outFile > parsed_latest_registers.txt
    gnuplot -e "infile='parsed_latest_registers.txt';outfile='demo-web/qlens_series_latest.png'" plot_qlens.gplt
    # Figure out if full time series should be reparsed and updated
    if [ $regen_plot_counter -eq 0 ]; then
	python parse_all_register_values.py > parsed_all_registers.txt
	gnuplot -e "infile='parsed_all_registers.txt'; outfile='demo-web/qlens_series_full.png'" plot_qlens.gplt
	regen_plot_counter=$init_regen_plot_counter
    fi
    regen_plot_counter=$((regen_plot_counter-1))
    sleep $snapshot_time_sec
done
