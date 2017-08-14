#!/bin/bash

if [ -z $1 ]
then
    echo "Requires JSON file (compiled query) to run"
    exit 1
fi

echo "source demo_mininet_workload.mn" | sudo python marple_twoswitch.py --json $1
