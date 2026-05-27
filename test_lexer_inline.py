from nat2algo.lexer import _match_keyword

def _extract_inline_stmt(text: str):
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
                if kw in {"REINPUT", "WRITE", "DISPLAY", "PRINT", "MOVE", "COMPUTE", "ADD", "SUBTRACT", "MULTIPLY", "DIVIDE", "RESET", "DO", "ESCAPE TOP", "ESCAPE BOTTOM", "STOP", "TERMINATE", "PERFORM", "CALL"}:
                    cond = text[:i].strip()
                    if cond.upper().endswith(" THEN"):
                        cond = cond[:-5].strip()
                    return cond, kw, substr[len(kw):].strip()
    return None

print(_extract_inline_stmt("SAT-COD-INSCR-CGCTE = 0 REINPUT 'Informe o cgcte' ALARM"))
print(_extract_inline_stmt("#DATA-TRANSF = 0 DO"))
