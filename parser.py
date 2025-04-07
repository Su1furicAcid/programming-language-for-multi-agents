import ply.yacc as yacc
from pllm_ast import *
from lexer import lexer, tokens

# 优先级规则
precedence = (
    ('left', 'PLUS', 'MINUS'),
    ('left', 'TIMES', 'DIVIDE', 'MOD'),
    ('left', 'EQ', 'NEQ', 'GT', 'LT', 'LE', 'GE'),
)

# program ::= global_block? program_body
def p_program(p):
    '''program : global_block program_body
               | program_body'''
    if len(p) == 3:
        p[0] = Program(global_block=p[1], body=p[2])
    else:
        p[0] = Program(global_block=None, body=p[1])

# program_body ::= (statement | agent_def | connect_block | func_def)+
def p_program_body(p):
    '''program_body : program_body_item program_body
                    | program_body_item'''
    if len(p) == 3:
        p[0] = [p[1]] + p[2]
    else:
        p[0] = [p[1]]

def p_program_body_item(p):
    '''program_body_item : statement
                         | agent_def
                         | connect_block
                         | func_def'''
    p[0] = p[1]

# global_block ::= "global" ":" INDENT var_decl_list DEDENT
def p_global_block(p):
    '''global_block : GLOBAL COLON INDENT var_decl_list DEDENT'''
    p[0] = GlobalBlock(variables=p[4])

# var_decl_list ::= var_decl+
def p_var_decl_list(p):
    '''var_decl_list : var_decl var_decl_list
                     | var_decl'''
    if len(p) == 3:
        p[0] = [p[1]] + p[2]
    else:
        p[0] = [p[1]]

# var_decl ::= IDENTIFIER (":" type)? ("=" expr)?
def p_var_decl(p):
    '''var_decl : IDENTIFIER COLON type EQUALS expr
                | IDENTIFIER COLON type
                | IDENTIFIER EQUALS expr
                | IDENTIFIER'''
    if len(p) == 6:
        p[0] = VarDecl(name=p[1], var_type=p[3], value=p[5])
    elif len(p) == 4:
        if p[2] == ':':
            p[0] = VarDecl(name=p[1], var_type=p[3])
        else:
            p[0] = VarDecl(name=p[1], value=p[3])
    else:
        p[0] = VarDecl(name=p[1])

# type ::= base_type | list_type | record_type
def p_type(p):
    '''type : base_type
            | list_type
            | record_type'''
    p[0] = p[1]

# base_type ::= "str" | "int" | "float" | "bool" | IDENTIFIER
def p_base_type(p):
    '''base_type : TYPE_STR
                 | TYPE_INT
                 | TYPE_FLOAT
                 | TYPE_BOOL'''
    p[0] = BaseType(name=p[1])

# list_type ::= "list" "[" type "]"
def p_list_type(p):
    '''list_type : TYPE_LIST LBRACE type RBRACE'''
    p[0] = ListType(element_type=p[3])

# record_type ::= "record" "{" field_decl_list "}"
def p_record_type(p):
    '''record_type : TYPE_RECORD LBRACE field_decl_list RBRACE'''
    p[0] = RecordType(fields=p[3])

def p_field_decl_list(p):
    '''field_decl_list : field_decl field_decl_list
                       | field_decl'''
    if len(p) == 3:
        p[0] = [p[1]] + p[2]
    else:
        p[0] = [p[1]]

def p_field_decl(p):
    '''field_decl : IDENTIFIER COLON type'''
    p[0] = FieldDecl(name=p[1], field_type=p[3])

# agent_def ::= "agent" IDENTIFIER ":" INDENT agent_body DEDENT
def p_agent_def(p):
    '''agent_def : AGENT IDENTIFIER COLON INDENT agent_body DEDENT'''
    p[0] = AgentDef(name=p[2], body=p[5])

# agent_body ::= (input_block | output_block | memory_block | model_block | statement | chat_block)+
def p_agent_body(p):
    '''agent_body : agent_body_item agent_body
                  | agent_body_item'''
    if len(p) == 3:
        p[0] = [p[1]] + p[2]
    else:
        p[0] = [p[1]]

def p_agent_body_item(p):
    '''agent_body_item : input_block
                       | output_block
                       | memory_block
                       | model_block
                       | statement
                       | chat_block'''
    p[0] = p[1]

# input_block ::= "input" ":" INDENT var_decl_list DEDENT
def p_input_block(p):
    '''input_block : INPUT COLON INDENT var_decl_list DEDENT'''
    p[0] = InputBlock(variables=p[4])

# output_block ::= "output" ":" INDENT var_decl_list DEDENT
def p_output_block(p):
    '''output_block : OUTPUT COLON INDENT var_decl_list DEDENT'''
    p[0] = OutputBlock(variables=p[4])

