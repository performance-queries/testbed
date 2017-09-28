# This script is meant specifically to order the register values obtained for the
# per-packet queueing latency results. Results should be structured as as a sequence of:
#    queue_length_register[idx] = 5
#    queue_time_register[idx] = 1001232103
# The resulting pairs of (ts, queue depth) are printed to stdout in increasing order of ts.
import os
import sys

if len(sys.argv) < 2:
    print 'Requires register dir'
    sys.exit(1)

def parse_file(name):
    f = open(name)
    j = 0
    nxt = []
    prev_time = 0
    for line in f.read().splitlines():
        parts = line.split("=")
        if len(parts) == 1:
            continue
        num = parts[1].strip()
        if j % 2 == 0:
            nxt = [int(num)]
        else:
            nxt.append(int(num))
            if prev_time == 0 or (prev_time > 0 and prev_time < int(num)):
                print '%d\t%d' % (nxt[0], nxt[1])
                prev_time = nxt[1]
        j = j+1

i = 0
while os.path.isfile("%s/%d.txt" % (sys.argv[1], i)):
    parse_file("%s/%d.txt" % (sys.argv[1], i))
    i = i+1

