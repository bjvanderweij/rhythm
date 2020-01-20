import re
# Given recip and names file, read each line in the recip file, split by spaces extract the numbers (rests or not) and 

METER = 'meter'
NOTE = 'note'
REST = 'rest'
BAR = 'bar'

DURATION_TYPES = [NOTE, REST]
BARLINE_TYPES = [BAR]

NOTE_VALUE = r'([0-9]*\.?[0-9]+)(\.*)'
NOTE_VALUE_PROPS = {
    'value':{'index':1, 'parser':float},
    'dots':{'index':2, 'parser':lambda dots: len(dots)},
}

SPEC = {
    METER:{
        'exp':r'\*M([0-9]+)/([0-9]+)([%0-9+]*)',
        'props':{
            'numerator':1,
            'denominator':2,
            'gibberish':{'index':3, 'parser':str},
        },
    },
    NOTE:{
        'exp':r'(\[)?' + NOTE_VALUE + '(\])?',
        'props':{
            'value':{'index':2, 'parser':float},
            'dots':{'index':3, 'parser':lambda dots: len(dots)},
            'tie_open':{'index':1, 'parser':lambda tie: tie is not None},
            'tie_close':{'index':4, 'parser':lambda tie: tie is not None},
        },
    },
    REST:{
        'exp':NOTE_VALUE + r'r',
        'props':NOTE_VALUE_PROPS,
    },
    BAR:{
        'exp':r'=(=*)([0-9]+)?[a-z]?[;!:|-]*', # This ignores the difference between bar 9 and bar 9a
        'props':{
            'number':{'index':2, 'parser': lambda n: int(n) if n is not None else None},
            'final':{'index':1, 'parser':lambda s: len(s) > 0},
        },
    },
}

class ParsingError(Exception):
    pass

class RecipParser():

    def __init__(self, timebase=1):
        self.timebase = timebase

    def meter_period(self, m):
        return self.timebase * m['numerator'] / m['denominator']

    def duration(self, dur):
        denominator = 0.5 if dur['value'] == 0 else dur['value']
        duration = self.timebase /  denominator
        return duration + (duration / 2**dur['dots'] if dur['dots'] > 0 else 0)

    def _parse_properties(self, match, spec):
        r = {}
        for prop, prop_spec in spec['props'].items():
            index = prop_spec
            parser = int
            if isinstance(prop_spec, dict):
                index = prop_spec['index']
                parser = prop_spec['parser']
            r[prop] = parser(match.group(index))
        return r

    def _parse_token(self, token):
        for t, spec in SPEC.items():
            m = re.match(r'^' + spec['exp'] + r'$', token)
            if m is not None:
                result = {'type':t}
                result.update(self._parse_properties(m, spec))
                return result
        raise ParsingError(
                'Parsing error. Token: '.format(i+1, name) + 
                '"' + token + '".')

    def parse(self, tokens):
        for token in tokens:
            parsed = self._parse_token(token)
            yield parsed
