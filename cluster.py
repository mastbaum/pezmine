import math
import pickle

from board import Board, FixedBoard, InvalidIDError
import dbs

db = dbs.prod

def get_fixed_boards():
    '''Load fixed board data from disk.'''
    with open('solutions.pickle','r') as f:
        solutions = pickle.load(f)
    with open('old_tests.pickle','r') as f:
        old_tests = pickle.load(f)

    boards = []
    for id in solutions:
        if id in old_tests:
            print 'Fixed:', id
            boards.append(FixedBoard(id, old_tests[id], solutions[id]))

    return boards

def get_bad_boards():
    '''Load bad boards from db, where bad = debugging status | status.'''
    boards = []
    for row in db.view('debugdb/tags_with_status', group_level=1):
        if row.value[0] == 'bad' or db[row.key]['status'] == 'bad':
            print 'Bad:', row.key
            try:
                boards.append(Board(row.key))
            except InvalidIDError:
                print 'Invalid ID', row.key

    return boards

def distance_euclidean(a, b=None):
    '''compute the euclidean distance between two dicts.'''
    if a == b:
        return 0.0

    s2 = 0.0
    for k in a:
        if b is None:
            s2 += (a[k])**2
        else:
            if k in b:
                s2 += (b[k] - a[k])**2

    return math.sqrt(s2)

def cluster(test, boards, centers=[0], epsilon=5, rmsmax=2):
    delta = epsilon + 1
    iteration_count = 0
    while delta > epsilon:
        print '== Iteration %i (delta %f) ==' % (iteration_count, delta)
        ids = [[] for i in range(len(centers))]
        pos = [[] for i in range(len(centers))]

        for board in boards:
            if test not in board.vectors:
                continue

            s = distance_euclidean(board.vectors[test])
            cluster_index = centers.index(min(centers, key=lambda x: abs(x-s)))

            # put outliers into new clusters
            outlier = False
            if len(pos[cluster_index]) > 1:
                mean = sum(pos[cluster_index])/len(pos[cluster_index])
                rms = math.sqrt(1.0/len(pos[cluster_index]) * sum([x**2-mean**2 for x in pos[cluster_index]]))
                d = abs(s - mean)
                #print 'check outlier', d, rms, rmsmax
                outlier = d > rms * rmsmax

            if outlier:
                centers.append(s)
                ids.append([board.id])
                pos.append([s])
            else:
                ids[cluster_index].append(board.id)
                pos[cluster_index].append(s)

        # move centers to centroids and remove empty clusters
        new_centers = []
        i = 0
        while i < len(ids):
            if len(pos[i]) == 0:
                centers.pop(i)
                ids.pop(i)
                pos.pop(i)
                continue

            mean = sum(pos[i]) / len(pos[i])
            print mean, ids[i]
            new_centers.append(mean)
            
            i += 1

        delta = max([abs(centers[i] - new_centers[i]) for i in range(len(ids))])
        centers = new_centers

        iteration_count += 1

    print '** Converged after %i iterations (delta = %f)' % (iteration_count, delta)

if __name__ == '__main__':
    fixed = get_fixed_boards()
    print 'Loaded', len(fixed), 'fixed boards'

    #bad = get_bad_boards()
    #print 'Loaded', len(bad), 'bad boards'

    for test in ['disc_check']: #['chinj_scan', 'cmos_m_gtvalid', 'crate_cbal', 'disc_check']:
        cluster(test, fixed)


