import argparse
from utils import grid_to_iois, repeat_ioi_pattern
from itertools import product

def all_rhythms(grid_length):

    return product([0,1], repeat=grid_length)

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('N', type=int, help='number of patterns to generate')
    parser.add_argument('--iois', action='store_true', help='output iois instead of grids')
    parser.add_argument('--repetitions', type=int, default=1, help='number of times to repeat each rhythm')
    parser.add_argument('--phase', type=int, help='default phase')
    args = parser.parse_args()

    if args.phase is None:
        rhythms = all_rhythms(args.N)
        # Skip first rhythm consisting of all zeros
        next(rhythms)
    else:
        def add_first_onset(rhythm):
            return tuple(0 for _ in range(args.phase)) + (1, ) + rhythm
        rhythms = map(add_first_onset, all_rhythms(args.N - 1 - args.phase))

    if args.iois:
        rhythms = map(grid_to_iois, rhythms)
    
    def print_rhythm(rhythm):
        if args.iois: 
            offset, iois = rhythm
            iois = repeat_ioi_pattern(offset, iois, args.repetitions)
            print('%s %s' % (offset, ' '.join(map(str, iois))))
        else:
            print(' '.join(map(str, args.repetitions * rhythm)))

    list(map(print_rhythm, rhythms))

