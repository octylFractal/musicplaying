from .sox import SoxPlayer
from .mido_midi import MidoMidiPlayer
from .base import Player

all_players = [
    SoxPlayer,
    MidoMidiPlayer
]
