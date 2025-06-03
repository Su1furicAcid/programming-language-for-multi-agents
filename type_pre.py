from abc import ABC, abstractmethod
from typing import Dict, List, Set, Optional
import re
from collections import defaultdict, deque

# --- TypeGraph ---
class TypeGraph:
    def __init__(self):
        self._graph: Dict[str, Set[str]] = defaultdict(set)
        self._all_types: Set[str] = set()

    def register_type(self, name: str):
        """Register a new type name in the type graph."""
        if not name:
            raise ValueError("Type name cannot be empty.")
        self._all_types.add(name)

    def add_subtype(self, subtype: str, supertype: str):
        """Add a subtype-supertype relationship."""
        self.register_type(subtype)
        self.register_type(supertype)
        self._graph[subtype].add(supertype)

    def is_subtype(self, a: str, b: str) -> bool:
        """Check if type `a` is a subtype of type `b`."""
        if a == b or b == "any":
            return True
        visited = set()
        queue = deque([a])
        while queue:
            current = queue.popleft()
            if current == b:
                return True
            for parent in self._graph[current]:
                if parent not in visited:
                    visited.add(parent)
                    queue.append(parent)
        return False

    def get_supertypes(self, typename: str) -> Set[str]:
        """Retrieve all supertypes of a given type."""
        result = set()
        queue = deque([typename])
        while queue:
            current = queue.popleft()
            for parent in self._graph[current]:
                if parent not in result:
                    result.add(parent)
                    queue.append(parent)
        return result

    def all_types(self) -> Set[str]:
        """Get all registered types."""
        return frozenset(self._all_types)


# Global instance of TypeGraph
TYPE_GRAPH = TypeGraph()

# --- Abstract Base Class ---
class Type(ABC):
    @abstractmethod
    def __str__(self) -> str:
        """String representation of the type."""
        pass

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}: {self}>"

    @abstractmethod
    def is_subtype_of(self, other: 'Type') -> bool:
        """Check if this type is a subtype of another."""
        pass

    def is_equivalent_to(self, other: 'Type') -> bool:
        """Check if two types are equivalent."""
        return self.is_subtype_of(other) and other.is_subtype_of(self)

    @abstractmethod
    def __eq__(self, other) -> bool:
        pass

    @abstractmethod
    def __hash__(self) -> int:
        pass


# --- Singleton AnyType ---
class AnyType(Type):
    _instance: Optional['AnyType'] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __str__(self) -> str:
        return "any"

    def is_subtype_of(self, other: 'Type') -> bool:
        return True

    def __eq__(self, other) -> bool:
        return isinstance(other, AnyType)

    def __hash__(self) -> int:
        return hash("any")


# Singleton instance
Any = AnyType()


# --- BasicType ---
class BasicType(Type):
    def __init__(self, name: str):
        if not name:
            raise ValueError("BasicType name cannot be empty.")
        self._name = name
        TYPE_GRAPH.register_type(name)

    def __str__(self) -> str:
        return self._name

    @property
    def name(self) -> str:
        return self._name

    def is_subtype_of(self, other: 'Type') -> bool:
        if isinstance(other, AnyType):
            return True
        if isinstance(other, BasicType):
            return TYPE_GRAPH.is_subtype(self.name, other.name)
        return False

    def __eq__(self, other) -> bool:
        return isinstance(other, BasicType) and self.name == other.name

    def __hash__(self) -> int:
        return hash(self.name)


# --- ListType ---
class ListType(Type):
    def __init__(self, element_type: Type):
        self._element_type = element_type

    def __str__(self) -> str:
        return f"list[{self._element_type}]"

    @property
    def element_type(self) -> Type:
        return self._element_type

    def is_subtype_of(self, other: 'Type') -> bool:
        if isinstance(other, AnyType):
            return True
        if isinstance(other, ListType):
            return self.element_type.is_subtype_of(other.element_type)
        return False

    def __eq__(self, other) -> bool:
        return isinstance(other, ListType) and self.element_type == other.element_type

    def __hash__(self) -> int:
        return hash(("list", self._element_type))


# --- RecordType ---
class RecordType(Type):
    def __init__(self, fields: Dict[str, Type]):
        self._fields = dict(sorted(fields.items()))

    def __str__(self) -> str:
        if not self._fields:
            return "record{}"
        field_strs = [f"{name}: {t}" for name, t in self._fields.items()]
        return f"record{{{', '.join(field_strs)}}}"

    @property
    def fields(self) -> Dict[str, Type]:
        return self._fields.copy()

    def is_subtype_of(self, other: 'Type') -> bool:
        if isinstance(other, AnyType):
            return True
        if isinstance(other, RecordType):
            return all(
                field in self._fields and self._fields[field].is_subtype_of(o_type)
                for field, o_type in other._fields.items()
            )
        return False

    def __eq__(self, other) -> bool:
        return isinstance(other, RecordType) and self._fields == other._fields

    def __hash__(self) -> int:
        return hash(("record", tuple(self._fields.items())))
    
class UnionType(Type):
    def __init__(self, types: List[Type]):
        self._types = list(set(types))
        if not self._types:
            raise ValueError("UnionType must have at least one type.")

    def __str__(self) -> str:
        return f"union[{', '.join(str(t) for t in self._types)}]"

    @property
    def types(self) -> List[Type]:
        return self._types

    def is_subtype_of(self, other: 'Type') -> bool:
        if isinstance(other, AnyType):
            return True
        if isinstance(other, UnionType):
            return all(any(t.is_subtype_of(o) for o in other.types) for t in self._types)
        return all(t.is_subtype_of(other) for t in self._types)

    def __eq__(self, other) -> bool:
        return isinstance(other, UnionType) and set(self._types) == set(other._types)

    def __hash__(self) -> int:
        return hash(("union", tuple(sorted(self._types, key=str))))

