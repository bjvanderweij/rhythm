import argparse
from utils import grid_to_iois, repeat_ioi_pattern
from itertools import product

def all_grids(grid_length):
    return product([0,1], repeat=grid_length)

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('length', type=int, help='number of grid points')
    parser.add_argument('--iois', action='store_true', help='output iois instead of grids')
    parser.add_argument('--repetitions', type=int, default=1, help='number of times to repeat each rhythm')
    parser.add_argument('--phase', type=int, help='default phase')
    parser.add_argument('--csv', action='store_true', help='output csv')
    args = parser.parse_args()

    if args.phase is None:
        rhythms = all_grids(args.length)
        # Skip first rhythm which does not contain any onsets
        next(rhythms)
    else:
        def add_first_onset(rhythm):
            return tuple(0 for _ in range(args.phase)) + (1, ) + rhythm
        rhythms = map(add_first_onset, all_grids(args.length - 1 - args.phase))

    if args.iois:
        rhythms = map(grid_to_iois, rhythms)

    def format(rhythm):
        offset, iois = rhythm
        uid = ''.join(map(str, (offset, ) + iois))
        if args.iois: 
            iois = repeat_ioi_pattern(offset, iois, args.repetitions)
            return uid, (offset, ) + iois
        return uid, args.repetitions * rhythm
    
    def print_rhythm(uid, rhythm):
        if args.csv:
            for i, e in enumerate(rhythm):
                print('{},{},{}'.format(uid, i, e)) 
        else:
            print(' '.join(map(str, rhythm)))

    if args.csv:
        print('sequence-uid,event,{}'.format('ioi' if args.iois else 'onset'))

    for uid, rhythm in map(format, rhythms):
        print_rhythm(uid, rhythm)

