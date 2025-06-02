class ASTNode:
    """基础 AST 节点类"""
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    def __repr__(self):
        fields = ", ".join(f"{key}={value!r}" for key, value in self.__dict__.items())
        return f"{self.__class__.__name__}({fields})"

class Program(ASTNode):
    """程序节点，包含全局块和多个语句/定义"""
    def __init__(self, body=[], position={}):
        super().__init__(body=body, position=position)

class VarDecl(ASTNode):
    """变量声明节点"""
    def __init__(self, name, var_type="", value="", position={}):
        super().__init__(name=name, var_type=var_type, value=value, position=position)

class AgentDef(ASTNode):
    """代理定义"""
    def __init__(self, name, body=[], position={}):
        super().__init__(name=name, body=body, position=position)

class InputBlock(ASTNode):
    """输入块"""
    def __init__(self, variables=[], position={}):
        super().__init__(variables=variables, position=position)

class OutputBlock(ASTNode):
    """输出块"""
    def __init__(self, variables=[], position={}):
        super().__init__(variables=variables, position=position)

class ModelBlock(ASTNode):
    """模型块"""
    def __init__(self, model_name, position={}):
        super().__init__(model_name=model_name, position=position)

class ChatBlock(ASTNode):
    """聊天块"""
    def __init__(self, name, template, position={}):
        super().__init__(name=name, template=template, position=position)

class ConnectBlock(ASTNode):
    """连接块"""
    def __init__(self, connections=[], position={}):
        super().__init__(connections=connections, position=position)

class Connection(ASTNode):
    """连接定义"""
    def __init__(self, name, conn_type, source, target, position={}):
        super().__init__(name=name, conn_type=conn_type, source=source, target=target, position=position)

class AgentRef(ASTNode):
    """代理引用（嵌套结构）"""
    def __init__(self, parts, position={}):
        super().__init__(parts=parts, position=position)

class FuncDef(ASTNode):
    """函数定义节点"""
    def __init__(self, name, params=[], return_type="", stmt_body=[], position={}):
        super().__init__(name=name, params=params, return_type=return_type, 
                         stmt_body=stmt_body, position=position)

class ParamDecl(ASTNode):
    """参数声明"""
    def __init__(self, name, param_type="", default_value="", position={}):
        super().__init__(name=name, param_type=param_type, default_value=default_value, position=position)

class Stmt(ASTNode):
    """语句基类"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

class AssignStmt(Stmt):
    """赋值语句"""
    def __init__(self, target, var_type="", value="", position={}):
        super().__init__(target=target, var_type=var_type, value=value, position=position)

class ReturnStmt(Stmt):
    """返回语句"""
    def __init__(self, value="", position={}):
        super().__init__(value=value, position=position)

class IfStmt(Stmt):
    """条件语句"""
    def __init__(self, condition, body, else_block, position={}):
        super().__init__(condition=condition, body=body, else_block=else_block, position=position)

class WhileStmt(Stmt):
    """循环语句"""
    def __init__(self, condition, body, position={}):
        super().__init__(condition=condition, body=body, position=position)

class ForStmt(Stmt):
    """For 循环"""
    def __init__(self, iterator, iterable, body, position={}):
        super().__init__(iterator=iterator, iterable=iterable, body=body, position=position)

class BreakStmt(Stmt):
    """Break 语句"""
    def __init__(self, position={}):
        super().__init__(position=position)

class ContinueStmt(Stmt):
    """Continue 语句"""
    def __init__(self, position={}):
        super().__init__(position=position)

class Expr(ASTNode):
    """表达式基类"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

class BinaryOp(Expr):
    """二元操作表达式"""
    def __init__(self, left, op, right, position={}):
        """初始化二元操作表达式"""
        super().__init__(left=left, op=op, right=right, position=position)

class FuncCall(Expr):
    """函数调用表达式"""
    def __init__(self, func_name, args=[], position={}):
        super().__init__(func_name=func_name, args=args, position=position)

class Identifier(Expr):
    """标识符"""
    def __init__(self, name, position={}):
        super().__init__(name=name, position=position)

class Constant(Expr):
    """字面值"""
    def __init__(self, value, position={}):
        super().__init__(value=value, position=position)

class ListExpr(Expr):
    """列表表达式"""
    def __init__(self, elements=[], position={}):
        super().__init__(elements=elements, position=position)

class RecordExpr(Expr):
    """记录表达式"""
    def __init__(self, fields=[], position={}):
        super().__init__(fields=fields, position=position)

class InstanceAssign(Expr):
    def __init__(self, field, value="", position={}):
        super().__init__(field=field, value=value, position=position)

class TupleExpr(Expr):
    """元组表达式"""
    def __init__(self, elements=[], position={}):
        super().__init__(elements=elements, position=position)

class FieldAccess(Expr):
    """字段访问"""
    def __init__(self, obj, field, position={}):
        super().__init__(obj=obj, field=field, position=position)

class IndexAccess(Expr):
    """列表访问"""
    def __init__(self, obj, index, position={}):
        super().__init__(obj=obj, index=index, position=position)