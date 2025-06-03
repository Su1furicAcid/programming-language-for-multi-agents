"""
File name: pllm_parser.py
Description: This file contains the parser for the PLLM language, defining the grammar and parsing rules.
Author: Sun Ao
Last edited: 2025-6-2
"""

import ply.yacc as yacc
from pllm_ast import *
from pllm_lexer import lexer, tokens

"""
Precedence and associativity of operators
"""
precedence = (
    ('left', 'PLUS', 'MINUS'),
    ('left', 'TIMES', 'DIVIDE', 'MOD'),
    ('left', 'EQ', 'NEQ', 'GT', 'LT', 'LE', 'GE'),
)

"""
Global variable to store parse errors
"""
parse_errors = []

"""
Syntax rules for the PLLM language, generating an AST when parsing the source code.
Every rule corresponds to an error handling rule, which returns an AST node or an error node.
"""
def p_program(p):
    '''program : program_body'''
    p[0] = Program(body=p[1], position=get_position(p))

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

def p_var_decl_list(p):
    '''var_decl_list : var_decl var_decl_list
                     | var_decl'''
    if len(p) == 3:
        p[0] = [p[1]] + p[2]
    else:
        p[0] = [p[1]]

def p_var_decl(p):
    '''var_decl : identifier COLON type EQUALS expr
                | identifier COLON type
                | identifier EQUALS expr
                | identifier'''
    if len(p) == 6:
        p[0] = VarDecl(name=p[1], var_type=p[3], value=p[5], position=get_position(p))
    elif len(p) == 4:
        if p[2] == ':':
            p[0] = VarDecl(name=p[1], var_type=p[3], position=get_position(p))
        else:
            p[0] = VarDecl(name=p[1], value=p[3], position=get_position(p))
    else:
        p[0] = VarDecl(name=p[1], position=get_position(p))

def p_type(p):
    '''type : base_type
            | list_type
            | record_type
            | func_ret_type
            | union_type
            | type_alias'''
    p[0] = p[1]

def p_base_type(p):
    '''base_type : TYPE_STR
                 | TYPE_INT
                 | TYPE_FLOAT
                 | TYPE_BOOL
                 | TYPE_UNIT'''
    p[0] = p[1]

def p_type_alias(p):
    '''type_alias : IDENTIFIER'''
    p[0] = p[1]

def p_union_type(p):
    '''union_type : TYPE_UNION LBRACKET type_list RBRACKET'''
    p[0] = f"union[{p[3]}]"

def p_func_ret_type(p):
    '''func_ret_type : LPAREN type_list RPAREN'''
    p[0] = p[2]

def p_type_list(p):
    '''type_list : type
                 | type COMMA type_list'''
    if len(p) == 4:
        p[0] = p[1] + ", " + p[3]
    else:
        p[0] = p[1]

def p_list_type(p):
    '''list_type : TYPE_LIST LBRACKET type RBRACKET'''
    p[0] = f"list[{p[3]}]"

def p_record_type(p):
    '''record_type : TYPE_RECORD LBRACE field_decl_list RBRACE'''
    p[0] = "record{" + p[3] + "}"

def p_field_decl_list(p):
    '''field_decl_list : field_decl COMMA field_decl_list
                       | field_decl'''
    if len(p) == 4:
        p[0] = f"{p[1]}, {p[3]}"
    else:
        p[0] = p[1]

def p_field_decl(p):
    '''field_decl : identifier COLON type'''
    p[0] = f"{p[1].name}: {p[3]}"

