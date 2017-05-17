# This script is meant specifically to order the register values obtained for the
# per-packet queueing latency results. Results should be structured as as a sequence of:
#    queue_length_register[idx] = 5
#    queue_time_register[idx] = 1001232103
# The resulting pairs of (ts, queue depth) are printed to stdout in increasing order of ts.
import os
import sys

lines = []

def parse_file(name):
    f = open(name)
    j = 0
    nxt = []
    for line in f.read().splitlines():
        parts = line.split("=")
        if len(parts) == 1:
            continue
        num = parts[1].strip()
        if j % 2 == 0:
            nxt = [int(num)]
        else:
            nxt.append(int(num))
            if len(lines) == 0 or (len(lines) > 0 and lines[-1][1] < int(num)):
                lines.append(nxt)
        j = j+1

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print "Cannot analyze data without at least one snapshot."
        sys.exit(1)
    else:
        parse_file(sys.argv[1])
        for line in lines:
            print '%d\t%d' % (line[0], line[1])
