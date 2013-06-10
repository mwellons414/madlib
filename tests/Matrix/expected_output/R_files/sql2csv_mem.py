import re
import sys

def convert(sqlfile, csvfile):
    data = ''
    for line in open(sqlfile).readlines():
        if line.startswith('{{'):
            data = line
            break

    w = open(csvfile, 'w')
    data = data.replace('},{', '\n')
    data = data.replace('{{', '')
    data = data.replace('}}', '')
    w.write(data)
    w.close()

convert(sys.argv[1], sys.argv[2])
