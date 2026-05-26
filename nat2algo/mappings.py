"""
Tabela de mapeamento de palavras-chave Natural/Adabas → texto algorítmico em português.

Cada entrada mapeia uma keyword (uppercase) para um template de pseudocódigo.
Templates com '{args}' recebem o restante da linha original como argumento.
"""

from typing import Final

# ── Condicionais ───────────────────────────────────────────────────────────────
CONDITIONAL: Final[dict[str, str]] = {
    "IF":      "SE {args} ENTÃO",
    "ELSE":    "SENÃO",
    "END-IF":  "FIM-SE",
}

# ── Laços ─────────────────────────────────────────────────────────────────────
LOOP: Final[dict[str, str]] = {
    "FOR":      "PARA {args} FAÇA",
    "END-FOR":  "FIM-PARA",
    "REPEAT":   "REPETIR",
    "END-REPEAT": "FIM-REPETIR",
    "LOOP":     "FIM-LAÇO",          # modo Reporting: fecha o laço corrente
}

# ── Acesso a banco (Adabas) ───────────────────────────────────────────────────
DB_ACCESS: Final[dict[str, str]] = {
    "FIND":           "BUSCAR em {args}",
    "END-FIND":       "FIM-BUSCA",
    "READ":           "LER {args}",
    "END-READ":       "FIM-LEITURA",
    "HISTOGRAM":      "HISTOGRAMA {args}",
    "END-HISTOGRAM":  "FIM-HISTOGRAMA",
    "STORE":          "ARMAZENAR {args}",
    "UPDATE":         "ATUALIZAR {args}",
    "DELETE":         "EXCLUIR {args}",
    "END-TRANSACTION": "FIM-TRANSAÇÃO",
    "BACKOUT TRANSACTION": "DESFAZER TRANSAÇÃO",
    "GET":            "OBTER {args}",
}

# ── Atribuição e aritmética ───────────────────────────────────────────────────
ASSIGNMENT: Final[dict[str, str]] = {
    # MOVE A TO B  →  B ← A  (tratamento especial no emitter)
    "MOVE":         "__MOVE__",
    "COMPUTE":      "__COMPUTE__",
    # ADD val TO var  →  var ← var + val
    "ADD":          "__ADD__",
    "SUBTRACT":     "__SUBTRACT__",
    "MULTIPLY":     "__MULTIPLY__",
    "DIVIDE":       "__DIVIDE__",
    "RESET":        "ZERAR {args}",
}

# ── Saída ─────────────────────────────────────────────────────────────────────
OUTPUT: Final[dict[str, str]] = {
    "WRITE":   "ESCREVER {args}",
    "DISPLAY": "EXIBIR {args}",
    "PRINT":   "IMPRIMIR {args}",
}

# ── Entrada ───────────────────────────────────────────────────────────────────
INPUT_STMT: Final[dict[str, str]] = {
    "INPUT": "LER {args}",
}

# ── Chamada de subrotinas e programas externos ─────────────────────────────────
CALL: Final[dict[str, str]] = {
    "PERFORM": "EXECUTAR {args}",
    "CALL":    "CHAMAR {args}",
    "FETCH":   "CARREGAR PROGRAMA {args}",
}

# ── Definição de subrotinas ────────────────────────────────────────────────────
SUBROUTINE: Final[dict[str, str]] = {
    "DEFINE SUBROUTINE": "SUBROTINA {args}",
    "END-SUBROUTINE":    "FIM-SUBROTINA",
}

# ── Fluxo de controle ─────────────────────────────────────────────────────────
FLOW: Final[dict[str, str]] = {
    "ESCAPE TOP":    "SAIR DO TOPO DO LAÇO",
    "ESCAPE BOTTOM": "SAIR DO FUNDO DO LAÇO",
    "STOP":          "PARAR",
    "TERMINATE":     "ENCERRAR",
    "END":           "FIM",
}

# ── Bloco DEFINE DATA ─────────────────────────────────────────────────────────
DEFINE_DATA: Final[dict[str, str]] = {
    "DEFINE DATA": "__DEFINE_DATA__",
    "END-DEFINE":  "__END_DEFINE__",
    "LOCAL":       "VARIÁVEIS LOCAIS:",
    "GLOBAL":      "VARIÁVEIS GLOBAIS:",
    "PARAMETER":   "PARÂMETROS:",
}

# ── Lookup global: keyword → template ─────────────────────────────────────────
# A ordem importa para prefixos compostos (ex: "ESCAPE TOP" antes de "ESCAPE").
ALL_MAPPINGS: Final[dict[str, str]] = {
    **DEFINE_DATA,
    **SUBROUTINE,
    **CONDITIONAL,
    **LOOP,
    **DB_ACCESS,
    **ASSIGNMENT,
    **OUTPUT,
    **INPUT_STMT,
    **CALL,
    **FLOW,
}

# Keywords que abrem um bloco filho na AST
BLOCK_OPENERS: Final[frozenset[str]] = frozenset({
    "IF", "ELSE",
    "FOR", "REPEAT",
    "FIND", "READ", "HISTOGRAM",
    "DEFINE SUBROUTINE",
})

# Keywords que fecham um bloco
BLOCK_CLOSERS: Final[frozenset[str]] = frozenset({
    "END-IF", "ELSE",
    "END-FOR", "END-REPEAT", "LOOP",
    "END-FIND", "END-READ", "END-HISTOGRAM",
    "END-SUBROUTINE",
    "END-DEFINE",
    "END",
})

# Keywords que encerram o escopo de ELSE (tratadas pelo parser)
ELSE_CLOSERS: Final[frozenset[str]] = frozenset({"END-IF"})
