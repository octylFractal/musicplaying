#!/usr/bin/env bash
echo "A4 Lexer... "  && antlr4 -o app/gen -lib app/gen SheetLexer.g4
echo "A4 Parser... " && antlr4 -o app/gen -lib app/gen SheetParser.g4