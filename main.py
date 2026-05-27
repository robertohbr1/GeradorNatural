"""
Ponto de entrada CLI do transpilador Natural/Adabas → Pseudocódigo em português.

Uso:
    python main.py <arquivo.txt> [--output saida.algo] [--encoding cp1252]

Exemplos:
    python main.py programa.txt
    python main.py programa.txt --output resultado.algo
    python main.py programa.txt --encoding utf-8
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from nat2algo.emitter import emit
from nat2algo.lexer import tokenize_lines
from nat2algo.parser import ParseError, parse


def _build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="nat2algo",
        description="Transpilador Natural/Adabas → Pseudocódigo em Português",
    )
    p.add_argument("input", type=Path, help="Arquivo .txt com código-fonte Natural")
    p.add_argument(
        "--output", "-o",
        type=Path,
        default=None,
        help="Arquivo de saída (padrão: mesmo nome com extensão .algo)",
    )
    p.add_argument(
        "--encoding", "-e",
        default="cp1252",
        help="Codificação do arquivo de entrada (padrão: cp1252)",
    )
    return p


def _resolve_output(input_path: Path, output_arg: Path | None) -> Path:
    if output_arg is not None:
        return output_arg
    return input_path.with_suffix(".algo")


def _preprocess_natural_lines(raw_lines: list[str]) -> list[str]:
    """Remove linhas de controle do Natural e descarta a numeração de linha.

    Linhas com ':' na coluna 3 (índice 2) e na coluna 5 (índice 4) são
    marcadores internos do editor Natural e devem ser ignoradas.
    As primeiras 5 colunas de cada linha restante são a numeração de linha
    padrão do Natural e também são descartadas.
    """
    result: list[str] = []
    for line in raw_lines:
        if len(line) >= 6 and line[2] == ":" and line[5] == ":":
            continue
        result.append(line[5:] if len(line) > 5 else "\n")
    return result


def _read_source(path: Path, encoding: str) -> list[str]:
    if not path.exists():
        print(f"Erro: arquivo não encontrado: {path}", file=sys.stderr)
        sys.exit(1)
    try:
        raw = path.read_text(encoding=encoding).splitlines(keepends=True)
        return _preprocess_natural_lines(raw)
    except UnicodeDecodeError as exc:
        print(
            f"Erro de codificação ao ler '{path}' com encoding '{encoding}': {exc}\n"
            "Tente --encoding utf-8 ou --encoding latin-1",
            file=sys.stderr,
        )
        sys.exit(1)


def _write_output(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")
    print(f"[OK] Pseudocodigo gerado em: {path}")


def main() -> None:
    args = _build_arg_parser().parse_args()

    source_lines = _read_source(args.input, args.encoding)
    output_path = _resolve_output(args.input, args.output)

    try:
        tokens = tokenize_lines(source_lines)
        program = parse(tokens)
        pseudocode = emit(program)
    except ParseError as exc:
        print(f"Erro de parse: {exc}", file=sys.stderr)
        sys.exit(1)

    _write_output(output_path, pseudocode)


if __name__ == "__main__":
    main()
