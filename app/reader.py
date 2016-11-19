import mido

from app.player.mido_midi import request_device

intest = request_device(True)
print(intest)
bufsize = 512
dev = mido.open_input(intest)
print('Ready to roll!')
for event in dev:
    print(event)
