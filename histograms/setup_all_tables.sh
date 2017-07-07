#!/bin/bash

echo "Setting up table 1..."
./setup_tables.sh $1 $2 9090
echo "Setting up table 2..."
./setup_tables2.sh $1 $2 9091
echo "Setting up table 3..."
./setup_tables3.sh $1 $2 9092
echo "Setting up table 4..."
./setup_tables4.sh $1 $2 9093
