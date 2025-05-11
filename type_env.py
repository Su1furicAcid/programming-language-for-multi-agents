# 类型环境/符号表类 (Type Environment / Symbol Table)

# 这个类用来实现 Env，即从标识符到其类型的映射。

# TypeEnvironment (或 SymbolTable):
# define(name: string, type: Type): 定义一个标识符及其类型。
# lookup(name: string): Type | null: 查找一个标识符的类型。
# enterScope(): 进入一个新的作用域。
# exitScope(): 退出当前作用域。
# 需要处理作用域嵌套（例如，全局作用域、函数作用域、Agent 作用域）。