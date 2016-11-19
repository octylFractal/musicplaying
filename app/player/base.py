from app.dao import Sheet, Track, NoteInfo
from typing import Dict, List

QueueIndex = int


class Player:
    def __init__(self):
        super().__init__()

    def reset(self):
        """
        Reset the player to begin queueing again.
        :return:
        """
        pass

    def queue(self, sheet: Sheet):
        """
        Queues some note data to be played.

        :param sheet: The note/rest to play
        :return: None
        """
        pass

    def play(self):
        """
        Plays all the queued data.
        :return:
        """
        pass


class SeparateTrackPlayer(Player):
    def __init__(self):
        super().__init__()
        self.tempo = 0
        self._track_to_queue_index = {}
        self._queue = []

    def play(self):
        self.play_queue(self._queue, self._track_to_queue_index)

    def play_queue(self, queue: List, track: Dict[Track, int]):
        pass

    def _add_track(self, track: Track) -> QueueIndex:
        i = len(self._queue)
        self._track_to_queue_index[track] = i
        self._queue.append([])
        return i

    def _queue_note(self, track: int, note_data: NoteInfo):
        """
        Returns insertion data for the queue.

        If the returned object is a List or Tuple, it will be flattened.
        :param track:
        :param note_data:
        :return:
        """
        pass

    def queue(self, sheet: Sheet):
        self.tempo = sheet.tempo
        for track in sheet.tracks:
            qi = self._add_track(track)
            for n in track.notes:
                append = self._queue_note(qi, n)
                if isinstance(append, (list, tuple)):
                    self._queue[qi] += append
                else:
                    self._queue[qi].append(append)

    def reset(self):
        super().reset()
        self._track_to_queue_index = {}
        self._queue = []
