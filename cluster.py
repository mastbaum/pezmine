import pickle
from board import Board, FixedBoard
import dbs

db = dbs.prod

def get_fixed_boards():
    with open('solutions.pickle','r') as f:
        solutions = pickle.load(f)
    with open('old_tests.pickle','r') as f:
        old_tests = pickle.load(f)

    fixed_boards = []
    for id in solutions:
        if not id in old_tests:
            continue

        print id, len(old_tests[id])
        channels = db[id]['channels'] if 'channels' in db[id] else None

        fixed_boards.append(FixedBoard(id, old_tests[id], solutions[id], channels))

    return fixed_boards

if __name__ == '__main__':
    fixed = get_fixed_boards()

    print fixed

