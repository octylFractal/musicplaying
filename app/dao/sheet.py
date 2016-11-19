from typing import List

from .infos import NoteInfo


class Sheet:
    def __init__(self, tempo: int, tracks: List['Track']):
        if not tempo:
            raise ValueError("Invalid tempo {}".format(tempo))
        self.tempo = tempo
        self.tracks = tracks


class Track:
    def __init__(self, identifier: str, instrument: str, notes: List[NoteInfo]):
        if not identifier:
            raise ValueError("Invalid identifier {}".format(identifier))
        self.identifier = identifier
        self.instrument = instrument
        self.notes = notes
