import ply.yacc as yacc
from pllm_ast import *
from lexer import lexer, tokens

# 优先级规则（用于解析二元操作符）
precedence = (
    ('left', 'PLUS', 'MINUS'),
    ('left', 'TIMES', 'DIVIDE', 'MOD'),
    ('left', 'EQ', 'NEQ', 'GT', 'LT', 'LE', 'GE'),
)

def p_program(p):
    '''program : global_block program_body
               | program_body'''
    if len(p) == 3:
        p[0] = Program(global_block=p[1], body=p[2])
    else:
        p[0] = Program(global_block=None, body=p[1])

def p_program_body(p):
    '''program_body : statement program_body
                    | agent_def program_body
                    | connect_block program_body
                    | func_def program_body
                    | empty'''
    if len(p) == 3:
        p[0] = [p[1]] + p[2]
    else:
        p[0] = []

def p_global_block(p):
    '''global_block : GLOBAL COLON INDENT var_decl_list DEDENT'''
    p[0] = GlobalBlock(variables=p[4])