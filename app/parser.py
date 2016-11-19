from antlr4.BufferedTokenStream import BufferedTokenStream
from antlr4.InputStream import InputStream
from antlr4.error.ErrorListener import ErrorListener
from antlr4.error.Errors import NoViableAltException
from app.gen import SheetLexer, SheetParser

from app.dao import Sheet
from app.exceptions import AntlrSyntaxError


def parse(source: str) -> Sheet:
    return __do_parse(InputStream(source)).sheetObj


def __do_parse(source: InputStream) -> SheetParser.SheetContext:
    # really type Lexer, but antlr4 has buggy type annotations...
    lexer = SheetLexer(source)  # type: None
    stream = BufferedTokenStream(lexer)
    parser = SheetParser(stream)

    parser.removeErrorListeners()
    parser.addErrorListener(SPL())

    return parser.sheet()


class SPL(ErrorListener):
    def __init__(self):
        super().__init__()

    def syntaxError(self, recognizer: SheetParser, offending_symbol, line, column, msg, e):
        if isinstance(e, NoViableAltException):
            msg += "; current ctx = {}".format(type(recognizer._ctx).__name__)
        raise AntlrSyntaxError(msg, line, column)


__all__ = ['parse']
