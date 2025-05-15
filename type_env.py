from typing import Dict, Optional, List
from contextlib import contextmanager
from type_pre import Type

class TypeEnvironment:
    """
    类型环境类，支持嵌套作用域的标识符类型管理。
    """

    def __init__(self):
        self._scopes: List[Dict[str, Type]] = [{}]

    def define(self, name: str, type_: Type, level: int = 1) -> None:
        if not self._scopes:
            raise RuntimeError("No active scope found.")
        self._scopes[-level][name] = type_

    def lookup(self, name: str) -> Optional[Type]:
        for scope in reversed(self._scopes):
            if name in scope:
                return scope[name]
        return None

    def enterScope(self) -> None:
        self._scopes.append({})

    def exitScope(self) -> None:
        if len(self._scopes) <= 1:
            raise RuntimeError("Cannot exit the global scope.")
        self._scopes.pop()

    @contextmanager
    def scoped(self):
        self.enterScope()
        try:
            yield
        finally:
            self.exitScope()

    def __str__(self) -> str:
        scope_strs = []
        for i, scope in enumerate(self._scopes):
            scope_strs.append(f"Scope {i}: {scope}")
        return "\n".join(scope_strs)

    def __repr__(self) -> str:
        return f"<TypeEnvironment: {len(self._scopes)} scopes>"