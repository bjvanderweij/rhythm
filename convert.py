#!/usr/bin/python3
import sys, argparse, subprocess, tempfile
from midiutil.MidiFile3 import MIDIFile

parser = argparse.ArgumentParser()

parser.add_argument('output_path',
    help='Path to the output file')

parser.add_argument('--bpm',
    type=int,
    default=120,
    help='Beats per minute for the midi file')
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
parser.add_argument('--click-track-start',
    type=int,
)


def save_midi(iois, pitches, path, click_track=False, click_track_start=0, accent_downbeat=False, period=0, pulse=1, bpm=240, channel=0, velocity=100):
    '''
    bpm means grid-units per second in this case
    '''

    track = 0

    mf = MIDIFile(1)

    mf.addTrackName(track, 0, "Sample Track")
    mf.addTempo(track, 0, bpm)

    rhythm_start = 0

    if click_track: 

        if click_track_start < 0:
            rhythm_start = -click_track_start
            click_track_start = 0

        click_track_end = (
            rhythm_start + len(iois)
        )

        write_click_track(mf, start_time=click_track_start, end_time=click_track_end, period=period, pulse=pulse, velocity=velocity, accent_downbeat=accent_downbeat)

    write_notes(mf, iois, pitches, start_time=rhythm_start, track=track, channel=channel, velocity=velocity)

    with open(path, 'wb') as midi_file:
        mf.writeFile(midi_file)

def write_notes(midi_file, iois, pitches, start_time=0, track=0, channel=0, velocity=100):

    time = start_time

    for duration, pitch in zip(iois, pitches):

        midi_file.addNote(track, channel, pitch, time, duration, velocity)
        time += duration

    return time

def write_click_track(midi_file, start_time=0, end_time=0, track=0, velocity=100, accent_downbeat=0, *, period, pulse):

    time = start_time
    channel = 9
    cowbell = 56
    hi_woodblock = 76
    lo_woodblock = 77
    stick = 37

    for beat in range((end_time - start_time) // pulse):

        midi_file.addNote(track, channel, hi_woodblock if time % period == 0 and accent_downbeat else lo_woodblock, time, pulse, velocity - int(0.25 * velocity))
        time += pulse

    return time

if __name__ == '__main__':
    args = parser.parse_args()

    # Read rhythm from stdin
    inp = [list(map(float, line.split(' '))) for line in sys.stdin]
    iois = inp[0]
    pitches = list(map(int, inp[1]))

    resolution = 4

    if args.format in ('midi', 'mid'):
        mid_path = args.output_path
    else:
        (_, mid_path) = tempfile.mkstemp(suffix='.mid')

    save_midi(iois, pitches, mid_path, channel=args.channel, bpm=args.bpm, click_track=args.click_track, pulse=args.pulse, period=args.period, click_track_start=args.click_track_start, accent_downbeat=args.downbeat)
        
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

