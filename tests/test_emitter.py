"""Testes do emitter: saída final em pseudocódigo português."""

import os
from nat2algo.emitter import emit
from nat2algo.lexer import tokenize_lines
from nat2algo.parser import parse


def _emit(lines: list[str]) -> str:
    return emit(parse(tokenize_lines(lines)))


class TestArithmeticTranslations:
    def test_move_to(self) -> None:
        out = _emit(["MOVE 5000 TO #SAL\n", "END\n"])
        assert "#SAL ← 5000" in out

    def test_compute_equals(self) -> None:
        out = _emit(["COMPUTE #X = #A * 2\n", "END\n"])
        assert "#X ← #A * 2" in out

    def test_add_to(self) -> None:
        out = _emit(["ADD 1 TO #CNT\n", "END\n"])
        assert "#CNT ← #CNT + 1" in out

    def test_subtract_from(self) -> None:
        out = _emit(["SUBTRACT 10 FROM #TOTAL\n", "END\n"])
        assert "#TOTAL ← #TOTAL - 10" in out

    def test_multiply_by(self) -> None:
        out = _emit(["MULTIPLY #BASE BY 0.1\n", "END\n"])
        assert "#BASE ← #BASE * 0.1" in out

    def test_divide_into(self) -> None:
        out = _emit(["DIVIDE 2 INTO #VAL\n", "END\n"])
        assert "#VAL ← #VAL / 2" in out


class TestConditionals:
    def test_if_translated(self) -> None:
        lines = ["IF #X > 0\n", "  WRITE 'ok'\n", "END-IF\n", "END\n"]
        out = _emit(lines)
        assert "SE #X > 0 ENTÃO" in out
        assert "FIM-SE" in out

    def test_else_translated(self) -> None:
        lines = [
            "IF #X > 0\n", "  WRITE 'pos'\n",
            "ELSE\n", "  WRITE 'neg'\n",
            "END-IF\n", "END\n",
        ]
        out = _emit(lines)
        assert "SENÃO" in out

    def test_indentation_increases_inside_if(self) -> None:
        lines = ["IF #X > 0\n", "  WRITE 'ok'\n", "END-IF\n", "END\n"]
        out = _emit(lines)
        # ESCREVER deve estar indentado (2 espaços)
        assert "  ESCREVER 'ok'" in out


class TestLoops:
    def test_read_translated(self) -> None:
        lines = ["READ EMP BY NAME\n", "  DISPLAY NAME\n", "END-READ\n", "END\n"]
        out = _emit(lines)
        assert "LER EMP BY NAME" in out
        assert "FIM-LEITURA" in out

    def test_for_translated(self) -> None:
        lines = ["FOR #I = 1 TO 5\n", "  ADD 1 TO #S\n", "END-FOR\n", "END\n"]
        out = _emit(lines)
        assert "PARA #I = 1 TO 5 FAÇA" in out
        assert "FIM-PARA" in out


class TestSubroutines:
    def test_subroutine_in_separate_section(self) -> None:
        lines = [
            "PERFORM CALC\n",
            "END\n",
            "DEFINE SUBROUTINE CALC\n",
            "  WRITE 'calculando'\n",
            "END-SUBROUTINE\n",
        ]
        out = _emit(lines)
        assert "EXECUTAR CALC" in out
        assert "SUBROTINAS" in out
        assert "SUBROTINA CALC" in out
        assert "FIM-SUBROTINA" in out
        # Subroutine deve vir DEPOIS do corpo principal
        assert out.index("EXECUTAR CALC") < out.index("SUBROTINAS")

    def test_comment_becomes_double_slash(self) -> None:
        out = _emit(["* isso é um comentário\n", "END\n"])
        assert "// isso é um comentário" in out


class TestDefineData:
    def test_local_variables_section(self) -> None:
        lines = [
            "DEFINE DATA LOCAL\n",
            "  1 #X (N5)\n",
            "END-DEFINE\n",
            "END\n",
        ]
        out = _emit(lines)
        assert "VARIÁVEIS LOCAIS:" in out
        assert "#X (N5)" in out

    def test_end_statement(self) -> None:
        out = _emit(["END\n"])
        assert "FIM" in out


class TestGoldenFiles:
    """Testa a saída completa contra o arquivo de fixture básico."""

    def test_basic_fixture_contains_expected_lines(self) -> None:
        fixture = os.path.join(
            os.path.dirname(__file__), "fixtures", "sample_basic.txt"
        )
        with open(fixture, encoding="utf-8") as f:
            lines = f.readlines()
        out = _emit(lines)

        expected_fragments = [
            "VARIÁVEIS LOCAIS:",
            "#SALARIO ← 5000.00",
            "SE #SALARIO > 3000 ENTÃO",
            "#DESCONTO ← #SALARIO * 0.27",
            "SENÃO",
            "#DESCONTO ← #SALARIO * 0.15",
            "FIM-SE",
            "#LIQUIDO ← #SALARIO - #DESCONTO",
            "ESCREVER 'Salário Líquido: ' #LIQUIDO",
            "FIM",
        ]
        for fragment in expected_fragments:
            assert fragment in out, f"Fragmento ausente na saída: {fragment!r}"
