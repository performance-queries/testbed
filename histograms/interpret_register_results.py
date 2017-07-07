# This script is intended to be run on the results of a single query.
# The script assumes that you have downloaded the register contents (using 'record_register.sh')
# Given a set of files corresponding to each donwloaded register, this script
# groups the values by the hash id and presents the Keys and Values for each grouped-by target.

import os
import numpy as np
import matplotlib
import glob
matplotlib.use('Agg')
import matplotlib.pyplot as plt

min_size_allowed = 1

# Parses a 32-bit integer representation of an IP address into a string.
def parse_ip(asNum):
    return '%d.%d.%d.%d' % (asNum >> 24, (asNum >> 16) & 0xff, (asNum >> 8) & 0xff, asNum & 0xff)

ax = plt.gca()
def parse_results(target_thresh):
    results = {}
    registers = []
    target_dir = "results_%d" % target_thresh
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
    
    x = []
    y = []
    for k, v in results.iteritems():
        print 'Index %d:' % k
        for r in registers:
            val = 0
            if r in v:
               val = v[r]
            if r.startswith("regK_result"):
                x.append(int(val))
            elif r.startswith("regV_result"):
                y.append(int(val))
            if val > (1 << 24):
                print '\t%s = %d \t#As IP: %s' % (r, val, parse_ip(val))
            else:
                print '\t%s = %d' % (r, val) 
        print '===============' 
    
    # Plot the CDF of flowlet sizes.     
    arr = np.array([x, y], np.float32)
    arr = arr[:, arr[0,:].argsort()]
    # Filter out values of 0 and keys of 0.
    arr = arr[:, np.prod(arr, axis=0) > 0]
    while arr[0][0] < min_size_allowed:
        arr = arr[:,1:]
    print arr
    x = arr[0]
    y = arr[1]
    y = np.cumsum(y)
    y /= y[-1]
    label = "delta = %d ms" % (target_thresh / 1000)
    ax.plot(x,y,linewidth=2.5, label=label)
    print 'plotting %s' % target_dir

ax.set_xlabel("Flowlet size (packets)", fontsize=28)
ax.set_ylabel("CDF", fontsize=28)
plt.xscale('log')
plt.gcf().set_size_inches(11,4)
ax.set_xlim([1,10000])
for t in [10000,20000, 50000, 100000, 500000]:
    parse_results(t)
ax.tick_params(axis='both', which='major', labelsize=16)
plt.legend(fontsize=20, loc='upper left', bbox_to_anchor=(1,1))
plt.subplots_adjust(top=0.95, left=0.1, bottom=0.2, right=0.7)
plt.savefig('cdf.pdf')
