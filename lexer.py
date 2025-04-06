import ply.lex as lex

# -------------------------------
# 关键字和保留字
# -------------------------------
reserved = {
    "agent": "AGENT",
    "input": "INPUT",
    "output": "OUTPUT",
    "model": "MODEL",
    "chat": "CHAT",
    "connect": "CONNECT",
    "memory": "MEMORY",
    "global": "GLOBAL",
    "record": "TYPE_RECORD",
    "tuple": "TYPE_TUPLE",
    "list": "TYPE_LIST",
    "def": "DEF",
    "for": "FOR",
    "in": "IN",
    "if": "IF",
    "elif": "ELIF",
    "else": "ELSE",
    "while": "WHILE",
    "str": "TYPE_STR",
    "int": "TYPE_INT",
    "float": "TYPE_FLOAT",
    "bool": "TYPE_BOOL"
}

# -------------------------------
# Token 列表
# -------------------------------
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
    "DOT",
    "PLUS", "MINUS", "TIMES", "DIVIDE", "MOD",
    "EQ", "NEQ", "LT", "GT", "LE", "GE",
    "COMMA", "SEMICOLON"
] + list(reserved.values())

# -------------------------------
# 正则定义
# -------------------------------
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
t_SEMICOLON = r";"

# -------------------------------
# 字面值
# -------------------------------
def t_TRIPLE_STRING(t):
    r'"""(?:.|\n)*?"""'
    return t

def t_STRING(t):
    r'"[^"\n]*"'
    return t

def t_NUMBER(t):
    r'\d+(\.\d+)?'
    t.value = float(t.value) if '.' in t.value else int(t.value)
    return t

def t_IDENTIFIER(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    t.type = reserved.get(t.value, 'IDENTIFIER')
    return t

# -------------------------------
# 缩进处理
# -------------------------------
indent_stack = [0]

def t_NEWLINE(t):
    r'\n[ \t]*'
    t.lexer.lineno += 1
    spaces = len(t.value) - 1  # count spaces after \n
    next_indent = spaces

    # Peek next char; if it's a newline or comment, skip it
    pos = t.lexer.lexpos
    if pos >= len(t.lexer.lexdata):
        return None
    next_char = t.lexer.lexdata[pos]
    if next_char == '\n' or next_char == '#':
        return None

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
        return None  # same indent, no token

# -------------------------------
# 处理 DEDENT Token 插入
# -------------------------------
def lexer_token():
    if hasattr(lexer, 'dedent_tokens') and lexer.dedent_tokens:
        return lexer.dedent_tokens.pop(0)
    else:
        return lexer.token_original()

# -------------------------------
# 忽略空格和注释
# -------------------------------
t_ignore = ' '
t_ignore_COMMENT = r'\#.*'

def t_error(t):
    print(f"Illegal character {t.value[0]!r} at line {t.lineno}")
    t.lexer.skip(1)

# -------------------------------
# 构建词法分析器
# -------------------------------
lexer = lex.lex()
lexer.token_original = lexer.token
lexer.token = lexer_token