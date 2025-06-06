"""
File name: pllm_lexer.py
Description: This file contains the lexer for the PLLM.
Author: Sun Ao
Last edited: 2025-6-3
"""

import ply.lex as lex

"""
Reserved keywords and tokens.
"""
reserved = {
    "agent": "AGENT",
    "input": "INPUT",
    "output": "OUTPUT",
    "model": "MODEL",
    "chat": "CHAT",
    "connect": "CONNECT",
    "record": "TYPE_RECORD",
    "tuple": "TYPE_TUPLE",
    "list": "TYPE_LIST",
    "unit": "TYPE_UNIT",
    "union": "TYPE_UNION",
    "fun": "FUN",
    "for": "FOR",
    "in": "IN",
    "if": "IF",
    "else": "ELSE",
    "while": "WHILE",
    "str": "TYPE_STR",
    "int": "TYPE_INT",
    "float": "TYPE_FLOAT",
    "bool": "TYPE_BOOL",
    "return": "RETURN",
    "break": "BREAK",
    "continue": "CONTINUE",
    "type": "TYPE"
}

"""
Token list.
"""
tokens = [
    "IDENTIFIER",
    "NUMBER",
    "STRING",
    "TRIPLE_STRING",
    "NEWLINE",
    "INDENT",
    "DEDENT",
    "COLON",
    "EQUALS",
    "ARROW",        # ->
    "LPAREN", "RPAREN",
    "LBRACE", "RBRACE",
    "LBRACKET", "RBRACKET",
    "DOT",
    "PLUS", "MINUS", "TIMES", "DIVIDE", "MOD",
    "EQ", "NEQ", "LT", "GT", "LE", "GE",
    "COMMA"
] + list(reserved.values())

"""
Regular expressions for tokens.
"""
t_COLON = r":"
t_EQUALS = r"="
t_ARROW = r"->"
t_LPAREN = r"\("
t_RPAREN = r"\)"
t_LBRACE = r"\{"
t_RBRACE = r"\}"
t_DOT = r"\."
t_PLUS = r"\+"
t_MINUS = r"-"
t_TIMES = r"\*"
t_DIVIDE = r"/"
t_MOD = r"%"
t_EQ = r"=="
t_NEQ = r"!="
t_LT = r"<"
t_GT = r">"
t_LE = r"<="
t_GE = r">="
t_COMMA = r","
t_LBRACKET = r"\["
t_RBRACKET = r"\]"

"""
Literal for immerdiate values.
"""
def t_TRIPLE_STRING(t):
    r'"""(?:.|\n)*?"""'
    t.lexer.lineno += t.value.count('\n')
    return t

def t_STRING(t):
    r'"[^"\n]*"'
    return t

def t_NUMBER(t):
    r'\d+(\.\d+)?'
    t.value = float(t.value) if '.' in t.value else int(t.value)
    return t

def t_BOOL(t):
    r'(True|False)'
    t.value = True if t.value == 'True' else False
    return t

def t_IDENTIFIER(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    t.type = reserved.get(t.value, 'IDENTIFIER')
    return t

"""
Indentation handling.
"""
indent_stack = [0]

def t_NEWLINE(t):
    r'\n[ \t]*'
    t.lexer.lineno += 1
    spaces = len(t.value) - 1
    next_indent = spaces

    pos = t.lexer.lexpos
    while pos < len(t.lexer.lexdata) and t.lexer.lexdata[pos] in '\n\r':
        t.lexer.lineno += 1
        t.lexer.lexpos += 1
        pos += 1
    if pos >= len(t.lexer.lexdata):
        return None
    next_char = t.lexer.lexdata[pos]
    current_indent = indent_stack[-1]
    if next_indent > current_indent:
        indent_stack.append(next_indent)
        t.type = 'INDENT'
        return t
    elif next_indent < current_indent:
        t.type = 'DEDENT'
        dedent_tokens = []
        while indent_stack and next_indent < indent_stack[-1]:
            indent_stack.pop()
            tok = lex.LexToken()
            tok.type = 'DEDENT'
            tok.value = ''
            tok.lineno = t.lineno
            tok.lexpos = t.lexpos
            dedent_tokens.append(tok)
        t.lexer.dedent_tokens = dedent_tokens
        return t.lexer.dedent_tokens.pop(0)
    else:
        return None
"""
Custom token function to handle indentation and dedentation.
"""
def lexer_token():
    """Get the next token, handling indentation and dedentation."""
    if hasattr(lexer, 'dedent_tokens') and lexer.dedent_tokens:
        return lexer.dedent_tokens.pop(0)
    
    token = lexer.token_original()
    
    
    if token is None and len(indent_stack) > 1:
        dedent_tokens = []
        while len(indent_stack) > 1:
            indent_stack.pop()
            tok = lex.LexToken()
            tok.type = 'DEDENT'
            tok.value = ''
            tok.lineno = lexer.lineno
            tok.lexpos = lexer.lexpos
            dedent_tokens.append(tok)
        
        lexer.dedent_tokens = dedent_tokens 
        return lexer.dedent_tokens.pop(0)
    
    return token

"""
Ignore whitespace and comments.
"""
t_ignore = ' '
t_ignore_COMMENT = r'\#.*'

def t_error(t):
    print(f"Illegal character {t.value[0]!r} at line {t.lineno}")
    t.lexer.skip(1)

"""
Initialize the lexer.
"""
lexer = lex.lex()
lexer.token_original = lexer.token
lexer.token = lexer_token
lexer.lineno = 1