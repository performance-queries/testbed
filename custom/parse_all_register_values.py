# This script is meant specifically to order the register values obtained for the
# per-packet queueing latency results. Results should be structured as as a sequence of:
#    queue_length_register[idx] = 5
#    queue_time_register[idx] = 1001232103
# The resulting pairs of (ts, queue depth) are printed to stdout in increasing order of ts.
import os

lines = []

def parse_file(name):
    f = open("register_values/%d.txt" % i)
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

i = 0
while os.path.isfile("register_values/%d.txt" % i):
    parse_file("register_values/%d.txt" % i)
    i = i+1

for line in lines:
    print '%d\t%d' % (line[0], line[1])
