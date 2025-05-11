# 类型检查器类 (Type Checker / Analyzer)

# 这是执行类型检查逻辑的核心类。

# TypeChecker:
# 通常会使用访问者模式 (Visitor Pattern) 来遍历 AST。为每种 AstNode 类型实现一个 visit 方法 (例如 visitVarDeclNode(node: VarDeclNode, env: TypeEnvironment)).
# 在 visit 方法内部，实现你的 Well(Env, stmt) 和 Gen(Env, stmt) 规则。
# 维护当前的 TypeEnvironment。
# 当检查表达式时，visit 方法通常会返回该表达式的类型 (Env(e) = T)。
# 当遇到类型错误时，记录错误信息（通常包含错误类型、位置、期望类型和实际类型等）。
# checkProgram(programNode: ProgramNode): 类型检查的入口点。

# TypeChecker (类型检查器)：
# 接收 AST 的根节点。
# 创建一个初始的全局 TypeEnvironment (可以预定义一些内建函数或类型)。
# 开始遍历 AST (通常从根节点开始)。
# 对于声明节点 (如 VarDeclNode, FuncDefNode)，它会更新 TypeEnvironment (对应你的 Gen 规则)。
# 对于表达式节点，它会计算并返回表达式的 Type (对应你的 Env(e) = T 规则)。
# 对于语句节点，它会检查其是否类型良好 (对应你的 Well 规则)。
# 在遍历过程中，TypeChecker 会使用 Type 类的实例进行比较 (如子类型判断)。
# 如果发现错误，通过 ErrorReporter 报告。