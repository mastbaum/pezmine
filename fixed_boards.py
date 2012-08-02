'''attach solution labels to fixed boards.

boards which have been fixed form the training set. when these boards are
clustered based on old tests, which should contain problem features, we must
know how to solve the problem the cluster the represents.

this script loops through fixed boards (boards which hwave tags, but are now
gold), displays the set of tags, and prompts for a summary of the solution.
the summary labels the cluster, and may be used to troubleshoot the still-bad
boards.
'''

import sys
import pickle
import couchdb
import dbs

def label_boards(db):
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
    return solutions

if __name__ == '__main__':
    # read from production
    db = dbs.prod

    if len(sys.argv) > 1:
        with open(sys.argv[1],'r') as f:
            solutions = pickle.load(f)
    else:
        solutions = label_boards(db)

    # determine which tests to use for problem clustering
    old_tests = {}
    for board in solutions:
        if board.startswith('d'):
            view = 'debugdb/tests_by_db'
        elif board.startswith('f'):
            view = 'debugdb/tests/by/fec'
        else:
            print '''Can't get tests for board ID %s''' % board
            continue

        print '==', board, '='*32
        print '-- Tags', '-' * 32
        for r in db.view('debugdb/tags_by_board', startkey=[board], endkey=[board,{}]):
            print '* %s\t%s\t%s\t%s' % (r.value['created'], r.value['author'], r.value['status'], r.value['content'])

        print '\nSolution: %s\n' % solutions[board]

        print '-- Tests', '-' * 31
        testidx = 0
        tests = []
        for row in db.view('debugdb/tests_by_db', startkey=[board], endkey=[board,{}]):
            status = ('PASS' if row.value['pass'] else 'FAIL') if 'pass' in row.value else '????'

            print '%3i: %s %s %s %s' % (testidx, row.value['created'], status, row.value['type'], row.id)

            # add all tests in a final test as a group
            if row.value['type'] == 'final_test':
                fttests = []
                for ftrow in db.view('debugdb/final_test', startkey=[row.id], endkey=[row.id,{}]):
                    if ftrow.key[1] == 1:
                        print '\t\t\t\t   * %s %s %s' % ('PASS' if ftrow.value['pass'] else 'FAIL', ftrow.value['type'], ftrow.id)
                        fttests.append(ftrow.id)
                tests.append(fttests)

            else:
                tests.append(row.id)

            testidx += 1

        if len(tests) == 0:
            print 'No tests!'
            print
            continue

        # prevent super-annoying accidental enter-pressing
        while True:
            test_choices = map(int, raw_input('Enter indices (-1 to drop): ').split())
            if len(test_choices) > 0:
                break

        # skip this board
        if test_choices[0] == -1:
            print
            continue

        for choice in test_choices:
            if hasattr(tests[choice], '__iter__'):
                for i in tests[choice]:
                    old_tests.setdefault(board, []).append(i)
            else:
                old_tests.setdefault(board, []).append(choice)

        print '** selected tests:', old_tests.get('board', [])

        #if test_choices == -1:
        #    continue
        #old_tests[board] = test_sets[test_choice]
        print

    print old_tests

    with open('old_tests.pickle', 'w') as f:
        pickle.dump(old_tests, f)

    #with open('solutions.pickle', 'w') as f:
    #    pickle.dump(solutions, f)

