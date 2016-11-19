from itertools import chain
from typing import Dict, List

import sh

from app.dao import Track, NoteInfo, RestInfo, ChordInfo
from .base import SeparateTrackPlayer

play = sh.Command('play')

QueueIndex = int


class SoxPlayer(SeparateTrackPlayer):
    def __init__(self):
        super().__init__()
        self.tempo = 60

    def _queue_note(self, track: int, note_data: NoteInfo):
        t = note_data.time * self.tempo_adjust
        args = ['|sox', '-n', '-p']
        if isinstance(note_data, RestInfo):
            args += ['trim', '0', str(t)]
        elif isinstance(note_data, ChordInfo):
            args += ["synth", str(t)]
            args += chain.from_iterable(['pluck', x.note] for x in note_data.children)
        else:
            print("Skipping unknown NoteInfo", type(note_data).__name__)
            return
        return ' '.join(args)

    @property
    def tempo_adjust(self):
        if not self.tempo:
            raise ValueError("Invalid tempo!")
        return 60 / self.tempo

    def play_queue(self, queue: List, track: Dict[Track, int]):
        playing = [play(*q, _bg=True) for q in queue]
        for proc in playing:
            proc.wait()