# memory_block ::= "memory" ":" INDENT var_decl_list DEDENT
def p_memory_block(p):
    '''memory_block : MEMORY COLON INDENT var_decl_list DEDENT'''
    p[0] = MemoryBlock(variables=p[4])

# model_block ::= "model" ":" STRING
def p_model_block(p):
    '''model_block : MODEL COLON STRING'''
    p[0] = ModelBlock(model_name=p[3])

# chat_block ::= "chat" IDENTIFIER ":" TRIPLE_STRING
def p_chat_block(p):
    '''chat_block : CHAT IDENTIFIER COLON TRIPLE_STRING'''
    p[0] = ChatBlock(name=p[2], template=p[4])

# connect_block ::= "connect" ":" INDENT connection+ DEDENT
def p_connect_block(p):
    '''connect_block : CONNECT COLON INDENT connection_list DEDENT'''
    p[0] = ConnectBlock(connections=p[4])

def p_connection_list(p):
    '''connection_list : connection connection_list
                       | connection'''
    if len(p) == 3:
        p[0] = [p[1]] + p[2]
    else:
        p[0] = [p[1]]

# connection ::= IDENTIFIER ":" type agent_ref "->" agent_ref
def p_connection(p):
    '''connection : IDENTIFIER COLON type agent_ref ARROW agent_ref'''
    p[0] = Connection(name=p[1], conn_type=p[3], source=p[4], target=p[6])

# agent_ref ::= IDENTIFIER ("." IDENTIFIER)*
def p_agent_ref(p):
    '''agent_ref : IDENTIFIER agent_ref_tail'''
    p[0] = AgentRef(parts=[p[1]] + p[2])

def p_agent_ref_tail(p):
    '''agent_ref_tail : DOT IDENTIFIER agent_ref_tail
                      | empty'''
    if len(p) == 4:
        p[0] = [p[2]] + p[3]
    else:
        p[0] = []

# func_def ::= "def" IDENTIFIER "(" param_list? ")" (":" type)? ":" INDENT stmt_block DEDENT
def p_func_def(p):
    '''func_def : DEF IDENTIFIER LPAREN param_list RPAREN COLON type COLON stmt_block
                | DEF IDENTIFIER LPAREN param_list RPAREN COLON stmt_block'''
    if len(p) == 11:
        p[0] = FuncDef(name=p[2], params=p[4], return_type=p[7], stmt_body=p[9])
    else:
        p[0] = FuncDef(name=p[2], params=p[4], stmt_body=p[7])

# param_list ::= param_decl ("," param_decl)*
def p_param_list(p):
    '''param_list : param_decl param_list_tail
                  | empty'''
    if len(p) == 3:
        p[0] = [p[1]] + p[2]
    else:
        p[0] = []

def p_param_list_tail(p):
    '''param_list_tail : COMMA param_decl param_list_tail
                       | empty'''
    if len(p) == 4:
        p[0] = [p[2]] + p[3]
    else:
        p[0] = []

# param_decl ::= var_decl
def p_param_decl(p):
    '''param_decl : var_decl'''
    p[0] = p[1]

# stmt_block ::= INDENT statement+ DEDENT
def p_stmt_block(p):
    '''stmt_block : INDENT statement_list DEDENT'''
    p[0] = p[2]

def p_statement_list(p):
    '''statement_list : statement statement_list
                      | statement'''
    if len(p) == 3:
        p[0] = [p[1]] + p[2]
    else:
        p[0] = [p[1]]

# statement ::= for_stmt | if_stmt | while_stmt | assign_stmt | break_stmt | continue_stmt | return_stmt
def p_statement(p):
    '''statement : for_stmt
                 | if_stmt
                 | while_stmt
                 | assign_stmt
                 | break_stmt
                 | continue_stmt
                 | return_stmt'''
    p[0] = p[1]

# assign_stmt ::= IDENTIFIER (":" type)? "=" expr
def p_assign_stmt(p):
    '''assign_stmt : IDENTIFIER COLON type EQUALS expr
                   | IDENTIFIER EQUALS expr'''
    if len(p) == 5:
        p[0] = AssignStmt(name=p[1], var_type=p[3], value=p[5])
    else:
        p[0] = AssignStmt(name=p[1], value=p[3])

# return_stmt ::= "return" expr
def p_return_stmt(p):
    '''return_stmt : RETURN expr'''
    p[0] = ReturnStmt(value=p[2])

# for_stmt ::= "for" IDENTIFIER "in" expr ":" stmt_block
def p_for_stmt(p):
    '''for_stmt : FOR IDENTIFIER IN expr COLON stmt_block'''
    p[0] = ForStmt(var_name=p[2], iterable=p[4], body=p[6])

# break_stmt ::= "break"
def p_break_stmt(p):
    '''break_stmt : BREAK'''
    p[0] = BreakStmt()

