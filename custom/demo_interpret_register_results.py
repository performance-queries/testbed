# This script is intended to be run on the results of a single query.
# The script assumes that you have downloaded the register contents (using 'record_register.sh')
# Given a set of files corresponding to each donwloaded register, this script
# groups the values by the hash id and presents the Keys and Values for each grouped-by target.

import os

# Parses a 32-bit integer representation of an IP address into a string.
def parse_ip(asNum):
    return '%d.%d.%d.%d' % (asNum >> 24, (asNum >> 16) & 0xff, (asNum >> 8) & 0xff, asNum & 0xff)

results = {}
register_names = ['regK_result_f0', 
                  'regK_result_f1',
                  'regK_result_f2',
                  'regK_result_f3',
                  'regK_result_f4',
                  'regV_result_num_bursts',
                  'regV_result_total_size',
                  'regV_result_total_time',
                  'regK_result_f5'
              ]
register_prints = ['srcip',
                   'dstip',
                   'srcport',
                   'dstport',
                   'protocol',
                   'number of bursts',
                   'total size',
                   'total time',
                   'switch ID'
]
target_dir = "results/"
files = os.listdir(target_dir)
for name in register_names:
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

assert len(register_prints) == len(register_names)

print '<!DOCTYPE html>'
print '<html><body><table cellspacing=20>'
print '<tr><th>'
print '</th><th>'.join(register_prints)
print '</th></tr>'

for k, v in results.iteritems():
    # print 'Index %d:' % k,
    print '<tr>'
    for i in range(0, len(register_names)):
        r = register_names[i]
        val = 0
        print_key = register_prints[i]
        if r in v:
           val = v[r]
        if print_key == 'srcip' or print_key == 'dstip':
            print '<td>%s</td>' % parse_ip(val),
        else:
            print '<td>%d</td>' % val,
    print '</tr>'
    # print '===============' 
print '</table>'
