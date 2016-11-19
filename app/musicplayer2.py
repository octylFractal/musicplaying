import sys
from pathlib import Path

import app.parser as parser
from app.dao import Sheet
from app.player import MidoMidiPlayer


def parse(inp: str) -> Sheet:
    return parser.parse(inp)


def main(f: (str, Path) = None):
    inp = None
    if f:
        inp = Path(f).read_text()
    inp = inp or input('Data plz? ')
    print('Parsing input...')
    sheet = parse(inp)
    player = MidoMidiPlayer()  # todo: argument parsing
    print('Queueing notes...')
    player.queue(sheet)
    print('Starting player...')
    player.play()


if __name__ == '__main__':
    args = sys.argv[1:]
    if not args:
        while True:
            main()
    else:
        main(args[0])
