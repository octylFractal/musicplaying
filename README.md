musicplaying
============

A Python-based music player that uses custom input. Outputs to any MIDI Out using `mido` (PortMidi, RtMidi, or PyGame).

An example program:

```
# comments start with hash
Tempo 60 # optional

# "block"s are of the form
# <type> <arguments> {
#   <more complex data>
# }
# Currently there are 3 blocks: track, repeat, and grace.

# track "name_of_track" "instrument" (both arguments currently ignored)
track "1" "piano" {
    # a note is time:note
    # time is in parts of a whole note
    # note is [a-gA-G](b|#)?[0-9]?
    # or, in pseudo code: [base offset](/* optional */ flat|sharp)/* optional */ [octave]
    # if octave is left out, default is 4

    # all three of the following C notes are the same
    1/4:C
    1/4:C4
    1/4:B#4 # B sharp == C

    # repeat "times"
    # the following two sections are the same
    
    # 1
    1/4:C 1/4:C 1/4:C 1/4:C

    #2
    repeat 4 { 1/4:C }


    # grace note
    # grace notes are handled by multiplying the top and bottom parts of the time by 64
    # the following two sections are the same

    # 1
    1/128:C 63/128:D

    # 2
    grace C { 1/2:D }

    # also the same:

    # 1
    2/384:C 126/384:E # note that 2/384 + 126/384 == 2/6

    # 2
    grace C { 2/6:E }
}
```
