parser grammar SheetParser;

options {
    language = Python3;
    tokenVocab = SheetLexer;
}

@header {
from app.dao import *
import itertools
}

sheet
    returns [sheetObj]
    locals [tempoVal=60,notes=list()]
    :   (tempoCtx=tempo {$tempoVal = $tempoCtx.val})?
        (tracks+=track WS?)+
        EOF
        {$sheetObj = Sheet($tempoVal, [t.trackObj for t in $tracks])}
    ;
tempo
    returns [val]
    : TempoHeader timeCtx=Number {self._input.LT(1).text == "\n"}? WS
      {$val = int($timeCtx.text)}
    ;
noteRestRepeat
    returns [notes=list()]
    :
    (     n=noteOrRest {$notes.append($n.note)}
        | r=repeat {$notes += $r.notes}
        | g=graceNote {$notes += $g.notes}
        );
noteOrRest
    returns [note]
    locals [time]
    : timeCtx=noteTime {$time = $timeCtx.time}
    NoteTimeSep
    (     c=chord {$note = ChordInfo($time, $c.notes)}
        | r=Rest {$note = RestInfo($time)}
        )
    ;
noteTime
    returns [time]
    : timeCtx=rawNoteTime
      {$time = $timeCtx.top / $timeCtx.bottom}
    ;
rawNoteTime
    returns [top, bottom]
    : topCtx=Number (Division bottomCtx=Number)?
      {$top = int($topCtx.text)}
      {$bottom = int($bottomCtx.text or 1)}
    ;
chord
    returns [notes=list()]
    : (noteCtx=Note {$notes.append(Note($noteCtx.text))})
      (Division noteCtx=Note {$notes.append(Note($noteCtx.text))})*
    ;
track
    returns [trackObj]
    locals [ident,instrument,notes]
    : Track
        identCtx=Identifier {$ident = $identCtx.text[1:-1]} WS
        instrumentCtx=Identifier {$instrument = $instrumentCtx.text[1:-1]}
      WS? BlockStart WS? data+=noteRestRepeat (WS data+=noteRestRepeat)* WS? BlockEnd
      {$notes = list(itertools.chain.from_iterable(d.notes for d in $data))}
      {$trackObj = Track($ident, $instrument, $notes)}
    ;
repeat
    returns [notes]
    : Repeat
        count=Number
      WS? BlockStart WS? data+=noteRestRepeat (WS data+=noteRestRepeat)* WS? BlockEnd
      {$notes = int($count.text) * list(itertools.chain.from_iterable(d.notes for d in $data))}
    ;
timeAndNote
    returns [top, bottom, notes]
    : timeCtx=rawNoteTime {$top, $bottom = $timeCtx.top, $timeCtx.bottom}
      NoteTimeSep
      c=chord {$notes = $c.notes}
    ;
graceNote
    returns [notes]
    locals [t, b, s64]
    : GraceNote
        grace=Note
      WS? BlockStart WS? data=timeAndNote WS? BlockEnd
      {$t, $b = $data.top, $data.bottom}
      {$s64 = [$t * 64, $b * 64]}
      {$notes = [
            ChordInfo($t / $s64[1], [Note($grace.text)]),
            ChordInfo(($s64[0] - $t) / $s64[1], $data.notes)
      ]}
    ;