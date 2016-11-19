from .base import Player
from .mido_midi import MidoMidiPlayer
from .sox import SoxPlayer

all_players = [
    SoxPlayer,
    MidoMidiPlayer
]
