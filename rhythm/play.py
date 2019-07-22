from pymuco.midi.lhl import DrumKit
from pymuco.lhl.representations import Grid, Meter, TimeSignature
from pymuco.util import commandline

import pickle

ts = TimeSignature(4, 4)
ts.divisions = (2, 2, 2, 2)

witek = pickle.load(open('/home/bastiaan/PhD/Data/custom/witek.pickle', 'rb'))

rhythms = list(sorted(witek.keys()))
choice = commandline.menu('', rhythms)
rhythm = witek[rhythms[choice]]

drumkit = DrumKit(
    {
        'Snare Drum 1':rhythm['snare_drum'],
        'Bass Drum 2':rhythm['bass_drum'],
        'Closed Hi-hat':rhythm['hi_hat'],
    }
)

drumkit.bpm = 480

drumkit.play()
