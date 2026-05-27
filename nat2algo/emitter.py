"""
Emitter: percorre a AST e produz pseudocódigo em português.

Responsabilidade única: dado um Program (saída do parser), gerar linhas de texto
algorítmico com indentação de 2 espaços por nível.

Uso:
    from nat2algo.emitter import emit
    text = emit(program)
    print(text)
"""

from __future__ import annotations

import re
from typing import Iterator

from nat2algo.mappings import ALL_MAPPINGS
from nat2algo.parser import ASTNode, Program

_INDENT = "  "  # 2 espaços por nível de indentação

# ── Helpers de tradução de instruções aritméticas ─────────────────────────────

def _emit_move(args: str) -> str:
    """MOVE A TO B  →  B ← A"""
    # Suporta: MOVE expr TO var  e  MOVE CORRESPONDING ...
    match = re.match(r"(.+?)\s+TO\s+(.+)", args, re.IGNORECASE)
    if match:
        source, target = match.group(1).strip(), match.group(2).strip()
        return f"{target} ← {source}"
    return f"MOVER {args}"  # fallback para formas não padrão


def _emit_compute(args: str) -> str:
    """COMPUTE X = expr  →  X ← expr"""
    match = re.match(r"(.+?)\s*=\s*(.+)", args)
    if match:
        var, expr = match.group(1).strip(), match.group(2).strip()
        return f"{var} ← {expr}"
    return f"CALCULAR {args}"


def _emit_add(args: str) -> str:
    """ADD val TO var  →  var ← var + val"""
    match = re.match(r"(.+?)\s+TO\s+(.+)", args, re.IGNORECASE)
    if match:
        val, var = match.group(1).strip(), match.group(2).strip()
        return f"{var} ← {var} + {val}"
    return f"SOMAR {args}"


def _emit_subtract(args: str) -> str:
    """SUBTRACT val FROM var  →  var ← var - val"""
    match = re.match(r"(.+?)\s+FROM\s+(.+)", args, re.IGNORECASE)
    if match:
        val, var = match.group(1).strip(), match.group(2).strip()
        return f"{var} ← {var} - {val}"
    return f"SUBTRAIR {args}"


def _emit_multiply(args: str) -> str:
    """MULTIPLY var BY val  →  var ← var * val"""
    match = re.match(r"(.+?)\s+BY\s+(.+)", args, re.IGNORECASE)
    if match:
        var, val = match.group(1).strip(), match.group(2).strip()
        return f"{var} ← {var} * {val}"
    return f"MULTIPLICAR {args}"


def _emit_divide(args: str) -> str:
    """DIVIDE val INTO var  →  var ← var / val  (ou GIVING para resultado separado)"""
    giving = re.match(
        r"(.+?)\s+INTO\s+(.+?)\s+GIVING\s+(.+)", args, re.IGNORECASE
    )
    if giving:
        val, _var, result = (
            giving.group(1).strip(),
            giving.group(2).strip(),
            giving.group(3).strip(),
        )
        return f"{result} ← {_var} / {val}"

    simple = re.match(r"(.+?)\s+INTO\s+(.+)", args, re.IGNORECASE)
    if simple:
        val, var = simple.group(1).strip(), simple.group(2).strip()
        return f"{var} ← {var} / {val}"
    return f"DIVIDIR {args}"


# ── Handlers especiais ─────────────────────────────────────────────────────────

_SPECIAL_HANDLERS: dict[str, object] = {
    "__MOVE__":     _emit_move,
    "__COMPUTE__":  _emit_compute,
    "__ADD__":      _emit_add,
    "__SUBTRACT__": _emit_subtract,
    "__MULTIPLY__": _emit_multiply,
    "__DIVIDE__":   _emit_divide,
}


def _format_args(args: str) -> str:
    """Aplica formatações nos argumentos, como conversão de operadores."""
    if not args:
        return args
    args = re.sub(r'\bNE\b', '<>', args)
    return args

def _render_node(node: ASTNode) -> str:
    """Converte um nó folha em uma linha de pseudocódigo."""
    template = ALL_MAPPINGS.get(node.keyword)
    formatted_args = _format_args(node.args)

    if template is None:
        if node.keyword == "COMMENT":
            return f"// {formatted_args}" if formatted_args else ""
        if node.keyword == "UNKNOWN":
            return f"/* {formatted_args} */"
        return f"{node.keyword} {formatted_args}".strip()

    if template in _SPECIAL_HANDLERS:
        handler = _SPECIAL_HANDLERS[template]  # type: ignore[index]
        return handler(formatted_args)  # type: ignore[operator]

    if template.startswith("__"):
        # Marcadores de bloco DEFINE DATA tratados pelo _emit_define_data
        return ""

    return template.replace("{args}", formatted_args).strip()


