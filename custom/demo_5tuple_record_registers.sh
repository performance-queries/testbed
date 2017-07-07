#!/bin/bash

while [ 4 -gt 1 ]
do
    ./record_register.sh 1024 regK_result_f0
    ./record_register.sh 1024 regK_result_f1
    ./record_register.sh 1024 regK_result_f2
    ./record_register.sh 1024 regK_result_f3
    ./record_register.sh 1024 regK_result_f4
    ./record_register.sh 1024 regK_result_f5
    ./record_register.sh 1024 regV_result_total_time
    ./record_register.sh 1024 regV_result_total_size
    ./record_register.sh 1024 regV_result_num_bursts
    python demo_interpret_register_results.py > demo-web/interpreted_results.html
sleep 5
done
