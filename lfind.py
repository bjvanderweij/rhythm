import argparse, sys

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description=
            'Print lines in reference file corresponding the the numbers in input files')
    parser.add_argument('input_files', nargs='*', default=None)
    parser.add_argument('reference_file')
    args = parser.parse_args()

    line_numbers = []
    if len(args.input_files) > 0:
        for f in args.input_files:
            line_numbers += [int(line) for line in open(f)]
    else:
        line_numbers = [int(line) for line in sys.stdin]

    lines = [line.strip() for i, line in enumerate(open(args.reference_file)) if i in line_numbers]

    print('\n'.join(lines))


