class ASTNode:
    """基础 AST 节点类"""
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    def __repr__(self):
        fields = ", ".join(f"{key}={value!r}" for key, value in self.__dict__.items())
        return f"{self.__class__.__name__}({fields})"

class Program(ASTNode):
    """程序节点，包含全局块和多个语句/定义"""
    def __init__(self, global_block=None, body=None):
        super().__init__(global_block=global_block, body=body or [])

class GlobalBlock(ASTNode):
    """全局变量块"""
    def __init__(self, variables=None):
        super().__init__(variables=variables or []) 

class VarDecl(ASTNode):
    """变量声明节点"""
    def __init__(self, name, var_type=None, value=None):
        super().__init__(name=name, var_type=var_type, value=value)

class AgentDef(ASTNode):
    """代理定义"""
    def __init__(self, name, body=None):
        super().__init__(name=name, body=body or [])

class InputBlock(ASTNode):
    """输入块"""
    def __init__(self, variables=None):
        super().__init__(variables=variables or [])

class OutputBlock(ASTNode):
    """输出块"""
    def __init__(self, variables=None):
        super().__init__(variables=variables or [])

class MemoryBlock(ASTNode):
    """内存块"""
    def __init__(self, variables=None):
        super().__init__(variables=variables or [])

class ModelBlock(ASTNode):
    """模型块"""
    def __init__(self, model_name):
        super().__init__(model_name=model_name)

class ChatBlock(ASTNode):
    """聊天块"""
    def __init__(self, name, template):
        super().__init__(name=name, template=template)

class ConnectBlock(ASTNode):
    """连接块"""
    def __init__(self, connections=None):
        super().__init__(connections=connections or [])

class Connection(ASTNode):
    """连接定义"""
    def __init__(self, name, conn_type, source, target):
        super().__init__(name=name, conn_type=conn_type, source=source, target=target)

class AgentRef(ASTNode):
    """代理引用（嵌套结构）"""
    def __init__(self, parts):
        super().__init__(parts=parts)

class FuncDef(ASTNode):
    """函数定义节点"""
    def __init__(self, name, params=None, return_type=None, stmt_body=None, expr_body=None):
        super().__init__(name=name, params=params or [], return_type=return_type, 
                         stmt_body=stmt_body, expr_body=expr_body)

class ParamDecl(ASTNode):
    """参数声明"""
    def __init__(self, name, param_type=None, default_value=None):
        super().__init__(name=name, param_type=param_type, default_value=default_value)

class Type(ASTNode):
    """类型基类"""
    def __init__(self, name, params=None):
        super().__init__(name=name, params=params or [])

class BaseType(Type):
    """基础类型"""
    def __init__(self, name):
        super().__init__(name=name)

class ListType(Type):
    """列表类型"""
    def __init__(self, element_type):
        super().__init__(name="list", params=[element_type])

class RecordType(Type):
    """记录类型"""
    def __init__(self, fields=None):
        super().__init__(name="record", params=fields or [])

class TupleType(Type):
    """元组类型"""
    def __init__(self, element_types=None):
        super().__init__(name="tuple", params=element_types or [])

class Stmt(ASTNode):
    """语句基类"""
    def __init__(self, metadata=None, **kwargs):
        super().__init__(metadata=metadata, **kwargs)

class AssignStmt(Stmt):
    """赋值语句"""
    def __init__(self, target, var_type=None, value=None):
        super().__init__(target=target, var_type=var_type, value=value)

class ExprStmt(Stmt):
    """表达式语句"""
    def __init__(self, expr):
        super().__init__(expr=expr)

class ReturnStmt(Stmt):
    """返回语句"""
    def __init__(self, value=None):
        super().__init__(value=value)

class IfStmt(Stmt):
    """条件语句"""
    def __init__(self, condition, body, else_block=None):
        super().__init__(condition=condition, body=body, else_block=else_block)

class WhileStmt(Stmt):
    """循环语句"""
    def __init__(self, condition, body):
        super().__init__(condition=condition, body=body)

class ForStmt(Stmt):
    """For 循环"""
    def __init__(self, iterator, iterable, body):
        super().__init__(iterator=iterator, iterable=iterable, body=body)

class BreakStmt(Stmt):
    """Break 语句"""
    def __init__(self):
        super().__init__()

class ContinueStmt(Stmt):
    """Continue 语句"""
    def __init__(self):
        super().__init__()

class Expr(ASTNode):
    """表达式基类"""
    def __init__(self, expr_type=None, **kwargs):
        super().__init__(expr_type=expr_type, **kwargs)

class BinaryOp(Expr):
    """二元操作表达式"""
    def __init__(self, left, op, right):
        super().__init__(left=left, op=op, right=right)

class FuncCall(Expr):
    """函数调用表达式"""
    def __init__(self, func_name, args=None):
        super().__init__(func_name=func_name, args=args or [])

class Atom(Expr):
    """原子表达式"""
    def __init__(self, value):
        super().__init__(value=value)

class ListExpr(Expr):
    """列表表达式"""
    def __init__(self, elements=None):
        super().__init__(elements=elements or [])

class RecordExpr(Expr):
    """记录表达式"""
    def __init__(self, fields=None):
        super().__init__(fields=fields or [])

class TupleExpr(Expr):
    """元组表达式"""
    def __init__(self, elements=None):
        super().__init__(elements=elements or [])

class FieldDecl(ASTNode):
    """字段声明"""
    def __init__(self, name, field_type):
        super().__init__(name=name, field_type=field_type)

class FieldAccess(Expr):
    """字段访问"""
    def __init__(self, obj, field):
        super().__init__(obj=obj, field=field)

class FieldAssign(Stmt):
    """字段赋值"""
    def __init__(self, obj, field, value):
        super().__init__(obj=obj, field=field, value=value)