# --- FunctionType ---
class FunctionType(Type):
    def __init__(self, param_types: List[Type], return_types: List[Type]):
        """
        Initialize a FunctionType with a list of parameter types and a list of return types.
        :param param_types: List of parameter types.
        :param return_types: List of return types (supporting multiple returns).
        """
        self._param_types = param_types
        self._return_types = return_types

    def __str__(self) -> str:
        param_str = ", ".join(str(p) for p in self._param_types)
        return_str = ", ".join(str(r) for r in self._return_types)
        return f"({param_str}) -> ({return_str})"

    @property
    def param_types(self) -> List[Type]:
        """Get the list of parameter types."""
        return self._param_types

    @property
    def return_types(self) -> List[Type]:
        """Get the list of return types."""
        return self._return_types

    def is_subtype_of(self, other: 'Type') -> bool:
        if isinstance(other, AnyType):
            return True
        if isinstance(other, FunctionType):
            if len(self._param_types) != len(other._param_types):
                return False
            for self_param, other_param in zip(self._param_types, other._param_types):
                if not other_param.is_subtype_of(self_param): 
                    return False
            if len(self._return_types) != len(other._return_types):
                return False
            for self_return, other_return in zip(self._return_types, other._return_types):
                if not self_return.is_subtype_of(other_return):
                    return False
            return True
        return False

    def __eq__(self, other) -> bool:
        return (isinstance(other, FunctionType) and
                self._param_types == other._param_types and
                self._return_types == other._return_types)

    def __hash__(self) -> int:
        return hash(("function", tuple(self._param_types), tuple(self._return_types)))

class AliasType(Type):
    def __init__(self, alias: str, target: Type):
        if not alias:
            raise ValueError("Alias name cannot be empty.")
        if not isinstance(target, Type):
            raise ValueError("Alias target must be a Type.")
        self._alias = alias
        self._target = target

    @property
    def alias(self) -> str:
        return self._alias

    @property
    def target(self) -> Type:
        return self._target

    def __str__(self) -> str:
        return self._alias

    def is_subtype_of(self, other: 'Type') -> bool:
        return self._target.is_subtype_of(other)

    def __eq__(self, other) -> bool:
        return isinstance(other, AliasType) and self._target == other._target

    def __hash__(self) -> int:
        return hash(("alias", self._alias, self._target))

# --- Utilities ---
def string_to_type(type_str: str) -> Type:
    """Convert a type string to a Type instance."""
    if not type_str:
        return Any

    if type_str in STRING_TO_TYPE:
        return STRING_TO_TYPE[type_str]

    # List type
    list_match = re.fullmatch(r'list\[(.+)\]', type_str)
    if list_match:
        return ListType(string_to_type(list_match.group(1)))

    # Record type
    record_match = re.fullmatch(r'record\{(.*)\}', type_str)
    if record_match:
        fields = {}
        content = record_match.group(1).strip()
        if content:
            for field in content.split(','):
                name, typeval = map(str.strip, field.split(":"))
                fields[name] = string_to_type(typeval)
        return RecordType(fields)

    # Function type
    func_match = re.fullmatch(r'\((.*)\)\s*->\s*\((.*)\)', type_str)
    if func_match:
        param_strs = func_match.group(1).strip()
        return_strs = func_match.group(2).strip()
        param_types = [string_to_type(p.strip()) for p in param_strs.split(",") if p.strip()]
        return_types = [string_to_type(r.strip()) for r in return_strs.split(",") if r.strip()]
        return FunctionType(param_types, return_types)

    # Union type
    union_match = re.fullmatch(r'union\[(.+)\]', type_str)
    if union_match:
        # 解析 union[...] 内部的类型
        types = [string_to_type(t.strip()) for t in union_match.group(1).split(",")]
        return UnionType(types)

    raise ValueError(f"Unknown type string: {type_str}")

def type_to_pycode(t: Type) -> str:
    """Convert a Type instance to Python type annotation."""
    if isinstance(t, AnyType):
        return "Any"
    if isinstance(t, BasicType):
        return {
            "int": "int",
            "float": "float",
            "str": "str",
            "bool": "bool",
            "unit": "None",
        }.get(t.name, "Any")
    if isinstance(t, ListType):
        return f"List[{type_to_pycode(t.element_type)}]"
    if isinstance(t, RecordType):
        items = ", ".join(f'"{k}": {type_to_pycode(v)}' for k, v in t.fields.items())
        return f"TypedDict('Rec', {{{items}}})"
    if isinstance(t, FunctionType):
        param_types = ", ".join(type_to_pycode(p) for p in t.param_types)
        return_types = ", ".join(type_to_pycode(r) for r in t.return_types)
        return f"Callable[[{param_types}], Tuple[{return_types}]]"
    if isinstance(t, UnionType):
        return f"Union[{', '.join(type_to_pycode(tp) for tp in t.types)}]"
    raise ValueError(f"Unknown type object: {t}")

# --- Built-in Type Instances ---
Int = BasicType("int")
Float = BasicType("float")
Str = BasicType("str")
Bool = BasicType("bool")
Unit = BasicType("unit")

STRING_TO_TYPE = {
    "int": Int,
    "float": Float,
    "str": Str,
    "bool": Bool,
    "unit": Unit,
    "any": Any,
}

# Register subtype relationships
TYPE_GRAPH.add_subtype("bool", "int")
TYPE_GRAPH.add_subtype("int", "float")
TYPE_GRAPH.add_subtype("float", "any")
TYPE_GRAPH.add_subtype("str", "any")
TYPE_GRAPH.add_subtype("unit", "any")