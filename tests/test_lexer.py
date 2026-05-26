"""Testes do lexer: tokenização de cada instrução Natural."""

import pytest

from nat2algo.lexer import Token, tokenize_lines


def _tok(lines: list[str]) -> list[Token]:
    return tokenize_lines(lines)


class TestComments:
    def test_full_line_comment_is_comment_token(self) -> None:
        tokens = _tok(["* isso é um comentário\n"])
        assert len(tokens) == 1
        assert tokens[0].keyword == "COMMENT"
        assert tokens[0].args == "isso é um comentário"

    def test_inline_comment_stripped_from_args(self) -> None:
        tokens = _tok(["WRITE 'ok' /* comentário\n"])
        assert tokens[0].keyword == "WRITE"
        assert "comentário" not in tokens[0].args

    def test_blank_lines_discarded(self) -> None:
        tokens = _tok(["   \n", "\n", "END\n"])
        assert len(tokens) == 1
        assert tokens[0].keyword == "END"


class TestKeywordRecognition:
    def test_simple_keywords(self) -> None:
        pairs = [
            ("IF #X > 0\n", "IF"),
            ("ELSE\n", "ELSE"),
            ("END-IF\n", "END-IF"),
            ("FOR #I = 1 TO 5\n", "FOR"),
            ("END-FOR\n", "END-FOR"),
            ("MOVE A TO B\n", "MOVE"),
            ("COMPUTE #X = 1\n", "COMPUTE"),
            ("ADD 1 TO #C\n", "ADD"),
            ("SUBTRACT 2 FROM #C\n", "SUBTRACT"),
            ("MULTIPLY #C BY 3\n", "MULTIPLY"),
            ("DIVIDE 2 INTO #C\n", "DIVIDE"),
            ("WRITE 'texto'\n", "WRITE"),
            ("DISPLAY #X\n", "DISPLAY"),
            ("INPUT #VAR\n", "INPUT"),
            ("PERFORM SUB-ROTINA\n", "PERFORM"),
            ("END\n", "END"),
        ]
        for line, expected_kw in pairs:
            tokens = _tok([line])
            assert tokens[0].keyword == expected_kw, f"Falhou para: {line.strip()}"

    def test_define_data_compound_keyword(self) -> None:
        tokens = _tok(["DEFINE DATA LOCAL\n"])
        assert tokens[0].keyword == "DEFINE DATA"

    def test_define_subroutine_compound_keyword(self) -> None:
        tokens = _tok(["DEFINE SUBROUTINE CALC\n"])
        assert tokens[0].keyword == "DEFINE SUBROUTINE"
        assert tokens[0].args == "CALC"

    def test_unknown_line_preserved(self) -> None:
        tokens = _tok(["  1 #VAR (N10.2)\n"])
        assert tokens[0].keyword == "UNKNOWN"
        assert "#VAR" in tokens[0].args

    def test_case_insensitive_matching(self) -> None:
        tokens = _tok(["if #x > 0\n"])
        assert tokens[0].keyword == "IF"

    def test_line_number_is_correct(self) -> None:
        tokens = _tok(["* comentário\n", "\n", "END\n"])
        # linha 2 em branco descartada; END está na linha 3
        end_tok = next(t for t in tokens if t.keyword == "END")
        assert end_tok.line_no == 3
