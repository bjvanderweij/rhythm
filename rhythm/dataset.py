import argparse, sys, numbers, re
from utils import grid_to_iois, iois_to_onsets

# Generate a lisp format dataset for IDyOM encoding each IOI pattern in stdin as a rhythm

class LispSymbol(str): pass

class LispProperty(str): pass

def to_lisp(i):

    if isinstance(i, numbers.Number):
        return '%s' % i
    elif isinstance(i, LispProperty):
        return ':%s' % i
    elif isinstance(i, LispSymbol):
        return i
    elif isinstance(i, str):
        m = re.match(r'\(.+\)', i)
        if not m:
            return '\"%s\"' % i
    elif i is None:
        return "nil"
    return i

def list_to_lisp(l):
    return '(%s)' % ' '.join(map(to_lisp, l))

def dict_to_plist(d):
    return list_to_lisp(list_to_lisp((LispProperty(k), v)) for k, v in d.items())

def scale_duration(duration, old_timebase, new_timebase):
    return int(duration * new_timebase / old_timebase) # Timebase is the inverse of duration

def scale_rhythm(offset, iois, *args):
    return scale_duration(offset, *args), [scale_duration(ioi, *args) for ioi in iois]

def make_events(offset, iois, metre, pulses, source_timebase, target_timebase):

    offset, iois = scale_rhythm(offset, iois, source_timebase, target_timebase)
    biois = [offset] + iois
    onsets = np.cumsum([offset] + iois)[:-1]
    barlength = scale_duration(reduce(int.__mul__, metre), source_timebase, target_timebase)

    return [make_event(onset, bioi, ioi, barlength, pulses) for onset, bioi, ioi in zip(onsets, biois, iois)]

def make_event(onset, bioi, ioi, barlength=None, pulses=None):

    return {
        'onset': onset, 'deltast': 0, 'bioi': bioi, 'dur': ioi,
        'cpitch': 80, 'mpitch': 40, 'accidental': 0, 'keysig': 0,
        'mode': 0, 'barlength': barlength, 'pulses': pulses, 'phrase': 0,
        'voice': 1, 'ornament': None, 'comma': None, 'articulation': None,
        'dyn': None,
    }


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('-o', '--output')
    parser.add_argument('--ioi', action='store_true', help='take iois as input')
    parser.add_argument('--description', default='', help='dataset description')
    parser.add_argument('--timebase', type=int, default=96, help='timebase to encode dataset in')
    parser.add_argument('--input-timebase', type=int, default=8, help='input timebase')
    parser.add_argument('--midc', type=int, default=60, help='input timebase')

    args = parser.parse_args()

    # Read rhythm from stdin
    rhythms = []
    for line in sys.stdin:
        if not args.ioi:
            grid = [int(p) for p in line.split(' ')]
            offset, iois = grid_to_iois(grid)
        else:
            offset, *iois = (int(p) for p in line.split(' '))
        offset, iois = scale_rhythm(offset, iois, args.input_timebase, args.timebase)
        rhythms.append((offset, tuple(iois)))

    event_sequences = [map(make_event, iois_to_onsets(offset, iois), (offset, ) + iois, iois) for offset, iois in rhythms]
    lisp_event_sequences = [list_to_lisp((str(i), ) + tuple(map(dict_to_plist, events))) for i, events in enumerate(event_sequences)]
    lisp_dataset = list_to_lisp([args.description, args.timebase, args.midc] + lisp_event_sequences)

    if args.output is not None:
        with open(args.output, 'w') as ofile:
            ofile.write(lisp_dataset)
    else:
        print(lisp_dataset)

