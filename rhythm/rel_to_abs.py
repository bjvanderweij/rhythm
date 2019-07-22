#!/usr/bin/python3
import sys, argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('pitch',
        type=int,
        help='Reference pitch')

    args = parser.parse_args()

    # Read rhythm from stdin
    inp = [list(map(int, line.split(' '))) for line in sys.stdin]
    intervals = inp[0]

    pitches = [args.pitch]
    for interval in intervals:
        pitches.append(pitches[-1] + interval)

    sys.stdout.write(' '.join(map(str, pitches)) + '\n')


