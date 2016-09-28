#!/usr/bin/python3
import sys, argparse, subprocess, tempfile
from midiutil.MidiFile3 import MIDIFile
from utils import grid_to_iois, repeat_ioi_pattern

parser = argparse.ArgumentParser()

parser.add_argument('output_path',
    help='Path to the output file')

parser.add_argument('--ioi',
    action='store_true',
    help='Treat input as IOIs')
parser.add_argument('--bpm',
    type=int,
    default=120,
    help='Beats per minute for the midi file')
parser.add_argument('--repetitions',
    type=int,
    default=1,
    help='Repeat the rhythms a specified number of times.')
parser.add_argument('--channel',
    type=int,
    default=0,
    help='Midi channel')
parser.add_argument('--format',
    default='midi',
    choices=('mid', 'midi', 'ogg', 'wav', 'mp3'),
    help='Midi pitch')
parser.add_argument('--count-in',
    action='store_true'
)
parser.add_argument('--click-track',
    default=False,
    action='store_true'
)
parser.add_argument('--period',
    default=0,
    type=int,
)
parser.add_argument('--pulse',
    default=1,
    type=int,
)
parser.add_argument('--downbeat',
    action='store_true'
)
parser.add_argument('--click-track-phase',
    type=int,
    default=0,
)


def save_midi(offset, iois, pitches, path, click_track=False, click_track_phase=0, accent_downbeat=False, period=0, pulse=1, bpm=240, channel=0, velocity=100):
    '''
    bpm means grid-units per second in this case
    '''

    track = 0

    mf = MIDIFile(1)

    mf.addTrackName(track, 0, "Sample Track")
    mf.addTempo(track, 0, bpm)

    if click_track: 

        duration = offset + sum(iois)
        write_click_track(mf, duration, phase=click_track_phase, period=period, pulse=pulse, velocity=velocity, accent_downbeat=accent_downbeat)

    write_notes(mf, offset, iois, pitches, track=track, channel=channel, velocity=velocity)

    with open(path, 'wb') as midi_file:
        mf.writeFile(midi_file)

def write_notes(midi_file, offset, iois, pitches, track=0, channel=0, velocity=100):

    time = offset

    for duration, pitch in zip(iois, pitches):

        midi_file.addNote(track, channel, pitch, time, duration, velocity)
        time += duration

def write_click_track(midi_file, duration, phase=0, end_time=0, track=0, velocity=100, accent_downbeat=0, *, period, pulse):

    channel = 9
    cowbell = 56
    hi_woodblock = 76
    lo_woodblock = 77
    stick = 37

    for time in range(duration):
        metrical_time = time - phase
        if metrical_time % pulse == 0:
            midi_file.addNote(track, channel, lo_woodblock, time, pulse, int(0.75 * velocity))
        if metrical_time % period == 0:
            midi_file.addNote(track, channel, hi_woodblock, time, period, velocity)


if __name__ == '__main__':
    args = parser.parse_args()

    # Read rhythm from stdin
    rhythms = []
    input_lines = [line for line in sys.stdin]
    if len(input_lines) > 0:
        rhythm = input_lines[0]
        if not args.ioi:
            grid = [int(p) for p in rhythm.split(' ')]
            offset, iois = grid_to_iois(grid)
        else:
            offset, *iois = (int(p) for p in rhythm.split(' '))
        pitches = ([60 for _ in iois] if len(input_lines) == 1 
                else list(map(int, input_lines[1].split(' '))))

    iois = tuple(iois)
    iois = repeat_ioi_pattern(offset, iois, args.repetitions)
    pitches = args.repetitions * pitches

    if args.format in ('midi', 'mid'):
        mid_path = args.output_path
    else:
        (_, mid_path) = tempfile.mkstemp(suffix='.mid')

    save_midi(offset, iois, pitches, mid_path, channel=args.channel, bpm=args.bpm, click_track=args.click_track, 
            pulse=args.pulse, period=args.period, click_track_phase=args.click_track_phase, accent_downbeat=args.downbeat)
        
    if args.format == 'wav':
        (_, tmp_wav) = tempfile.mkstemp(suffix='.wav')
        process = subprocess.Popen([
            'fluidsynth', 
            '--audio-driver=alsa', 
            '/usr/share/sounds/sf2/FluidR3_GM.sf2',
            mid_path,
            '-F',
            args.output_path
        ])
        process.communicate()
    elif args.format == 'mp3':
        (_, tmp_wav) = tempfile.mkstemp(suffix='.wav')
        process = subprocess.Popen([
            'fluidsynth', 
            '--audio-driver=alsa', 
            '/usr/share/sounds/sf2/FluidR3_GM.sf2',
            mid_path,
            '-F',
            tmp_wav
        ])
        process.communicate()
        process = subprocess.Popen([
            'lame', 
            '-V2',
            tmp_wav,
            args.output_path
        ])
        process.communicate()
    elif args.format == 'ogg':
        (_, tmp_wav) = tempfile.mkstemp(suffix='.wav')
        process = subprocess.Popen([
            'fluidsynth', 
            '--audio-driver=alsa', 
            '/usr/share/sounds/sf2/FluidR3_GM.sf2',
            mid_path,
            '-F',
            tmp_wav
        ])
        process.communicate()
        process = subprocess.Popen([
            'oggenc', 
            tmp_wav,
            '--output',
            args.output_path
        ])
        process.communicate()