# ── Emissão do bloco DEFINE DATA ──────────────────────────────────────────────

def _emit_define_data(node: ASTNode) -> Iterator[str]:
    """Emite o bloco DEFINE DATA como seção de declaração de variáveis."""
    # node.children contém: LOCAL/GLOBAL/PARAMETER + linhas de variáveis
    current_scope = ""
    var_lines: list[str] = []

    for child in node.children:
        if child.keyword in ("LOCAL", "GLOBAL", "PARAMETER"):
            if current_scope and var_lines:
                yield current_scope
                for v in var_lines:
                    yield _INDENT + v
            current_scope = ALL_MAPPINGS.get(child.keyword, child.keyword)
            var_lines = []
        elif child.keyword == "UNKNOWN":
            # Linhas de declaração de variáveis (ex: "1 #SALARIO (N10.2)")
            var_lines.append(child.args)
        elif child.keyword == "COMMENT":
            var_lines.append(f"// {child.args}")

    if current_scope and var_lines:
        yield current_scope
        for v in var_lines:
            yield _INDENT + v

    yield ""  # linha em branco após declarações


# ── Emissão recursiva de nós ───────────────────────────────────────────────────

def _emit_nodes(nodes: list[ASTNode], depth: int) -> Iterator[str]:
    """Emite recursivamente uma lista de nós com a indentação `depth`."""
    prefix = _INDENT * depth

    for node in nodes:
        if node.keyword == "DEFINE DATA":
            for line in _emit_define_data(node):
                yield line
            continue

        if node.keyword == "COMMENT":
            text = f"// {node.args}" if node.args else ""
            if text:
                yield prefix + text
            continue

        if node.keyword == "ELSE":
            # ELSE reduz um nível para ficar alinhado com o IF
            else_prefix = _INDENT * max(0, depth - 1)
            yield else_prefix + "SENÃO"
            yield from _emit_nodes(node.children, depth)
            continue

        line = _render_node(node)

        if node.children:
            # Bloco estruturado: cabeçalho + filhos indentados
            if line:
                yield prefix + line
            yield from _emit_nodes(node.children, depth + 1)
            # Fechador do bloco
            closer = _block_closer_text(node.keyword)
            if closer:
                yield prefix + closer
        else:
            if line:
                yield prefix + line


def _block_closer_text(opener_keyword: str) -> str:
    """Retorna o texto do fechador algorítmico para cada tipo de bloco."""
    closers: dict[str, str] = {
        "IF":                 "FIM-SE",
        "FOR":                "FIM-PARA",
        "REPEAT":             "FIM-REPETIR",
        "FIND":               "FIM-BUSCA",
        "READ":               "FIM-LEITURA",
        "HISTOGRAM":          "FIM-HISTOGRAMA",
        "DEFINE SUBROUTINE":  "FIM-SUBROTINA",
        "DO":                 "FIM-FAÇA",
    }
    return closers.get(opener_keyword, "")


# ── Ponto de entrada do emitter ────────────────────────────────────────────────

def emit(program: Program) -> str:
    """Gera o pseudocódigo completo a partir de um Program.

    O corpo principal é emitido primeiro; as subrotinas são agrupadas
    em uma seção separada ao final, precedida de um separador visual.

    Args:
        program: resultado do parser.parse().

    Returns:
        String com o pseudocódigo algorítmico em português.

    Example:
        >>> from nat2algo.lexer import tokenize_lines
        >>> from nat2algo.parser import parse
        >>> from nat2algo.emitter import emit
        >>> prog = parse(tokenize_lines(["WRITE 'Olá'\\n", "END\\n"]))
        >>> print(emit(prog))
        ESCREVER 'Olá'
        FIM
    """
    lines: list[str] = []

    lines.extend(_emit_nodes(program.body, depth=0))

    if program.subroutines:
        lines.append("")
        lines.append("─" * 60)
        lines.append("SUBROTINAS")
        lines.append("─" * 60)
        for sub in program.subroutines:
            lines.append("")
            lines.extend(_emit_nodes([sub], depth=0))

    # Remove múltiplas linhas em branco consecutivas
    cleaned = _collapse_blank_lines(lines)
    return "\n".join(cleaned)


def _collapse_blank_lines(lines: list[str]) -> list[str]:
    """Garante no máximo uma linha em branco consecutiva."""
    result: list[str] = []
    prev_blank = False
    for line in lines:
        is_blank = not line.strip()
        if is_blank and prev_blank:
            continue
        result.append(line)
        prev_blank = is_blank
    return result
