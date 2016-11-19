def _msg_from_args(m, l, c):
    return "line {}, column {}: {}".format(l, c, m)


class AntlrSyntaxError(Exception):
    def __init__(self, msg, lineno, column):
        super().__init__(_msg_from_args(msg, lineno, column))
        self.original_message = msg
        self.lineno = lineno
        self.column = column
