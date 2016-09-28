import argparse, sys
from utils import grid_to_iois, iois_to_grid

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description=
            'Print a vector of line numbers containing each line of reference file that occurs in input files')
    parser.add_argument('input_files', nargs='*', default=None)
    parser.add_argument('factor', type=int)
    parser.add_argument('-i', '--input-format', default='grid', help='format of the input rhythms')
    parser.add_argument('-o', '--output-format', default='grid', help='format of the output rhythms')
    args = parser.parse_args()

    input_lines = []

    if len(args.input_files) > 0:
        for f in args.input_files:
            input_lines += [line for line in open(f)]
    else:
        input_lines = [line for line in sys.stdin]

    def process_input(line):

        if args.input_format == 'grid':
            grid = [int(p) for p in line.split(' ')]
            return grid_to_iois(grid)
        elif args.input_format == 'ioi':
            offset, *iois = (int(p) for p in line.split(' '))
            return offset, tuple(iois)
        else:
            print('unrecognised input format')

    def scale_rhythm(rhythm):

        offset, iois = rhythm

        return offset * args.factor, tuple(map(lambda ioi: args.factor * ioi, iois))

    def print_output(rhythm):
        
        offset, iois = rhythm
        if args.output_format == 'grid':
            print(' '.join(map(str, iois_to_grid(offset, iois))))
        elif args.output_format == 'ioi':
            print(' '.join(map(str, (offset, ) + iois)))
        else:
            print('unrecognised output format')

    rhythms = map(process_input, input_lines)
    scaled_rhythms = map(scale_rhythm, rhythms)

    for rhythm in scaled_rhythms:
        print_output(rhythm)
