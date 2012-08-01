'''attach solution labels to fixed boards.

boards which have been fixed form the training set. when these boards are
clustered based on old tests, which should contain problem features, we must
know how to solve the problem the cluster the represents.

this script loops through fixed boards (boards which hwave tags, but are now
gold), displays the set of tags, and prompts for a summary of the solution.
the summary labels the cluster, and may be used to troubleshoot the still-bad
boards.
'''

import pickle
import couchdb
import dbs

# read from production
db = dbs.prod

solutions = {}

for row in db.view('debugdb/tags_with_status', reduce=True, group_level=1):
    if row.value[0] == 'gold' and row.value[1] > 1:
        print '-' * 40
        print row.key, row.value
        print 'Tags:'
        for r in db.view('debugdb/tags_by_board', startkey=[row.key], endkey=[row.key,{}]):
            print '* %s\t%s\t%s' % (r.value['author'], r.value['status'], r.value['content'])
        solution = raw_input("Summarize the solution (x to drop): ")
        if not solution == 'x':
            solutions[row.key] = solution

with open('solutions.pickle', 'w') as f:
    pickle.dump(solutions, f)

