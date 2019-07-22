import argparse, numpy as np, random
from utils import iois_to_grid, repeat_ioi_pattern
from itertools import product

def input_space_phase_model(periods, n_events):
    """Generate all rhythms of <n_events> that are probabilistically 
    distinguishable by the phase model.
    """
    assert all(p > 0 for p in periods)
    assert max(periods) > 0
    lcm = np.lcm.reduce(periods)
    params = range(1, lcm+1)
    return product(params, repeat=n_events)

def sample(periods, n_events):
    """Sample with replacement."""
    assert all(p > 0 for p in periods)
    assert max(periods) > 0
    lcm = np.lcm.reduce(periods)
    return [1 + int(random.random() * lcm) for _ in range(n_events)]

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('periods', nargs='+', type=int, help='periodicities')
    parser.add_argument('--sample', type=int, help='number of rhythms to sample (with replacement)')
    parser.add_argument('--length', default=1, type=int, help='number of events')
    parser.add_argument('--iois', action='store_true', help='output iois instead of grids')
    parser.add_argument('--csv', action='store_true', help='output csv')
    args = parser.parse_args()

    if args.sample is None:
        rhythms = input_space_phase_model(args.periods, args.length)
    else:
        rhythms = [sample(args.periods, args.length) for _ in range(args.sample)]

    def format(rhythm):
        if not args.iois: 
            return iois_to_grid(0, rhythm)
        return rhythm
    
    def print_rhythm(uid, rhythm):
        if args.csv:
            for i, e in enumerate(rhythm):
                print('{},{},{}'.format(uid, i, e)) 
        else:
            print(' '.join(map(str, rhythm)))

    if args.csv:
        print('sequence-uid,event,{}'.format('bioi' if args.iois else 'onset'))

    for uid, rhythm in enumerate(map(format, rhythms)):
        print_rhythm(uid, rhythm)

