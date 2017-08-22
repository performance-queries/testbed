#!/bin/bash

j=0
init_regen_plot_counter=1
snapshot_time_sec=2 # how frequently to read registers from switch
max_snaphots=1000
while [ $j -ne 1000 ]
do
    outFile="live_latency.txt"
    j=$((j+1))
    # Plot latest file
    python parse_latency.py $outFile > parsed_latencies.txt
    echo "Plotting latest snapshot"
    gnuplot -e "infile='parsed_latencies.txt';outfile='data/latency.png'" plot_latency.gplt
    # Figure out if full time series should be reparsed and updated
    sleep $snapshot_time_sec
done
