'''generate problem clusters.

loop through recent tests on each board, use the `boildown` functions to
flatten the tests, and treat the flattened tests as vectors to compute the
(euclidean) distance between boards. clusters of boards indicate a common
feature in the tests, possibly indicating a common problem.

each test forms a high-dimensional space where boards can be clustered. how to
extend this to a larger space including all the tests, as well as other
features such as working channel arrays, will take some thinking.
'''

import math
import numpy as np
import couchdb
import boildown
import dbs

# development db
db = dbs.dev

tests = ['disc_check'] #['cald_test', 'cgt_test', 'chinj_scan', 'cmos_m_gtvalid', 'crate_cbal', 'disc_check']

boards = {}
for board_row in db.view('debugdb/boards'):
    id = board_row.key

    if id.startswith('d'):
        view = 'debugdb/tests_by_db'
    else:
        continue

    if int(id, 16) > int('d100', 16):
        break

    print id,
    boards[id] = {}
    seen = []
    for test_row in db.view(view, startkey=[id], endkey=[id,{}], include_docs=True):
        name = test_row.value['type']
        if name not in tests or name in seen:
            continue
        boards[id][name] = getattr(boildown, name)(test_row.doc, id)
        seen.append(name)
    print

boards = sorted(boards.iteritems())

distances = np.zeros((len(boards), len(boards)), dtype=np.float32)

def distance(a, b):
    if a == b:
        return 0
    s2 = 0.0
    for k, v in a.items():
        if k in b:
            if hasattr(a[k], '__iter__'):
                for i in range(min(len(a[k]), len(a[k]))):
                    s2 += (b[k][i] - a[k][i])**2
            else:
                s2 += (b[k] - a[k])**2
        else:
            print 'skip missing key', k

    d = math.sqrt(s2)
    return d

a = {}

print 'clustering'
c = [0.0, 1e6]

delta = 100
rmsmax = 100

while delta > 5:
    l = [[] for i in range(len(c))]
    d = [[] for i in range(len(c))]
    print '== ITERATION delta %i ==' % delta
    for id, b in boards:
        if 'disc_check' not in b: continue
        s2 = 0.0
        for k, v in b['disc_check'].iteritems():
            s2 += v**2
        s = math.sqrt(s2)
        ci = c.index(min(c,key=lambda x:abs(x-s)))

        if abs(s - math.sqrt(sum([x**2 for x in d[ci]]))) > rmsmax:
            #print 'adding new cluster at', s
            c.append(s)
            l.append([id])
            d.append([s])
        else:
            l[ci].append(id)
            d[ci].append(s)

    cnew = []
    i = 0
    while i<len(l):
        if len(d[i]) == 0:
            #print 'removing empty cluster at', c[i]
            l.pop(i)
            d.pop(i)
            c.pop(i)
            continue

        ave = sum(d[i])/len(d[i])
        cnew.append(ave)
        print ave, l[i]
        i += 1

    #print c, cnew
    delta = max([abs(c[i]-cnew[i]) for i in range(len(l))])
    #print delta
    c = cnew

import sys
sys.exit(0)

for i, (_i, u) in enumerate(boards):
    for j, (_j, v) in enumerate(boards):
        if j >= i:
            continue
        for k in u:
            if k not in v:
                continue
            a[(_i, _j)] = distance(u[k], v[k])

print 'disc_check'

c = [0.0, 500.0, 100000.0]
b = sorted(a.iteritems(), key=lambda x: a[x[0]])

