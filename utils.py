from functools import reduce
import numpy as np

def grid_to_onsets(grid):

    return tuple([i for i, onset in enumerate(grid) if onset])

def grid_to_iois(grid):

    onsets = grid_to_onsets(grid)
    onsets += (len(grid),)
    
    return onsets[0], tuple([b - a for a, b in zip(onsets, onsets[1:])])

def iois_to_onsets(offset, iois):

    return tuple(np.cumsum((offset, ) + iois))

def repeat_ioi_pattern(offset, iois, times):

    merge = lambda a, b: a[:-1] + (a[-1] + offset,) + b
    return reduce(merge, times * (iois,))

# TESTS

grid = (0, 0, 1, 0, 1, 1, 0, 0, 1, 0)
assert grid_to_onsets(grid) == (2, 4, 5, 8)
assert grid_to_iois(grid) == (2, (2, 1, 3, 2))

