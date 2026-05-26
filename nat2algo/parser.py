"""
Parser: constrói uma AST de ASTNode a partir da lista de tokens do lexer.

Responsabilidade: agrupar tokens em blocos aninhados (IF…END-IF,
FIND…END-FIND, etc.) e separar subroutines do corpo principal.

Uso:
    from nat2algo.lexer import tokenize_lines
    from nat2algo.parser import parse

    tokens = tokenize_lines(lines)
    program = parse(tokens)
    # program.body  → instruções do programa principal
    # program.subroutines → lista de ASTNode DEFINE SUBROUTINE
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterator

from nat2algo.lexer import Token
from nat2algo.mappings import BLOCK_OPENERS, BLOCK_CLOSERS


@dataclass
class ASTNode:
    """Nó da árvore sintática abstrata.

    Atributos:
        keyword:  keyword Natural do nó (ex: 'IF', 'FIND', 'MOVE').
        args:     argumentos da instrução (resto da linha).
        line_no:  linha de origem no arquivo.
        children: filhos do nó (para blocos estruturados).
    """

    keyword: str
    args: str
    line_no: int
    children: list[ASTNode] = field(default_factory=list)


@dataclass
class Program:
    """Resultado do parse de um programa Natural completo.

    Atributos:
        body:        nós do programa principal (sem subroutines inline).
        subroutines: cada DEFINE SUBROUTINE como um ASTNode com filhos.
    """

    body: list[ASTNode] = field(default_factory=list)
    subroutines: list[ASTNode] = field(default_factory=list)


class ParseError(Exception):
    """Erro de estrutura no código Natural com indicação de linha."""

    def __init__(self, msg: str, line_no: int) -> None:
        super().__init__(f"Linha {line_no}: {msg}")
        self.line_no = line_no


def parse(tokens: list[Token]) -> Program:
    """Constrói um Program a partir da lista de tokens.

    Estratégia em duas passagens:
    1. Extrai DEFINE SUBROUTINE...END-SUBROUTINE do fluxo de tokens,
       substituindo-os por um marcador, para que o END do programa
       não encerre a leitura antes das subroutines serem coletadas.
    2. Faz o parse do restante (corpo principal) normalmente.

    Args:
        tokens: saída do lexer.tokenize_lines().

    Returns:
        Program com corpo principal e subroutines separadas.

    Raises:
        ParseError: quando um bloco não é fechado corretamente.

    Example:
        >>> from nat2algo.lexer import tokenize_lines
        >>> toks = tokenize_lines(["IF #X > 0\\n", "WRITE 'ok'\\n", "END-IF\\n"])
        >>> prog = parse(toks)
        >>> prog.body[0].keyword
        'IF'
        >>> prog.body[0].children[0].keyword
        'WRITE'
    """
    program = Program()
    body_tokens, subroutine_groups = _split_subroutines(tokens)

    for group in subroutine_groups:
        sub_iter = iter(group)
        opener = next(sub_iter)
        sub_node = _parse_subroutine(opener, sub_iter)
        program.subroutines.append(sub_node)

    iterator = iter(body_tokens)
    body_nodes = _parse_block(iterator, stop_keywords=frozenset({"END"}))
    # END é incluído no body para que o emitter gere 'FIM'
    program.body = body_nodes

    return program


def _split_subroutines(
    tokens: list[Token],
) -> tuple[list[Token], list[list[Token]]]:
    """Separa tokens de subroutines do corpo principal.

    Retorna (body_tokens, [[sub1_tokens], [sub2_tokens], ...]).
    Tokens entre DEFINE SUBROUTINE e END-SUBROUTINE são removidos do body.
    """
    body: list[Token] = []
    subroutines: list[list[Token]] = []
    i = 0
    while i < len(tokens):
        tok = tokens[i]
        if tok.keyword == "DEFINE SUBROUTINE":
            group: list[Token] = [tok]
            i += 1
            while i < len(tokens) and tokens[i].keyword != "END-SUBROUTINE":
                group.append(tokens[i])
                i += 1
            if i < len(tokens):  # inclui END-SUBROUTINE
                group.append(tokens[i])
                i += 1
            subroutines.append(group)
        else:
            body.append(tok)
            i += 1
    return body, subroutines


def _parse_block(
    iterator: Iterator[Token],
    stop_keywords: frozenset[str],
) -> list[ASTNode]:
    """Lê tokens até encontrar uma stop_keyword ou exaurir o iterador.

    Esta função é chamada recursivamente para cada bloco aninhado.
    """
    nodes: list[ASTNode] = []

    for token in iterator:
        if token.keyword in stop_keywords:
            # Adiciona o token fechador como nó sentinela sem filhos
            nodes.append(ASTNode(token.keyword, token.args, token.line_no))
            return nodes

        if token.keyword == "DEFINE DATA":
            data_node = _parse_define_data(token, iterator)
            nodes.append(data_node)
            continue

        if token.keyword == "IF":
            block_node = _parse_nested_block(token, iterator)
            nodes.append(block_node)
            continue

        if token.keyword in BLOCK_OPENERS:
            block_node = _parse_nested_block(token, iterator)
            nodes.append(block_node)
            continue

        # Nó folha (instrução simples)
        nodes.append(ASTNode(token.keyword, token.args, token.line_no))

    return nodes


def _parse_define_data(opener: Token, iterator: Iterator[Token]) -> ASTNode:
    """Lê o bloco DEFINE DATA até END-DEFINE e retorna um ASTNode com filhos.

    O lexer tokeniza 'DEFINE DATA LOCAL' como keyword='DEFINE DATA', args='LOCAL'.
    Aqui criamos um nó filho LOCAL/GLOBAL/PARAMETER a partir dos args do opener.
    """
    data_node = ASTNode(opener.keyword, "", opener.line_no)
    scope_kws = {"LOCAL", "GLOBAL", "PARAMETER"}

    # Se o scope vem junto na mesma linha (ex: args='LOCAL')
    if opener.args.strip().upper() in scope_kws:
        scope_kw = opener.args.strip().upper()
        data_node.children.append(ASTNode(scope_kw, "", opener.line_no))

    for token in iterator:
        if token.keyword == "END-DEFINE":
            break
        data_node.children.append(ASTNode(token.keyword, token.args, token.line_no))
    return data_node


def _parse_nested_block(
    opener: Token,
    iterator: Iterator[Token],
) -> ASTNode:
    """Cria um ASTNode para o bloco aberto por `opener` e preenche seus filhos.

    IF é tratado via _parse_if_children (lida com ELSE).
    Os demais blocos usam _closer_for para encontrar o fechador.
    """
    node = ASTNode(opener.keyword, opener.args, opener.line_no)

    if opener.keyword == "IF":
        node.children = _parse_if_children(iterator, opener.line_no)
        return node

    closer = _closer_for(opener.keyword, opener.line_no)
    node.children = _parse_block(iterator, stop_keywords=frozenset({closer}))
    # Remove o token fechador da lista de filhos (é sentinela)
    node.children = [c for c in node.children if c.keyword != closer]

    return node


def _parse_if_children(
    iterator: Iterator[Token],
    if_line_no: int,
) -> list[ASTNode]:
    """Lê filhos de um bloco IF, criando um filho ELSE se houver."""
    then_children = _parse_block(
        iterator, stop_keywords=frozenset({"ELSE", "END-IF"})
    )

    # O último elemento é o sentinela (ELSE ou END-IF)
    if not then_children:
        raise ParseError("Bloco IF sem conteúdo ou sem END-IF", if_line_no)

    sentinel = then_children[-1]
    then_children = then_children[:-1]

    if sentinel.keyword == "END-IF":
        return then_children

    # sentinel.keyword == "ELSE"
    else_node = ASTNode("ELSE", "", sentinel.line_no)
    else_children = _parse_block(iterator, stop_keywords=frozenset({"END-IF"}))
    # Remove END-IF sentinela
    else_node.children = [c for c in else_children if c.keyword != "END-IF"]

    return then_children + [else_node]


def _parse_subroutine(opener: Token, iterator: Iterator[Token]) -> ASTNode:
    """Lê o corpo de uma DEFINE SUBROUTINE até END-SUBROUTINE."""
    sub_node = ASTNode(opener.keyword, opener.args, opener.line_no)
    sub_node.children = _parse_block(
        iterator, stop_keywords=frozenset({"END-SUBROUTINE"})
    )
    sub_node.children = [
        c for c in sub_node.children if c.keyword != "END-SUBROUTINE"
    ]
    return sub_node


def _closer_for(opener_keyword: str, line_no: int) -> str:
    """Retorna a keyword fechadora correspondente ao abridor.

    Raises:
        ParseError: se não houver fechador definido para o abridor.
    """
    mapping: dict[str, str] = {
        "FOR":       "END-FOR",
        "REPEAT":    "END-REPEAT",
        "FIND":      "END-FIND",
        "READ":      "END-READ",
        "HISTOGRAM": "END-HISTOGRAM",
    }
    closer = mapping.get(opener_keyword)
    if closer is None:
        raise ParseError(
            f"Keyword '{opener_keyword}' não possui fechador definido.",
            line_no,
        )
    return closer
