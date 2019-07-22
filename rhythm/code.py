import argparse, sys

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description=
            'Read each line from input files or stdin and print as list in the specified programming language')
    parser.add_argument('input_files', nargs='*')
    parser.add_argument('-l', '--language', default='python', help='output language. default is python.')
    parser.add_argument('-t', '--type', default='str', nargs=1, help='specify the data type of the input lines. default is str.')
    args = parser.parse_args()

    input_lines = []
    if len(args.input_files) > 0:
        for f in args.input_files:
            input_lines += [line.strip() for line in open(f)]
    else:
        input_lines = [line.strip() for line in sys.stdin]

    def format_list(items):
        if args.language == 'python':
            return '[%s]' % ', '.join(map(format_item, items))
        if args.language in ['lisp', 'commonlisp']:
            return '(%s)' % ' '.join(map(format_item, items))
        else:
            return 'unrecognised language'

    def format_item(line):
        if args.type in ['str', 'string', 'text']:
            return '\"%s\"' % line
        if args.type in ['int', 'integer', 'numeric', 'number', 'float']:
            return line
        if args.type in ['list']:
            return format_list(line.split(' '))
        return line

    print(format_list(input_lines))

