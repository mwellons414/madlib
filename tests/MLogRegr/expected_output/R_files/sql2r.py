import re
import sys

def convert(sqlfile, csvfile):
    patten = re.compile('([0-9]+)#{(.*?)}#([0-9]+)', re.DOTALL)
    w = open(csvfile, 'w')
    head = True
    for line in open(sqlfile).readlines():
        obj = patten.match(line)
        if obj:
            id = obj.group(1)
            x = obj.group(2)
            y = obj.group(3)
            if head:
                dim = len(x.split(','))
                w.write(', '.join(['x%d' % (i) for i in range(dim)]))
                w.write(', y\n')
                head = False
            dim = len(x.split(','))
            if dim <> 1151:
                print '*******', dim
            w.write('%s, %s\n' % (x, y))
    w.close()
convert(sys.argv[1], sys.argv[2])
