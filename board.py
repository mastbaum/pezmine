'''Board class

A collection of channel status, test ids, and computed feature vectors.
'''

import boildown
import dbs

db = dbs.prod

class Board:
    '''A board
    
    :param id: The board ID, e.g. d00d
    :param tests: *(optional)* List of test document IDs for use in clustering

    If no tests are provided, the most recent test of each type (where
    available) are used.
    '''
    def __init__(self, id, tests=None):
        if id[0] not in ['f', 'd']:
            raise Exception('Bad board id %s' % id)

        self.id = id
        self.channels = self.load_channel_status()
        self.vectors = self.load_tests(tests)

    def load_channel_status(self):
        '''Load the current channel status array from the db if possible.'''
        channels = db[self.id].get('channels', [])
        return [x['good'] for x in channels]

    def load_tests(self, tests=None):
        '''Load tests from the db and boil them down to feature vectors. If no
        test IDs are provided, use the most recent of each type available.
        '''
        # if a list of tests isn't provided, the the most recent of each
        if tests is None:
            if self.id.startswith('f'):
                view = 'debugdb/tests_by_fec'
            if self.id.startswith('d'):
                view = 'debugdb/tests_by_db'

            tests = {}
            for row in db.view(view, startkey=[self.id], endkey=[self.id, {}]):
                name = row.value['type']
                if not name in tests and not name == 'final_test':
                    tests[name] = row.id

            tests = tests.values()

        self.tests = tests
        t = {}
        for id in tests:
            doc = db[id]
            try:
                t[doc['type']] = getattr(boildown, doc['type'])(doc, self.id)
            except AttributeError:
                print 'Unable to boil down', doc['type']

        return t

    def __repr__(self):
        return '<%s %s (%i tests, %i channels)>' % (self.__class__.__name__, self.id, len(self.tests), len(self.channels))

class FixedBoard(Board):
    '''A board that has been debugged
    
    :param id: The board ID, e.g. d00d
    :param tests: List of test document IDs for use in clustering
    :param solution: A string describing the solution to the board's problem

    Tests must be provided, because there's no (good) way to figure out which
    particular old, bad tests exemplify the problem.

    ``fixed_boards.py`` provides an interface for building the test and
    solution lists.
    '''
    def __init__(self, id, tests, solution):
        Board.__init__(self, id, tests)
        self.solution = solution

