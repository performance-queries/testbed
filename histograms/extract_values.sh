#!/bin/bash

rm results/*
./record_register.sh 100000 regK_R1_f0
./record_register.sh 100000 regK_R1_f1
./record_register.sh 100000 regK_R1_f2
./record_register.sh 100000 regK_R1_f3
./record_register.sh 100000 regK_R1_f4
./record_register.sh 100000 regK_R1_f5
./record_register.sh 100000 regV_R1_f0
./record_register.sh 100000 regV_R1_f1
./record_register.sh 100000 regK_result_f0
./record_register.sh 100000 regV_result_f0
