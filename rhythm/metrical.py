from itertools import product, chain
from functools import reduce
from utils import grid_to_iois
import argparse

def rest(branch):
    (_, rightmost_onset_level), _ = branch
    return rightmost_onset_level is None

def rest_level(branch):
    (rest_level, _), _ = branch
    return rest_level

def onset(branch):
    (rest_level, rightmost_onset_level), _ = branch
    return rest_level is None and rightmost_onset_level is not None

def onset_level(branch):
    (_, rightmost_onset_level), _ = branch
    return rightmost_onset_level

def pattern(branch):
    (_, _), pattern = branch
    return pattern

def identity(branch):
    return branch == ()

def make_branch(rest_level, onset_level, pattern):
    return ((rest_level, onset_level), pattern)

def make_onset_leaf(level):
    return make_branch(None, level, (1,))

def make_rest_leaf(level):
    return make_branch(level, None, (0,))

def can_merge(branch_a, branch_b):

    # Merge if branch a is a rest (regardless of whether branch b is a rest)
    if rest(branch_a):
        # If branch a is the beginning of the bar, it can't start with a rest
        if rest_level(branch_a) == 0:
            return False
        return True
    # Merge if branch b begins with an onset
    if onset(branch_b):
        return True
    # If only branch b is a rest
    if rest(branch_b):
        # Merge only if the rest level is lower than the onset level of branch a
        if onset_level(branch_a) > rest_level(branch_b):
            return True
        return False
    # If branch b doesn't begin with an onset and is not a rest
    # Merge if the rest_level of branch b is lower than the onset level of a
    if onset_level(branch_a) > rest_level(branch_b):
        return True

    return False

def syncopation(branch_a, branch_b):

    if identity(branch_a) or identity(branch_b): return 0
    if rest(branch_a):
        if rest_level(branch_a) == 0:
            return 1
        return 0
    if onset(branch_b):
        return 0
    if rest(branch_b):
        if onset_level(branch_a) > rest_level(branch_b):
            return 0
        return 1
    if onset_level(branch_a) > rest_level(branch_b):
        return 0

    return 1 + rest_level(branch_b) - onset_level(branch_a)


def merge(branch_a, branch_b):

    if identity(branch_a): return branch_b
    if identity(branch_b): return branch_a

    pat = pattern(branch_a) + pattern(branch_b)
    
    # The rest level becomes the rest level of branch a
    rest_lvl = rest_level(branch_a)
    # If B is a rest (it doesn't have a rightmost level)
    # and A is not a rest
    if not rest(branch_a) and rest(branch_b):
        # The level of the rightmost onset become that of branch a
        onset_lvl = onset_level(branch_a)
    else:
        # All other cases
        # Rightmost onset level of branch b
        onset_lvl = onset_level(branch_b)

    return make_branch(rest_lvl, onset_lvl, pat)

def regular_passages(divisions, tree_level=0, node_level=0, max_syncopation=0):
    # If we've reached the deepest level, we're done
    if len(divisions) == 0: return [
            (0, make_onset_leaf(node_level)),
            (0, make_rest_leaf(node_level))
        ]

    division, *rest = divisions
    right_branches = [(0, ())]

    # Generate all possible concatenations of these patterns
    for i in range(division, 0, -1):

        left_branches = regular_passages(rest, tree_level=tree_level-1, node_level=node_level if i == 1 else tree_level-1, max_syncopation=max_syncopation)
        new_right_branches = []
        for s_a, branch_a in left_branches:
            for s_b, branch_b in right_branches:
                s = syncopation(branch_a, branch_b) + s_a + s_b
                if s <= max_syncopation:
                    branch = merge(branch_a, branch_b)
                    # At the top level, don't include housekeeping variables
                    if tree_level == 0 and i == 1:
                        new_right_branches.append(pattern(branch))
                    else:
                        new_right_branches.append((s, branch))

        right_branches = new_right_branches

    return right_branches

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('metre', nargs='+', type=int)
    parser.add_argument('--iois', action='store_true', help='output iois instead of grids')
    parser.add_argument('--syncopation', type=int, default=0, help='maximum allowed syncopation')
    args = parser.parse_args()
    rhythms = regular_passages(args.metre, max_syncopation=args.syncopation)

    if args.iois:
        rhythms = map(grid_to_iois, rhythms)
    
    def print_rhythm(rhythm):
        if args.iois: 
            offset, rhythm = rhythm
            print('%s %s' % (offset, ' '.join(map(str, rhythm))))
        else:
            print(' '.join(map(str, rhythm)))

    list(map(print_rhythm, rhythms))