# continue_stmt ::= "continue"
def p_continue_stmt(p):
    '''continue_stmt : CONTINUE'''
    p[0] = ContinueStmt()

# if_stmt ::= "if" expr ":" stmt_block "else" ":" stmt_block?
def p_if_stmt(p):
    '''if_stmt : IF expr COLON stmt_block ELSE COLON stmt_block
               | IF expr COLON stmt_block'''
    if len(p) == 8:
        p[0] = IfStmt(condition=p[2], body=p[4], else_block=p[7])
    else:
        p[0] = IfStmt(condition=p[2], body=p[4], else_block=None)

# while_stmt ::= "while" expr ":" stmt_block
def p_while_stmt(p):
    '''while_stmt : WHILE expr COLON stmt_block'''
    p[0] = WhileStmt(condition=p[2], body=p[4])

# expr ::= expr_head bin_op expr_tail | expr_head
def p_expr(p):
    '''expr : expr_head bin_op expr_tail
            | expr_head'''
    if p[2] is not None:
        p[0] = BinaryOp(left=p[1], op=p[2].op, right=p[2])
    else:
        p[0] = p[1]

# expr_head ::= atom | list_expr | record_expr | field_access | func_call
def p_expr_head(p):
    '''expr_head : atom
                 | list_expr
                 | record_expr
                 | field_access
                 | func_call'''
    p[0] = p[1]

# expr_tail ::= expr
def p_expr_tail(p):
    '''expr_tail : expr'''
    p[0] = p[1]

# atom ::= IDENTIFIER | STRING | NUMBER
def p_atom(p):
    '''atom : IDENTIFIER
            | STRING
            | NUMBER'''
    p[0] = Atom(value=p[1])

# list_expr ::= "[" (expr ("," expr)*)? "]"
def p_list_expr(p):
    '''list_expr : LBRACE list_elements RBRACE'''
    p[0] = ListExpr(elements=p[2])

def p_list_elements(p):
    '''list_elements : expr list_elements_tail
                     | expr'''
    if len(p) == 3:
        p[0] = [p[1]] + p[2]
    else:
        p[0] = [p[1]]

def p_list_elements_tail(p):
    '''list_elements_tail : COMMA expr list_elements_tail
                          | COMMA expr'''
    if len(p) == 4:
        p[0] = [p[2]] + p[3]
    else:
        p[0] = [p[2]]

# record_expr ::= "{" field_assign ("," field_assign)* "}"
def p_record_expr(p):
    '''record_expr : LBRACE record_elements RBRACE'''
    p[0] = RecordExpr(fields=p[2])

def p_record_elements(p):
    '''record_elements : field_assign record_elements_tail
                       | field_assign'''
    if len(p) == 3:
        p[0] = [p[1]] + p[2]
    else:
        p[0] = [p[1]]

def p_record_elements_tail(p):
    '''record_elements_tail : COMMA field_assign record_elements_tail
                            | COMMA field_assign'''
    if len(p) == 4:
        p[0] = [p[2]] + p[3]
    else:
        p[0] = [p[2]]

# field_assign ::= IDENTIFIER "=" expr
def p_field_assign(p):
    '''field_assign : IDENTIFIER EQUALS expr'''
    p[0] = FieldAssign(name=p[1], value=p[3])

# field_access ::= IDENTIFIER "." IDENTIFIER
def p_field_access(p):
    '''field_access : IDENTIFIER DOT IDENTIFIER'''
    p[0] = FieldAccess(obj=p[1], field=p[3])

# func_call ::= IDENTIFIER "(" arg_list? ")"
def p_func_call(p):
    '''func_call : IDENTIFIER LPAREN arg_list RPAREN'''
    p[0] = FuncCall(func_name=p[1], args=p[3])

# arg_list ::= expr ("," expr)*
def p_arg_list(p):
    '''arg_list : expr arg_list_tail
                | empty'''
    if len(p) == 3:
        p[0] = [p[1]] + p[2]
    else:
        p[0] = []

def p_arg_list_tail(p):
    '''arg_list_tail : COMMA expr arg_list_tail
                     | empty'''
    if len(p) == 4:
        p[0] = [p[2]] + p[3]
    else:
        p[0] = []

# bin_op ::= PLUS | MINUS | TIMES | DIVIDE | MOD | EQ | NEQ | LT | GT | LE | GE
def p_bin_op(p):
    '''bin_op : PLUS
              | MINUS
              | TIMES
              | DIVIDE
              | MOD
              | EQ
              | NEQ
              | LT
              | GT
              | LE
              | GE'''
    p[0] = p[1]

# 空规则
def p_empty(p):
    '''empty :'''
    p[0] = []

# 错误处理
def p_error(p):
    print(f"Syntax error at {p.value!r}" if p else "Syntax error at EOF")

# 构建解析器
parser = yacc.yacc(debug=True, debugfile='parser.out')