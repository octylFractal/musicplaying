import os
import pickle
import sys
import tempfile
from pathlib import Path
from typing import Generator, List, Tuple, Dict, TypeVar

import mido
import sh
from mido import Message, MidiFile

from app.dao import NoteInfo, ChordInfo, Track
from .base import SeparateTrackPlayer


def ask_device(output: bool) -> str:
    print('Please choose a midi device:')
    for i in (mido.get_output_names() if output else mido.get_input_names()):
        print(i)
    while True:
        device = input('> ')
        try:
            return match_device(output, device)
        except ValueError:
            pass


def match_device(output: bool, identification: str) -> str:
    # try interpreting directly as a midi device
    names = mido.get_output_names() if output else mido.get_input_names()
    if identification in names:
        return identification

    for name in names:
        if identification in name:
            return name
    raise ValueError("Couldn't find a match for device identifier " + repr(identification))


DEVICE_FLAG = '--device'


def request_device(output: bool = True) -> str:
    try:
        idx = sys.argv.index(DEVICE_FLAG)
    except ValueError:
        # DEVICE_FLAG not in list
        return ask_device(output)
    if len(sys.argv) <= (idx + 1):
        raise IndexError('device flag requires an argument!')
    return match_device(output, sys.argv[idx + 1])


class MidiNote:
    def __init__(self, channel: int, note: int, note_time: int):
        """

        :param note: 0-127, midi note; or -1 for rest
        :param note_time: in portions of a whole note, time for note to play
        """
        super().__init__()
        self.channel = channel
        self.note = note
        self.time = note_time

    def __repr__(self):
        return "Note {} on channel {} for {}s".format(self.note, self.channel, self.time)


semitones = 12
_letter_to_offset = [
    'C',
    'C#',
    'D',
    'D#',
    'E',
    'F',
    'F#',
    'G',
    'G#',
    'A',
    'B',
]


def _note_to_midi_helper(letter: str, offset: str, octave: int):
    letter = letter.upper()
    # idx is 1-12, in semitones
    idx = _letter_to_offset.index(letter) + 1
    if offset == 'b':
        # down a step
        idx -= 1
        if idx < 1:
            octave -= 1
            idx = semitones
    elif offset == '#':
        # up a step
        idx += 1
        if idx > semitones:
            octave += 1
            idx = 1
    return (octave + 1) * semitones + (idx - 1)


def note_to_midi(note: str) -> int:
    # valid notes are currently [0-7]
    # midi handles [-1-8], and parts of 9, so this could be expanded?
    length = len(note)
    if length < 1 or length > 3:
        raise ValueError("Invalid note " + note)
    if length == 1:
        # octave 4 implicit
        return _note_to_midi_helper(note, '-', 4)
    elif length == 2:
        letter = note[0]
        # either octave or offset
        othing = note[1]
        try:
            octave = int(othing)
            return _note_to_midi_helper(letter, '-', octave)
        except ValueError:
            return _note_to_midi_helper(letter, othing, 4)
    else:  # length == 3
        return _note_to_midi_helper(note[0], note[1], int(note[2]))


def note_info_to_midi(track: int, note_data: NoteInfo) -> Tuple[MidiNote]:
    if note_data.is_rest():
        note = (-1,)
    elif isinstance(note_data, ChordInfo):
        note = tuple(note_to_midi(n.note) for n in note_data.children)
    else:
        raise ValueError("unknown NoteInfo " + type(note_data).__name__)
    return tuple(MidiNote(track, n, note_data.time) for n in note)


class MidoMidiPlayer(SeparateTrackPlayer):
    def __init__(self):
        super().__init__()

        self.device = request_device()
        print('MIDOMIDI is using requested device', self.device)

    def _queue_note(self, track: int, note_data: NoteInfo) -> Tuple[MidiNote]:
        return note_info_to_midi(track, note_data)

    def play_queue(self, queue: List[List[MidiNote]], track: Dict[Track, int]):
        file = make_midi_file(self.tempo, queue)
        fork_and_play(self.device, file)


def make_midi_file(tempo: int, queue: List[List[MidiNote]]) -> MidiFile:
    """
    Takes the queue of notes, returns them in timestamp order.
    :param tempo:
    :param queue:
    :return:
    """
    tpb = mido.midifiles.midifiles.DEFAULT_TICKS_PER_BEAT
    file = MidiFile()
    for (i, track_data) in enumerate(queue):
        track = file.add_track('Track ' + str(i))

        last_delta = 0
        for n in track_data:
            track += note_to_message(tpb, i, n, last_delta)
            # we ignore last_delta changes for now...

    tempo_msg = mido.MetaMessage('set_tempo', tempo=mido.bpm2tempo(tempo))
    for track in file.tracks:
        track.insert(0, tempo_msg)
    return file


def note_to_message(tpb: int, channel: int, note: MidiNote, last_delta: int) \
        -> Generator[Message, None, None]:
    # one beat is a quarter note, time is in whole notes
    time_conv_factor = tpb / 0.25
    if note.note != -1:
        yield Message('note_on', channel=channel, note=note.note, time=last_delta)
        yield Message('note_off', channel=channel, note=note.note,
                      time=int(note.time * time_conv_factor))
    else:
        yield Message('note_off', channel=channel, note=0,
                      time=int(note.time * time_conv_factor))


T = TypeVar('T')


def chunks(l: List[T], n) -> Generator[T, None, None]:
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i + n]


NOTE_ON_BASE = 0x90
NOTE_OFF_BASE = 0x80


def fork_and_play(device_id: str, midi: MidiFile):
    tempdir = tempfile.gettempdir()
    name = tempdir + '/' + 'pygmidi-data' + str(os.getpid()) + '.pickle'
    mid_name = tempdir + '/' + 'pygmidi-data' + str(os.getpid()) + '.midi'
    proc = None
    try:
        midi.save(filename=mid_name)
        with open(name, 'w+b') as tmpfs:
            data = pickle.dumps({
                'dv_id': device_id,
                'midi_file': mid_name
            })
            tmpfs.write(data)

        def iterate_print(file):
            def iterate_for_file(chunk):
                sys.stdout.write(chunk)

            return iterate_for_file

        proc = (sh.Command('python3')
                (Path(__file__).parent / 'split_player.py', name,
                 _out=iterate_print(sys.stdout),
                 _err=iterate_print(sys.stderr), _out_bufsize=0))
        proc.wait()
    except:
        if proc is not None:
            sys.stderr.write(proc.stderr)
        raise
    finally:
        if os.path.exists(name):
            os.unlink(name)
        if os.path.exists(mid_name):
            os.unlink(mid_name)
