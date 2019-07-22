import argparse, sys

def read_n(n):
    i = 0
    lines = []
    while i < n:
        try:
            line = next(sys.stdin)
        except StopIteration:
            break
        lines.append(line)
        i += 1
    return i, lines

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description=
            'Split a csv file into files of a given number of rows')
    parser.add_argument('rows', type=int)
    parser.add_argument('output_name')
    args = parser.parse_args()

    line = next(sys.stdin) 
    header = line
    fcount = 0
    while True:
        ofile = '{}-{}.csv'.format(args.output_name, fcount)
        read, lines = read_n(args.rows)
        if read == 0:
            break
        with open(ofile, 'w') as f:
            f.write(header)
            for line in lines:
                f.write(line)
        fcount += 1
