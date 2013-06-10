import re
import sys

def convert(sqlfile, csvfile):
    patten = re.compile('[0-9.]+\\t\{[0-9.,]+\}')
    data = {}
    w = open(csvfile, 'w')
    for line in open(sqlfile).readlines():
        if patten.match(line):
            [id, vector] = line.strip().split('\t')
            data[int(id)] = vector[1:-1]
    for key in sorted(data.keys()):
        w.write(data[key])
        w.write('\n')
    w.close()

convert(sys.argv[1], sys.argv[2])
