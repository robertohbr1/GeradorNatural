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


def _extract_inline_stmt(text: str) -> tuple[str, str, str] | None:
    """Extrai um statement inline após a condição do IF, ignorando strings."""
    in_str = False
    quote_char = None
    for i, c in enumerate(text):
        if c in ("'", '"'):
            if not in_str:
                in_str = True
                quote_char = c
            elif c == quote_char:
                in_str = False
        elif not in_str and c.isspace():
            substr = text[i+1:].lstrip()
            normalized = substr.upper()
            match = _match_keyword(normalized)
            if match:
                kw, args = match
                valid_starters = {"REINPUT", "WRITE", "DISPLAY", "PRINT", "MOVE", "COMPUTE", "ADD", "SUBTRACT", "MULTIPLY", "DIVIDE", "RESET", "DO", "ESCAPE TOP", "ESCAPE BOTTOM", "STOP", "TERMINATE", "PERFORM", "CALL"}
                if kw in valid_starters:
                    cond = text[:i].strip()
                    if cond.upper().endswith(" THEN"):
                        cond = cond[:-5].strip()
                    return cond, kw, substr[len(kw):].strip()
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

        is_continuation = False
        if tokens and tokens[-1].keyword not in ("COMMENT", "DEFINE DATA"):
            prev_tok = tokens[-1]
            prev_upper = prev_tok.args.upper().rstrip()
            open_parens = prev_tok.args.count("(") - prev_tok.args.count(")")
            triggers = (
                " AND", " OR", "+", "-", "*", "/", "=",
                "<", ">", "<=", ">=", "<>", "^=", "~=",
                " TO", " FROM", " BY", " INTO", " GIVING", " THRU", " NOT"
            )
            exact_triggers = {t.strip() for t in triggers}
            
            if open_parens > 0 or prev_upper.endswith(triggers) or prev_upper in exact_triggers:
                is_continuation = True

        if is_continuation:
            prev_tok = tokens[-1]
            new_args = prev_tok.args + " " + clean.strip()
            new_raw = prev_tok.raw + "\n" + raw
            tokens[-1] = Token(prev_tok.line_no, prev_tok.keyword, new_args, new_raw)
            continue

        match = _match_keyword(normalized)
        if match:
            keyword, _ = match
            original_args = clean[len(keyword):].strip()
            
            if keyword == "IF":
                inline = _extract_inline_stmt(original_args)
                if inline:
                    cond, inline_kw, inline_args = inline
                    tokens.append(Token(line_no, "IF", cond, raw))
                    tokens.append(Token(line_no, inline_kw, inline_args, raw))
                    continue

            # Preserva o case original dos args (variáveis e literais)
            tokens.append(Token(line_no, keyword, original_args, raw))
        else:
            # Verifica atribuição implícita (ex: #VAR = expr)
            if re.match(r"^[A-Za-z0-9\#\-\.\(\)]+\s*=", clean):
                tokens.append(Token(line_no, "COMPUTE", clean, raw))
            else:
                # Linha não reconhecida: preserva como UNKNOWN para não perder info
                tokens.append(Token(line_no, "UNKNOWN", clean, raw))

    return tokens
