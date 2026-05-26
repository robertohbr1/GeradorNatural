"""Testes do parser: construção correta da AST."""

import pytest

from nat2algo.lexer import tokenize_lines
from nat2algo.parser import ASTNode, ParseError, Program, parse


def _parse(lines: list[str]) -> Program:
    return parse(tokenize_lines(lines))


class TestSimpleStatements:
    def test_single_write(self) -> None:
        prog = _parse(["WRITE 'ok'\n", "END\n"])
        assert prog.body[0].keyword == "WRITE"

    def test_end_not_in_body_as_child(self) -> None:
        prog = _parse(["WRITE 'x'\n", "END\n"])
        # END deve encerrar o parse — não aparecer como filho de nada
        keywords = [n.keyword for n in prog.body]
        assert "WRITE" in keywords


class TestIfElse:
    def test_if_without_else(self) -> None:
        lines = ["IF #X > 0\n", "  WRITE 'pos'\n", "END-IF\n", "END\n"]
        prog = _parse(lines)
        if_node = prog.body[0]
        assert if_node.keyword == "IF"
        assert if_node.children[0].keyword == "WRITE"

    def test_if_with_else(self) -> None:
        lines = [
            "IF #X > 0\n",
            "  WRITE 'pos'\n",
            "ELSE\n",
            "  WRITE 'neg'\n",
            "END-IF\n",
            "END\n",
        ]
        prog = _parse(lines)
        if_node = prog.body[0]
        assert if_node.keyword == "IF"
        # Último filho deve ser ELSE
        else_node = if_node.children[-1]
        assert else_node.keyword == "ELSE"
        assert else_node.children[0].keyword == "WRITE"

    def test_nested_if(self) -> None:
        lines = [
            "IF #A > 0\n",
            "  IF #B > 0\n",
            "    WRITE 'ambos'\n",
            "  END-IF\n",
            "END-IF\n",
            "END\n",
        ]
        prog = _parse(lines)
        outer = prog.body[0]
        inner = outer.children[0]
        assert inner.keyword == "IF"
        assert inner.children[0].keyword == "WRITE"


class TestLoops:
    def test_read_loop(self) -> None:
        lines = [
            "READ EMPLOYEES BY NAME\n",
            "  DISPLAY NAME\n",
            "END-READ\n",
            "END\n",
        ]
        prog = _parse(lines)
        read_node = prog.body[0]
        assert read_node.keyword == "READ"
        assert read_node.children[0].keyword == "DISPLAY"

    def test_for_loop(self) -> None:
        lines = ["FOR #I = 1 TO 5\n", "  ADD 1 TO #SOMA\n", "END-FOR\n", "END\n"]
        prog = _parse(lines)
        for_node = prog.body[0]
        assert for_node.keyword == "FOR"
        assert for_node.children[0].keyword == "ADD"


class TestSubroutines:
    def test_subroutine_separated_from_body(self) -> None:
        lines = [
            "PERFORM CALC\n",
            "END\n",
            "DEFINE SUBROUTINE CALC\n",
            "  COMPUTE #X = 1\n",
            "END-SUBROUTINE\n",
        ]
        prog = _parse(lines)
        assert prog.body[0].keyword == "PERFORM"
        assert len(prog.subroutines) == 1
        sub = prog.subroutines[0]
        assert sub.keyword == "DEFINE SUBROUTINE"
        assert sub.args == "CALC"
        assert sub.children[0].keyword == "COMPUTE"
