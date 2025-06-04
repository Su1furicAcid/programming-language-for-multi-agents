from typing import Dict, Optional, List
from contextlib import contextmanager
from type_system.type_pre import Type, Any

class TypeEnvironment:
    """
    类型环境类，支持嵌套作用域的标识符类型管理。
    """

    def __init__(self):
        self._scopes: List[Dict[str, Type]] = [{}]
        self._aliases: List[Dict[str, Type]] = [{}]

    def define(self, name: str, type_: Type, level: int = 1) -> None:
        if not self._scopes:
            raise RuntimeError("No active scope found.")
        self._scopes[-level][name] = type_

    def lookup(self, name: str) -> Type:
        for scope in reversed(self._scopes):
            if name in scope:
                return scope[name]
        return Any
    
    def set_alias(self, name: str, type_: Type, level: int = 1) -> None:
        if not self._aliases:
            raise RuntimeError("No active alias scope found.")
        self._aliases[-level][name] = type_

    def get_alias(self, name: str) -> Optional[Type]:
        for alias in reversed(self._aliases):
            if name in alias:
                return alias[name]
        return None
    
    def is_alias(self, name: str) -> bool:
        for scope in reversed(self._aliases):
            if name in scope:
                return True
        return False

    def enterScope(self) -> None:
        self._scopes.append({})
        self._aliases.append({})

    def exitScope(self) -> None:
        if len(self._scopes) <= 1:
            raise RuntimeError("Cannot exit the global scope.")
        self._scopes.pop()
        self._aliases.pop()

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
        return f"<TypeEnvironment: {len(self._scopes)} scopes, {len(self._aliases)} aliases>"