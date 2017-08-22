import os
import sys
import re

if len(sys.argv) < 2:
    print 'Requires a file with raw latencies'
    sys.exit(1)

#Expects files to have lines of the form:
# RPC %d completion time: %d ms
# All other lines will be ignored
f = open(sys.argv[1])
regx = re.compile(r"RPC (\d+) completion time: (\d+) ms")

for line in f.read().splitlines():
    match = regx.match(line)
    if match:
        start_ms = float(match.group(1))
        latency = int(match.group(2))
        print '%d %d' % (start_ms / 1000, latency)