def p_agent_def(p):
    '''agent_def : AGENT identifier COLON INDENT agent_body DEDENT'''
    p[0] = AgentDef(name=p[2], body=p[5], position=get_position(p))

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
                       | model_block
                       | statement
                       | chat_block'''
    p[0] = p[1]

def p_input_block(p):
    '''input_block : INPUT COLON INDENT var_decl_list DEDENT'''
    p[0] = InputBlock(variables=p[4], position=get_position(p))

def p_input_block_error(p):
    '''input_block : INPUT COLON INDENT error DEDENT'''
    p[0] = InputBlock(variables=[],
                      position=get_position(p))
    parse_errors.append({**get_position(p), "message": "Invalid variable declaration in input block"})

def p_output_block(p):
    '''output_block : OUTPUT COLON INDENT var_decl_list DEDENT'''
    p[0] = OutputBlock(variables=p[4], position=get_position(p))

def p_output_block_error(p):
    '''output_block : OUTPUT COLON INDENT error DEDENT'''
    p[0] = OutputBlock(variables=[],
                      position=get_position(p))
    parse_errors.append({**get_position(p), "message": "Invalid variable declaration in output block"})

def p_model_block(p):
    '''model_block : MODEL COLON constant'''
    p[0] = ModelBlock(model_name=p[3], position=get_position(p))

def p_model_block_error(p):
    '''model_block : MODEL COLON error'''
    p[0] = ModelBlock(model_name="",
                      position=get_position(p))
    parse_errors.append({**get_position(p), "message": "Invalid model name"})

def p_chat_block(p):
    '''chat_block : CHAT identifier COLON TRIPLE_STRING
                  | CHAT COLON TRIPLE_STRING
    '''
    if len(p) == 5:
        p[0] = ChatBlock(name=p[2], template=p[4], position=get_position(p))
    else:
        p[0] = ChatBlock(name="", template=p[3], position=get_position(p))

def p_connect_block(p):
    '''connect_block : CONNECT COLON INDENT connection_list DEDENT'''
    p[0] = ConnectBlock(connections=p[4], position=get_position(p))

def p_connection_list(p):
    '''connection_list : connection connection_list
                       | connection'''
    if len(p) == 3:
        p[0] = [p[1]] + p[2]
    else:
        p[0] = [p[1]]

def p_connection(p):
    '''connection : identifier COLON type INDENT agent_ref ARROW agent_ref DEDENT'''
    p[0] = Connection(name=p[1], conn_type=p[3], source=p[5], target=p[7], position=get_position(p))

def p_agent_ref(p):
    '''agent_ref : identifier agent_ref_tail'''
    p[0] = AgentRef(parts=[p[1]] + p[2], position=get_position(p))

def p_agent_ref_tail(p):
    '''agent_ref_tail : DOT identifier agent_ref_tail
                      | DOT OUTPUT agent_ref_tail
                      | DOT INPUT agent_ref_tail
                      | empty'''
    if len(p) == 4:
        p[0] = [p[2]] + p[3]
    else:
        p[0] = []

def p_func_def(p):
    '''func_def : FUN identifier LPAREN param_list RPAREN ARROW type COLON stmt_block
                | FUN identifier LPAREN param_list RPAREN COLON stmt_block'''
    if len(p) == 10:
        p[0] = FuncDef(name=p[2], params=p[4], return_type=p[7], stmt_body=p[9], position=get_position(p))
    else:
        p[0] = FuncDef(name=p[2], params=p[4], stmt_body=p[7], position=get_position(p))

def p_func_def_error(p):
    '''func_def : FUN identifier LPAREN error RPAREN ARROW type COLON stmt_block
                | FUN identifier LPAREN error RPAREN COLON stmt_block'''
    if len(p) == 10:
        p[0] = FuncDef(name=p[2], params=[],
                       return_type=p[7],
                       stmt_body=p[9],
                       position=get_position(p))
        p[0].params.append()
        parse_errors.append({**get_position(p), "message": "Invalid parameter list in function definition"})
    else:
        p[0] = FuncDef(name=p[2], params=[],
                       stmt_body=p[7],
                       position=get_position(p))
        p[0].params.append()
        parse_errors.append({**get_position(p), "message": "Invalid parameter list in function definition"})

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

def p_param_decl(p):
    '''param_decl : var_decl'''
    p[0] = p[1]

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

def p_statement(p):
    '''statement : for_stmt
                 | if_stmt
                 | while_stmt
                 | assign_stmt
                 | break_stmt
                 | continue_stmt
                 | return_stmt
                 | type_def_stmt'''
    p[0] = p[1]

def p_type_def_stmt(p):
    '''type_def_stmt : TYPE identifier EQUALS type'''
    p[0] = TypeDefStmt(name=p[2], type=p[4], position=get_position(p))

def p_assign_stmt(p):
    '''assign_stmt : assign_target COLON type EQUALS expr
                   | assign_target EQUALS expr'''
    if len(p) == 6:
        p[0] = AssignStmt(target=p[1], var_type=p[3], value=p[5], position=get_position(p))
    else:
        p[0] = AssignStmt(target=p[1], value=p[3], position=get_position(p))

def p_assign_stmt_error(p):
    '''assign_stmt : assign_target COLON type EQUALS error
                   | assign_target EQUALS error'''
    if len(p) == 6:
        p[0] = AssignStmt(target=p[1], var_type=p[3],
                          value="",
                          position=get_position(p))
        parse_errors.append({**get_position(p), "message": "Invalid expression in assignment"})
    else:
        p[0] = AssignStmt(target=p[1],
                          value="",
                          position=get_position(p))
        parse_errors.append({**get_position(p), "message": "Invalid expression in assignment"})

def p_assign_target(p):
    '''assign_target : identifier 
                     | field_access
                     | index_access'''
    p[0] = p[1]

def p_return_stmt(p):
    '''return_stmt : RETURN expr'''
    p[0] = ReturnStmt(value=p[2], position=get_position(p))

def p_for_stmt(p):
    '''for_stmt : FOR identifier IN expr COLON stmt_block'''
    p[0] = ForStmt(iterator=p[2], iterable=p[4], body=p[6], position=get_position(p))

def p_for_stmt_error(p):
    '''for_stmt : FOR identifier IN error COLON stmt_block'''
    p[0] = ForStmt(iterator=p[2], iterable="",
                   body=p[6], position=get_position(p))
    parse_errors.append({**get_position(p), "message": "Invalid iterable in For"})

def p_break_stmt(p):
    '''break_stmt : BREAK'''
    p[0] = BreakStmt()

def p_continue_stmt(p):
    '''continue_stmt : CONTINUE'''
    p[0] = ContinueStmt()

def p_if_stmt(p):
    '''if_stmt : IF expr COLON stmt_block ELSE COLON stmt_block
               | IF expr COLON stmt_block'''
    if len(p) == 8:
        p[0] = IfStmt(condition=p[2], body=p[4], else_block=p[7], position=get_position(p))
    else:
        p[0] = IfStmt(condition=p[2], body=p[4], else_block=None, position=get_position(p))

def p_if_stmt_error(p):
    '''if_stmt : IF error COLON stmt_block ELSE COLON stmt_block
               | IF error COLON stmt_block'''
    if len(p) == 8:
        p[0] = IfStmt(condition="",
                      body=p[4], else_block=p[7], position=get_position(p))
        parse_errors.append({**get_position(p), "message": "Invalid condition of If"})
    else:
        p[0] = IfStmt(condition="",
                      body=p[4], else_block=None, position=get_position(p))
        parse_errors.append({**get_position(p), "message": "Invalid condition of If"})

def p_while_stmt(p):
    '''while_stmt : WHILE expr COLON stmt_block'''
    p[0] = WhileStmt(condition=p[2], body=p[4], position=get_position(p))

def p_while_stmt_error(p):
    '''while_stmt : WHILE error COLON stmt_block'''
    p[0] = WhileStmt(condition="",
                     body=p[4], position=get_position(p))
    parse_errors.append({**get_position(p), "message": "Invalid condition of While"})

def p_expr(p):
    '''expr : expr_head bin_op expr_tail
            | expr_head'''
    if len(p) == 4:
        p[0] = BinaryOp(left=p[1], op=p[2], right=p[3], position=get_position(p))
    else:
        p[0] = p[1]

def p_expr_head(p):
    '''expr_head : atom
                 | list_expr
                 | record_expr
                 | field_access
                 | index_access
                 | func_call'''
    p[0] = p[1]

def p_expr_tail(p):
    '''expr_tail : expr'''
    p[0] = p[1]

def p_atom(p):
    '''atom : identifier
            | constant'''
    p[0] = p[1]

def p_identifier(p):
    '''identifier : IDENTIFIER'''
    p[0] = Identifier(name=p[1], position=get_position(p))

def p_constant(p):
    '''constant : STRING 
                | NUMBER'''
    p[0] = Constant(value=p[1], position=get_position(p))

def p_list_expr(p):
    '''list_expr : LBRACKET list_elements RBRACKET'''
    p[0] = ListExpr(elements=p[2], position=get_position(p))

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

def p_record_expr(p):
    '''record_expr : LBRACE record_elements RBRACE'''
    p[0] = RecordExpr(fields=p[2], position=get_position(p))

def p_record_elements(p):
    '''record_elements : instance_assign record_elements_tail
                       | instance_assign'''
    if len(p) == 3:
        p[0] = [p[1]] + p[2]
    else:
        p[0] = [p[1]]

def p_record_elements_tail(p):
    '''record_elements_tail : COMMA instance_assign record_elements_tail
                            | COMMA instance_assign'''
    if len(p) == 4:
        p[0] = [p[2]] + p[3]
    else:
        p[0] = [p[2]]

def p_instance_assign(p):
    '''instance_assign : identifier EQUALS expr'''
    p[0] = InstanceAssign(field=p[1], value=p[3], position=get_position(p))

def p_index_access(p):
    '''index_access : identifier LBRACKET expr RBRACKET'''
    p[0] = IndexAccess(obj=p[1], index=p[3], position=get_position(p))

def p_field_access(p):
    '''field_access : identifier DOT identifier'''
    p[0] = FieldAccess(obj=p[1], field=p[3], position=get_position(p))

def p_func_call(p):
    '''func_call : identifier LPAREN arg_list RPAREN'''
    p[0] = FuncCall(func_name=p[1], args=p[3], position=get_position(p))

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

def p_empty(p):
    '''empty :'''
    p[0] = []

def p_error(p):
    if p:
        parse_errors.append({
            "start": {"line": p.lineno, "column": 0},
            "end": {"line": p.lineno, "column": 0},
            "message": f"Syntax error at token '{p.value}'",
        })
    else:
        parse_errors.append({
            "start": {"line": 0, "column": 0},
            "end": {"line": 0, "column": 0},
            "message": "Syntax error at EOF",
        })

"""
Helper function to get the position of a node in the AST.
TODO: Implement column information. PLY does not provide column information by default.
"""
def get_position(p, start_idx=1, end_idx=None):
    def find_leftmost(obj):
        if hasattr(obj, "position") and obj.position and obj.position["start"]["line"] > 0:
            return obj.position["start"]
        elif isinstance(obj, list) and obj:
            return find_leftmost(obj[0])
        else:
            return None

    def find_rightmost(obj):
        if hasattr(obj, "position") and obj.position and obj.position["end"]["line"] > 0:
            return obj.position["end"]
        elif isinstance(obj, list) and obj:
            return find_rightmost(obj[-1])
        else:
            return None

    try:
        if end_idx is None:
            end_idx = len(p) - 1 if len(p) > 1 else 1

        left = find_leftmost(p[start_idx])
        right = find_rightmost(p[end_idx])

        if left and right:
            return {"start": left, "end": right}

        start_lineno = p.lineno(start_idx)
        start_lexpos = p.lexpos(start_idx)
        end_lineno = p.lineno(end_idx)
        end_lexpos = p.lexpos(end_idx)
        data = p.lexer.lexdata
        start_line_start = data.rfind('\n', 0, start_lexpos) + 1
        start_column = start_lexpos - start_line_start + 1
        end_line_start = data.rfind('\n', 0, end_lexpos) + 1
        end_column = end_lexpos - end_line_start + len(str(p[end_idx]))
        return {
            "start": {"line": start_lineno, "column": start_column},
            "end": {"line": end_lineno, "column": end_column}
        }
    except Exception:
        return {
            "start": {"line": 0, "column": 0},
            "end": {"line": 0, "column": 0}
        }

"""
Construct the parser.
"""
parser = yacc.yacc(debug=True, debugfile='parser.out')

def parse(source_code):
    """
    Parses the given source code and returns the AST and any parse errors.
    Args:
        source_code (str): The source code to parse.
    Returns:
        tuple: A tuple containing the AST (or None if parsing failed) and a list of parse errors.
    """
    global parse_errors
    parse_errors = []
    result = parser.parse(source_code, lexer=lexer)
    return result, parse_errors