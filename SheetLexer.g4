lexer grammar SheetLexer;

options {
    language = Python3;
}

CommentStart: '#' -> skip, mode(COMMENT);

fragment DGT: [0-9];
fragment NUM: DGT+;

TempoHeader: 'Tempo ';

Number: NUM;
Division: '/';
NoteTimeSep: ':';

fragment NoteBase: [a-gA-G];
fragment NoteStep: 'b' | '#';
fragment Octave: [0-7];
Note: NoteBase NoteStep? Octave?;
Rest: 'R';

// Block types
Repeat: 'repeat ';
Track: 'track ';
GraceNote: 'grace ';

BlockStart: '{';
BlockEnd: '}';

Identifier: '"' [a-zA-Z0-9\t ]+ '"';

WS: [\r\n\t ]+;

mode COMMENT;
Newline: '\n' -> skip, mode(DEFAULT_MODE);
AnythingElse: . -> skip;