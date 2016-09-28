import argparse, sys

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description=
            'Print a vector of line numbers containing each line of reference file that occurs in input files')
    parser.add_argument('input_files', nargs='*', default=None)
    parser.add_argument('reference_file')
    parser.add_argument('-p', '--python', action='store_true', help='format output as python list')
    parser.add_argument('-l', '--lisp', action='store_true', help='format output as lisp list')
    args = parser.parse_args()

    input_lines = []
    if len(args.input_files) > 0:
        for f in args.input_files:
            input_lines += [line for line in open(f)]
    else:
        input_lines = [line for line in sys.stdin]

    indices = [i for i, line in enumerate(open(args.reference_file)) if line in input_lines]

    if args.python:
        print('[%s]'.join(', '.join(map(str, indices))))
    if args.lisp:
        print('(%s)'.join(' '.join(map(str, indices))))
    if not (args.python and args.lisp):
        print('\n'.join(map(str, indices)))


