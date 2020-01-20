from math import gcd
from functools import reduce
from warnings import warn
import argparse
from recip import RecipParser

def lcm(a, b):
    return (a*b) // gcd(a, b)

def run():
    parser = argparse.ArgumentParser()
    parser.add_argument('mode',
            choices=['violations', 'meter', 'timebase'])
    parser.add_argument('recip_file')
    parser.add_argument('--timebase', type=int, default=1,
            help='represent durations on timebase, '
            'incompatible with timebase mode')
    args = parser.parse_args()
    # Read the data
    with open(args.recip_file) as f:
        recip_lines = [l.strip() for l in f]

    parser = RecipParser(timebase=args.timebase)

    tolerance = 10e-9 # floating-point error tolerance
    report = {}
    note_denominators = {1} # set of note denominators
    if args.mode == 'meter':
        print('name,meter_segment,start_time,numerator,denominator')
    for i, line in enumerate(recip_lines):
        name, *tokens = line.split(' ')
        violations = []
        period, last_barline, last_meter_time, last_meter = None, None, None, None
        meter_segment, bar_position, absolute_time = -1, 0, 0
        #if name != 'NLB122808_01': continue
        for parsed in parser.parse(tokens):
            #print(parsed)
            token_type = parsed['type']
            if token_type == METER:
                if args.mode == 'meter':
                    # Deal with a bunch of stupid edge case
                    meter = (parsed['numerator'], parsed['denominator'])
                    if last_meter_time != absolute_time and meter != last_meter:
                        meter_segment += 1
                    # Only update when the meter has changed
                    if meter != last_meter:
                        print('{},{},{},{},{}'.format(name, meter_segment, absolute_time, meter[0], meter[1]))
                    last_meter_time = absolute_time
                    last_meter = meter
                period = parser.meter_period(parsed)
            if period is not None:
                if token_type in DURATION_TYPES:
                    dt = parser.duration(parsed)
                    bar_position += dt
                    absolute_time += dt
                    #print(absolute_time)
                    denom = parsed['value']
                    if bar_position > period + tolerance:
                        violation = 'Duration of bar {} exceeded: {}'.format(('initial' if last_barline is None else last_barline['number']), bar_position)
                        violations.append(violation)
                    if denom % 1 != 0:
                        warn('Non-integer denominator encountered')
                    elif denom != 0:
                        note_denominators.add(int(denom))
                    #print(bar_position)
                if token_type in BARLINE_TYPES:
                    barnum = parsed['number']
                    if parsed['final']:
                        barnum = 'final'
                    if last_barline is None: 
                        if absolute_time > 0:
                            absolute_time = period # we're at the end of a pickup 
                        barnum = 'initial'
                    if barnum not in ['final', 'initial'] and bar_position + tolerance < period:
                        violation = ('Bar {} is incomplete: ' .format(barnum) +
                            'bar position ({}) not equal to period ({})'.format(bar_position, period))
                        violations.append(violation)
                    bar_position = 0
                    last_barline = parsed
                #print(absolute_time)
        if len(violations) > 0:
            report[name, i+1] = violations

    if args.mode == 'timebase':
        print(reduce(lcm, note_denominators))
    if args.mode == 'violations':
        print('name')
        for key in report.keys():
            print(key[0])
    #    print('Number of violations: {}'.format(len(report)))
    #    print('Files with violations: {}'.format(', '.join(map(lambda x: x[0], report.keys()))))
    #    print('Violations per file:\n{}'.format(
    #            '\n'.join('{}:\n{}'.format(key, '\n'.join('\t{}'.format(v) for v in report[key])) for key in report.keys())))

if __name__ == '__main__':
    report = run()
