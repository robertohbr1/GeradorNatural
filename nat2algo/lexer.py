"""
Lexer para código-fonte Natural/Adabas em texto puro.

Responsabilidade única: transformar linhas de texto em tokens tipados,
sem nenhuma lógica de estrutura de blocos (isso fica no parser).

Uso:
    tokens = tokenize_lines(open("prog.txt").readlines())
    for tok in tokens:
        print(tok)
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Sequence

from nat2algo.mappings import ALL_MAPPINGS


@dataclass(frozen=True)
class Token:
    """Um token extraído de uma linha do código Natural.

    Args:
        line_no: número da linha original (1-indexed).
        keyword:  palavra-chave Natural reconhecida (uppercase), ou 'COMMENT'/'UNKNOWN'.
        args:     resto da linha após a keyword (já sem comentário inline).
        raw:      texto original da linha sem a quebra de linha.
    """

    line_no: int
    keyword: str
    args: str
    raw: str


# Palavras-chave compostas precisam ser testadas antes das simples.
# Ordenadas do maior prefixo para o menor para que o match guloso funcione.
_ORDERED_KEYWORDS: list[str] = sorted(
    ALL_MAPPINGS.keys(), key=len, reverse=True
)

# Padrão para remover comentário inline (/* até o fim da linha)
_INLINE_COMMENT_RE: re.Pattern[str] = re.compile(r"/\*.*$")


def _strip_inline_comment(text: str) -> str:
    return _INLINE_COMMENT_RE.sub("", text).rstrip()


def _is_full_line_comment(line: str) -> bool:
    """Retorna True se a linha inteira é um comentário Natural (começa com *)."""
    stripped = line.lstrip()
    return stripped.startswith("*") and not stripped.startswith("*/")


def _match_keyword(normalized: str) -> tuple[str, str] | None:
    """Tenta casar a linha com alguma keyword conhecida.

    Retorna (keyword, args) ou None se nenhuma bater.
    """
    for kw in _ORDERED_KEYWORDS:
        if normalized == kw:
            return kw, ""
        if normalized.startswith(kw + " ") or normalized.startswith(kw + "\t"):
            args = normalized[len(kw):].strip()
            return kw, args
    return None


def tokenize_lines(lines: Sequence[str]) -> list[Token]:
    """Converte uma lista de linhas de código Natural em tokens.

    Args:
        lines: linhas do arquivo (com ou sem '\\n' no final).

    Returns:
        Lista de Token, uma por linha significativa.
        Linhas em branco são descartadas silenciosamente.

    Example:
        >>> tokens = tokenize_lines(["IF #X > 0\\n", "  WRITE 'ok'\\n", "END-IF\\n"])
        >>> [t.keyword for t in tokens]
        ['IF', 'WRITE', 'END-IF']
    """
    tokens: list[Token] = []

    for line_no, raw_line in enumerate(lines, start=1):
        raw = raw_line.rstrip("\n\r")
        stripped = raw.strip()

        if not stripped:
            continue

        if _is_full_line_comment(stripped):
            comment_text = stripped.lstrip("*").strip()
            tokens.append(Token(line_no, "COMMENT", comment_text, raw))
            continue

        clean = _strip_inline_comment(stripped)
        normalized = clean.upper()

        match = _match_keyword(normalized)
        if match:
            keyword, args = match
            # Preserva o case original dos args (variáveis e literais)
            original_args = clean[len(keyword):].strip()
            tokens.append(Token(line_no, keyword, original_args, raw))
        else:
            # Linha não reconhecida: preserva como UNKNOWN para não perder info
            tokens.append(Token(line_no, "UNKNOWN", clean, raw))

    return tokens
