# This script is intended to be run on the results of a single query.
# The script assumes that you have downloaded the register contents (using 'record_register.sh')
# Given a set of files corresponding to each donwloaded register, this script
# groups the values by the hash id and presents the Keys and Values for each grouped-by target.

import os

# Parses a 32-bit integer representation of an IP address into a string.
def parse_ip(asNum):
    return '%d.%d.%d.%d' % (asNum >> 24, (asNum >> 16) & 0xff, (asNum >> 8) & 0xff, asNum & 0xff)

results = {}
registers = []
target_dir = "results/"
files = os.listdir(target_dir)
for name in files:
    registers.append(name)
    f = open(os.path.join(target_dir, name))
    for line in f.read().splitlines():
        parts = line.split("=")
        if len(parts) == 1:
            continue
        val = int(parts[1].strip())
        if val == 0:
            continue
        lb = parts[0].find("[")
        rb = parts[0].find("]")
        ix = int(parts[0][lb+1:rb])
        if ix not in results:
            results[ix] = {}
        results[ix][name] = val

for k, v in results.iteritems():
    print 'Index %d:' % k
    for r in registers:
        val = 0
        if r in v:
           val = v[r]
        if val > (1 << 24):
            print '\t%s = %d \t#As IP: %s' % (r, val, parse_ip(val))
        else:
            print '\t%s = %d' % (r, val) 
    print '===============' 
     
