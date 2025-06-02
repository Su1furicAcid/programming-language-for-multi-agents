import json
from typing import Optional
from pllm_ast import *
from type_env import TypeEnvironment
from type_pre import *

class TypeErrorHandler:
    def __init__(self):
        self.errors = []

    def report(self, message: str = "", node: Optional[ASTNode] = None) -> None:
        """
        记录一个类型错误。
        :param message: 错误信息。
        :param node: 发生错误的AST节点
        """
        if node:
            self.errors.append({
                **node.position,
                "message": message or "Type Error",
            })

    def show(self) -> None:
        if len(self.errors) > 0:
            for err in self.errors:
                print(f"{err['start']['line']}:{err['start']['column']} ~ {err['end']['line']}:{err['end']['column']} : {err['message']}")

class TypeChecker:
    def __init__(self):
        self.type_env = TypeEnvironment()
        self.agent_io = TypeEnvironment()
        self.err_handler = TypeErrorHandler()

    def _addBuiltInFuncs(self, built_in_path: str) -> None:
        with open(built_in_path) as f:
            data = json.load(f)
            for key, val in data.items():
                self.type_env.define(key, string_to_type(val))

    def _initTypeEnvironment(self) -> None:
        self._addBuiltInFuncs("built_in_sig.json")
        self.type_env.define("_", Any)
        return
    
    def _show(self) -> None:
        self.err_handler.show()

    def checkProgram(self, program_node: Program) -> None:
        self._initTypeEnvironment()
        self.visit(program_node)
        # self._show()

    def visit(self, ast_node: ASTNode) -> Optional[Type]:
        method_name: str = f"visit{type(ast_node).__name__}"
        visitor = getattr(self, method_name, self._defaultVisitor)
        return visitor(ast_node)
    
    def _defaultVisitor(self, node: ASTNode) -> None:
        return

    # Program
    def visitProgram(self, node: Program) -> None:
        with self.type_env.scoped():
            for child in node.body:
                self.visit(child)

    # VarDecl
    def visitVarDecl(self, node: VarDecl) -> None:
        decl_var_name = node.name.name
        decl_var_type = string_to_type(node.var_type)
        decl_var_expr = node.value
        env_var_type = self.type_env.lookup(decl_var_name)

        # Case 1: id : type = expr
        if decl_var_expr != "":
            exp_var_type = self.visit(decl_var_expr)
            # type(expr) <: type
            if not exp_var_type.is_subtype_of(decl_var_type):
                self.err_handler.report(node=node)
            # type == history_type
            if not decl_var_type.is_equivalent_to(env_var_type):
                self.err_handler.report(node=node)
            # type(expr) <: history_type
            if not exp_var_type.is_subtype_of(env_var_type):
                self.err_handler.report(node=node)
            # Update the type environment
            self.type_env.define(decl_var_name, decl_var_type)
            return

        # Case 2: id : type
        else:
            # Handle gradual typing: Allow Any in the environment
            if not decl_var_type.is_equivalent_to(env_var_type):
                self.err_handler.report(node=node)
            # Update the type environment
            self.type_env.define(decl_var_name, decl_var_type)
            return
        
    # AgentDef
    # TODO: Assign a type to Agent, current type system is not complete
    def visitAgentDef(self, node: AgentDef) -> None:
        with self.type_env.scoped():
            for child in node.body:
                self.visit(child)
                if isinstance(child, InputBlock):
                    for var in child.variables:
                        self.agent_io.define(f"{node.name.name}.input.{var.name.name}", self.type_env.lookup(var.name.name));
                if isinstance(child, OutputBlock):
                    for var in child.variables:
                        self.agent_io.define(f"{node.name.name}.output.{var.name.name}", self.type_env.lookup(var.name.name));

    # InputBlock
    def visitInputBlock(self, node: InputBlock) -> None:
        for child in node.variables:
            self.visit(child)

    # OutputBlock
    def visitOutputBlock(self, node: OutputBlock) -> None:
        for child in node.variables:
            self.visit(child)

    # ModelBlock
    def visitModelBlock(self, node: ModelBlock) -> None:
        return
    
    # ChatBlock
    def visitChatBlock(self, node: ChatBlock) -> None:
        return
    
    # ConnectBlock
    def visitConnectBlock(self, node: ConnectBlock) -> None:
        for child in node.connections:
            self.visit(child)

    # Connection
    def visitConnection(self, node: Connection) -> None:
        source = f"{node.source.parts[0].name}.{node.source.parts[1]}.{node.source.parts[2].name}"
        target = f"{node.target.parts[0].name}.{node.target.parts[1]}.{node.target.parts[2].name}"
        source_type = self.agent_io.lookup(source)
        target_type = self.agent_io.lookup(target)
        if not source_type.is_subtype_of(target_type):
            self.err_handler.report(node=node)
            return
    
    # AgentRef
    def visitAgentRef(self, node: AgentRef) -> None:
        # handled in Connection
        return
    
    # FuncDef
    def visitFuncDef(self, node: FuncDef) -> None:
        func_name = node.name.name
        func_return_type = string_to_type(node.return_type)
        param_types = []
        with self.type_env.scoped(): 
            for param in node.params:
                self.visit(param)
                param_type = self.type_env.lookup(param.name.name)
                param_types.append(param_type)
            func_type = FunctionType(param_types, [func_return_type])
            self.type_env.define(func_name, func_type, 2)
            return_types = []
            for stmt in node.stmt_body:
                if isinstance(stmt, ReturnStmt):
                    stmt_type = self.visit(stmt.value)
                    return_types.append(stmt_type)
                    continue
                stmt_type = self.visit(stmt)
            for ret_type in return_types:
                if not ret_type.is_subtype_of(func_return_type):
                    self.err_handler.report(
                        f"Return type '{ret_type}' does not match declared return type '{func_return_type}' in function '{func_name}'.",
                        node=node
                    )

    # ParamDecl
    def visitParamDecl(self, node: ParamDecl) -> None:
        decl_var_name = node.name.name
        decl_var_type = node.param_type
        decl_var_expr = node.default_value
        env_var_type = self.type_env.lookup(decl_var_name)

        # Case 1: id : type = expr
        if decl_var_expr != "":
            exp_var_type = self.visit(decl_var_expr)
            # type(expr) <: type
            if not exp_var_type.is_subtype_of(decl_var_type):
                self.err_handler.report(node=node)
            # type == history_type
            if not decl_var_type.is_equivalent_to(env_var_type):
                self.err_handler.report(node=node)
            # type(expr) <: history_type
            if not exp_var_type.is_subtype_of(env_var_type):
                self.err_handler.report(node=node)
            # Update the type environment
            self.type_env.define(decl_var_name, decl_var_type)
            return

        # Case 2: id : type
        else:
            # Handle gradual typing: Allow Any in the environment
            if not decl_var_type.is_equivalent_to(env_var_type):
                self.err_handler.report(node=node)
            # Update the type environment
            self.type_env.define(decl_var_name, decl_var_type)
            return
        
    # AssignStmt
    def visitAssignStmt(self, node: AssignStmt) -> None:
        decl_var_name = node.target
        decl_var_type = string_to_type(node.var_type)
        decl_var_expr = node.value
        exp_var_type = self.visit(decl_var_expr)
        # type(expr) <: type
        if not exp_var_type.is_subtype_of(decl_var_type):
            self.err_handler.report(node=node)
        # Handle gradual typing: Allow Any in the environment
        if isinstance(decl_var_name, Identifier):
            env_var_type = self.type_env.lookup(decl_var_name.name)
            # type == history_type
            if not decl_var_type.is_equivalent_to(env_var_type):
                self.err_handler.report(node=node)
            # type(expr) <: history_type
            if not exp_var_type.is_subtype_of(env_var_type):
                self.err_handler.report(node=node)
            # Update the type environment
            self.type_env.define(decl_var_name.name, decl_var_type)
        elif isinstance(decl_var_name, FieldAccess):
            # FieldAccess: x.a
            obj_type = self.type_env.lookup(decl_var_name.obj.name)
            if not isinstance(obj_type, RecordType):
                self.err_handler.report(node=node)
            if decl_var_name.field.name not in obj_type.fields:
                self.err_handler.report(node=node)
            field_type = obj_type.fields[decl_var_name.field.name]
            # type == field_type
            if not decl_var_type.is_equivalent_to(field_type):
                self.err_handler.report(node=node)
            # type(expr) <: field_type
            if not exp_var_type.is_subtype_of(field_type):
                self.err_handler.report(node=node)
        elif isinstance(decl_var_name, IndexAccess):
            # IndexAccess: x[a]
            obj_type = self.type_env.lookup(decl_var_name.obj.name)
            if not isinstance(obj_type, ListType):
                self.err_handler.report(node=node)
            index_type = self.visit(decl_var_name.index)
            if index_type is not Int:
                self.err_handler.report(node=node)
            element_type = obj_type.element_type
            # type == element_type
            if not decl_var_type.is_equivalent_to(element_type):
                self.err_handler.report(node=node)
            # type(expr) <: element_type
            if not exp_var_type.is_subtype_of(element_type):
                self.err_handler.report(node=node)
        return
    
    # IfStmt
    def visitIfStmt(self, node: IfStmt) -> None:
        cond_expr = node.condition
        cond_expr_type = self.visit(cond_expr)
        if not cond_expr_type.is_equivalent_to(Bool):
            self.err_handler.report(node=node)
        for stmt in node.body:
            with self.type_env.scoped():
                self.visit(stmt)
        for stmt in node.else_block:
            with self.type_env.scoped():
                self.visit(stmt)
        return
    
    # WhileStmt
    def visitWhileStmt(self, node: WhileStmt) -> None:
        cond_expr = node.condition
        cond_expr_type = self.visit(cond_expr)
        if not cond_expr_type.is_equivalent_to(Bool):
            self.err_handler.report(node=node)
        for stmt in node.body:
            with self.type_env.scoped():
                self.visit(stmt)
        return
    
    # ForStmt
    def visitForStmt(self, node: ForStmt) -> None:
        iterator = node.iterator.name
        iterable = node.iterable.name
        iterator_type = self.type_env.lookup(iterator)
        iterable_type = self.type_env.lookup(iterable)
        if not isinstance(iterable_type, ListType):
            print("TypeError")
        element_type = iterable_type.element_type
        if not iterator_type.is_subtype_of(element_type):
            print("TypeError")
        for stmt in node.body:
            self.visit(stmt)

    # BreakStmt
    def visitBreakStmt(self, node: BreakStmt) -> None:
        return

    # ContinueStmt
    def visitContinueStmt(self, node: ContinueStmt) -> None:
        return

    # BinaryOp
    def visitBinaryOp(self, node: BinaryOp) -> Type:
        left_type = self.visit(node.left)
        right_type = self.visit(node.right)

        if node.op in {"+", "-", "*", "/", "%"}:
            if not (left_type.is_subtype_of(Int) or left_type.is_subtype_of(Float)):
                self.err_handler.report(node=node)
            if not (right_type.is_subtype_of(Int) or right_type.is_subtype_of(Float)):
                self.err_handler.report(node=node)
            if left_type.is_equivalent_to(Float) or right_type.is_equivalent_to(Float):
                return Float
            return Int
        elif node.op in {"==", "!=", "<", ">", "<=", ">="}:
            if not left_type.is_subtype_of(right_type) and not right_type.is_subtype_of(left_type):
                self.err_handler.report(node=node)
            return Bool
        else:
            self.err_handler.report(node=node)

    # Identifier
    def visitIdentifier(self, node: Identifier) -> Type:
        var_type = self.type_env.lookup(node.name)
        return var_type
        
    # Constant
    def visitConstant(self, node: Constant) -> Type:
        value = node.value
        if isinstance(value, int):
            return Int
        elif isinstance(value, float):
            return Float
        elif isinstance(value, str):
            return Str
        elif isinstance(value, bool):
            return Bool
        
    # ListExpr
    def visitListExpr(self, node: ListExpr) -> Type:
        element_types = [self.visit(element) for element in node.elements]
        # TODO: lub
        if len(set(element_types)) > 1:
            self.err_handler.report(node=node)
        return ListType(element_types[0]) if element_types else ListType(Any)
    
    # RecordExpr
    def visitRecordExpr(self, node: RecordExpr) -> Type:
        fields = {}
        for inst_assign in node.fields:
            if not isinstance(inst_assign, InstanceAssign):
                self.error_handler.report(
                    f"Expected InstanceAssign in RecordExpr, but got {type(inst_assign).__name__}",
                    node
                )
                continue
            field_type = self.visit(inst_assign)
            fields[inst_assign.field.name] = field_type
        return RecordType(fields)

    # InstanceAssign
    def visitInstanceAssign(self, node: InstanceAssign) -> Type:
        field_value_type = self.visit(node.value)
        
        if not field_value_type:
            self.error_handler.report(node)
            return Any
        
        return field_value_type
    
    # FieldAccess
    def visitFieldAccess(self, node: FieldAccess) -> Type:
        obj = node.obj.name
        obj_type = self.type_env.lookup(obj)
        if not isinstance(obj_type, RecordType):
            self.err_handler.report(node=node)
        if node.field not in obj_type.fields:
            self.err_handler.report(node=node)
        return obj_type.fields[node.field]
    
    # IndexAccess
    def visitIndexAccess(self, node: IndexAccess) -> Type:
        obj = node.obj.name
        obj_type = self.type_env.lookup(obj)
        if not isinstance(obj_type, ListType):
            self.err_handler.report(node=node)
        return obj_type.element_type

    # FuncCall
    def visitFuncCall(self, node: FuncCall) -> Type:
        func_name = node.func_name.name
        func_type = self.type_env.lookup(func_name)
        if not isinstance(func_type, FunctionType):
            self.err_handler.report(
                f"'{func_name}' is not a callable function.",
                node=node
            )
            return Any
        if len(node.args) != len(func_type.param_types):
            self.err_handler.report(
                f"Function '{func_name}' expects {len(func_type.param_types)} arguments, but {len(node.args)} were provided.",
                node=node
            )
            return func_type.return_types[0] if func_type.return_types else Unit
        for arg, param_type in zip(node.args, func_type.param_types):
            arg_type = self.visit(arg)
            if not arg_type.is_subtype_of(param_type):
                self.err_handler.report(
                    f"Argument type '{arg_type}' does not match parameter type '{param_type}' in function '{func_name}'.",
                    node=node
                )
        if len(func_type.return_types) == 1:
            return func_type.return_types[0]
        elif len(func_type.return_types) > 1:
            return RecordType({f"ret{i}": t for i, t in enumerate(func_type.return_types)})
        else:
            return Unit
        
def check_types(program_node: Program) -> None:
    type_checker = TypeChecker()
    type_checker.checkProgram(program_node)
    return type_checker.err_handler.errors