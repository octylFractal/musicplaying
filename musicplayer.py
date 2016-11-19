from enum import Enum
from sh import play
from pprint import pprint
import sys

class Note:
    def __init__(self, note):
        self.note = note
    def __repr__(self):
        return self.note
class NoteInfo:
    def __init__(self, children, time):
        if time is None:
            raise ValueError("time cannot be None")
        self.children = tuple(children)
        self.time = time
    def is_rest(self):
        return self.children[0].note == 'REST'
    def __repr__(self):
        return 'NoteInfo(' + self.time + ':' + ';'.join(map(repr, self.children)) + ')'
class ParseState(Enum):
    NORMAL = 1
    NORMAL_OR_REPEAT = 2
    REPEAT = 3
    NOTE_LENGTH = 4
    LENGTH_SEP = 5
    NOTE = 6
    MAKING_REST = 7
    SPACING = 8
    END_REPEAT = 9
    CHORD_SEP = 10
def parse(inp):
    # Note format: [length/divison:note]
    # e.g. eight-note A2 == 1/8:A2
    def mkstate(state, *args):
        return (state,) + tuple(args)
    inp = inp.upper()
    statestack = [mkstate(ParseState.NORMAL)]
    def gettop():
        return statestack[-1]
    consumedchars = ''
    for c in inp:
        i = 1
        while i > 0:
            top = gettop()
            if top[0] == ParseState.NORMAL:
                if c.isdigit():
                    # unknown
                    statestack.pop()
                    statestack.append(mkstate(ParseState.NORMAL_OR_REPEAT, c))
                elif c == ' ':
                    statestack.pop()
                    statestack.append(mkstate(ParseState.SPACING))
                elif c == '}':
                    statestack.insert(-1, mkstate(ParseState.END_REPEAT))
                elif c == ';':
                    statestack.insert(-1, mkstate(ParseState.CHORD_SEP))
                else:
                    raise ValueError('Expected [0-9 };], got "{}"'.format(c))
            elif c == '}':
                statestack.append(mkstate(ParseState.END_REPEAT))
                statestack.append(mkstate(ParseState.NORMAL))
            elif top[0] == ParseState.NORMAL_OR_REPEAT:
                # three choices, either another digit, a '/', or a '{'
                statestack.pop()
                chars = top[1] + c
                if c.isdigit():
                    statestack.append(mkstate(ParseState.NORMAL_OR_REPEAT, chars))
                elif c == '/':
                    # turn to NOTE_LENGTH
                    statestack.append(mkstate(ParseState.NOTE_LENGTH, chars))
                elif c == '{':
                    # turn to REPEAT
                    statestack.append(mkstate(ParseState.REPEAT, chars[:-1]))
                else:
                    raise ValueError('Expected [0-9/{], got "{}"'.format(c))
            elif top[0] == ParseState.NOTE_LENGTH:
                if c == ':':
                    statestack.append(mkstate(ParseState.LENGTH_SEP))
                else:
                    statestack.pop()
                    chars = top[1] + c
                    statestack.append(mkstate(ParseState.NOTE_LENGTH, chars))
            elif top[0] == ParseState.LENGTH_SEP:
                if c == 'R':
                    statestack.append(mkstate(ParseState.MAKING_REST, c))
                else:
                    statestack.append(mkstate(ParseState.NOTE, c))
            elif top[0] == ParseState.NOTE:
                if c == ' ':
                    statestack.append(mkstate(ParseState.SPACING))
                elif c == ';':
                    statestack.insert(-1, mkstate(ParseState.CHORD_SEP))
                    statestack.append(mkstate(ParseState.NORMAL))
                else:
                    statestack.pop()
                    if c == 'B' and top[1]:
                        c = 'b'
                    chars = top[1] + c
                    statestack.append(mkstate(ParseState.NOTE, chars))
            elif top[0] == ParseState.MAKING_REST:
                req = 'REST'
                req = req.replace(top[1], '')
                if not req:
                    # done!
                    statestack.append(mkstate(ParseState.NORMAL))
                    i += 1
                elif c == req[0]:
                    statestack.pop()
                    chars = top[1] + c
                    statestack.append(mkstate(ParseState.MAKING_REST, chars))
                else:
                    raise ValueError('REST expected a ' + req[0] + ' next, got ' + c)
            elif top[0] == ParseState.SPACING:
                if c == ' ':
                    pass
                else:
                    statestack.append(mkstate(ParseState.NORMAL))
                    i += 1
            elif top[0] == ParseState.REPEAT:
                statestack.append(mkstate(ParseState.NORMAL))
                i += 1
            else:
                raise ValueError('whoops. ' + c + '; ' + str(statestack))
            i -= 1
        consumedchars += c
    def convert(tokens, is_repeat=False, repeat_times=None):
        time = None
        notes = []
        infos = []
        idx = 0
        print('enter convert', {
            "tokens": tokens, "repeat": is_repeat, "repeat_times": repeat_times
        })
        while idx < len(tokens):
            t = tokens[idx]
            print('consume', t)
            if t[0] == ParseState.NORMAL:
                pass
            elif t[0] == ParseState.NOTE_LENGTH:
                time = t[1]
            elif t[0] == ParseState.LENGTH_SEP:
                pass
            elif t[0] == ParseState.MAKING_REST or t[0] == ParseState.NOTE:
                notes.append(Note(t[1]))
            elif t[0] == ParseState.CHORD_SEP:
                pass
            elif t[0] == ParseState.SPACING:
                infos.append(NoteInfo(notes, time))
                time = None
                notes = []
            elif t[0] == ParseState.REPEAT:
                data = convert(tokens[idx+1:], True, int(t[1]))
                print('repeat data', data)
                infos += data[0]
                old = idx
                idx += data[1]
                print('tok_skip', tokens[old:idx])
            elif t[0] == ParseState.END_REPEAT:
                if is_repeat:
                    infos.append(NoteInfo(notes, time))
                    return infos*repeat_times, idx + 1
            else:
                raise ValueError('unknown ' + str(t[0]))
            idx += 1
        if notes and time:
            infos.append(NoteInfo(notes, time))
            time = None
            notes = []
        print('exiting convert', tokens)
        if is_repeat:
            raise ValueError("should have returned differently, tokens: " + str(tokens))
        return infos
    # trash all extra tokens left on stack
    x = gettop()
    while x[0] in (ParseState.SPACING, ParseState.NORMAL):
        print('pop', x)
        statestack.pop()
        x = gettop()
    return convert(statestack)

def main(f=None):
    inp = None
    if f:
        with open(f, 'r') as f:
            inp = ' '.join(map(str.strip, f))
    inp = inp or input('Data plz? ')
    nums = parse(inp)
    arr = []
    for n in nums:
        t = eval(n.time)
        if n.is_rest():
            arr.append("|sox -n -p trim 0 {}".format(t))
            continue
        parsef = ' '.join('pluck {}'.format(x.note) for x in n.children)
        arr.append("|sox -n -p synth {} {}".format(t, parsef))
    play(*arr)
if __name__=='__main__':
    args = sys.argv[1:]
    if not args:
        while True:
            try:
                main()
            except KeyboardInterrupt:
                raise
            except EOFError:
                raise
            except:
                import traceback
                traceback.print_exc()
    else:
        main(*args)
