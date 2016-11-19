from abc import ABC, abstractmethod
from typing import List, Tuple


class Note:
    def __init__(self, note: str):
        # normalize note
        self.note = note[0].upper() + note[1:]

    def __repr__(self):
        return self.note


class NoteInfo(ABC):
    def __init__(self, time: int):
        if time is None:
            raise ValueError("time cannot be None")
        self.time = time

    @abstractmethod
    def is_rest(self) -> bool:
        pass


class RestInfo(NoteInfo):
    def __init__(self, time: int):
        super().__init__(time)

    def is_rest(self) -> bool:
        return True


class ChordInfo(NoteInfo):
    def __init__(self, time: int, children: List[Note]):
        super().__init__(time)
        self.children = tuple(children)  # type: Tuple[Note]

    def is_rest(self) -> bool:
        return False

    def __repr__(self):
        return 'Chord[time=' + str(self.time) + ';' + ''.join(map(repr, self.children)) + ']'
