import sys
import mido
from mido import MidiFile


def play(device_id: str, midi_file: str):
    with mido.open_output(device_id) as port:
        for message in MidiFile(midi_file).play():
            port.send(message)


if __name__ == '__main__':
    import pickle

    with open(sys.argv[1], 'rb') as tmpfs:
        data = pickle.load(tmpfs)
        play(data['dv_id'], data['midi_file'])
