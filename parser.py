import ply.yacc as yacc
from pllm_ast import *
from lexer import lexer, tokens

# 优先级规则（用于解析二元操作符）
precedence = (
    ('left', 'PLUS', 'MINUS'),
    ('left', 'TIMES', 'DIVIDE', 'MOD'),
    ('left', 'EQ', 'NEQ', 'GT', 'LT', 'LE', 'GE'),
)

