# --- Type System with TypeGraph for Subtyping ---

from abc import ABC, abstractmethod
from typing import Dict, List, Union, Tuple
import re
from collections import defaultdict, deque

# --- TypeGraph ---
class TypeGraph:
    def __init__(self):
        self._graph: Dict[str, set] = defaultdict(set)
        self._all_types: set = set()

    def register_type(self, name: str):
        self._all_types.add(name)

    def add_subtype(self, subtype: str, supertype: str):
        self.register_type(subtype)
        self.register_type(supertype)
        self._graph[subtype].add(supertype)

    def is_subtype(self, a: str, b: str) -> bool:
        if a == b:
            return True
        if b == "any":
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

    def get_supertypes(self, typename: str) -> set:
        result = set()
        queue = deque([typename])
        while queue:
            current = queue.popleft()
            for parent in self._graph[current]:
                if parent not in result:
                    result.add(parent)
                    queue.append(parent)
        return result

    def all_types(self) -> set:
        return set(self._all_types)


# Initialize the global type graph
TYPE_GRAPH = TypeGraph()

# --- Abstract Base Class ---
class Type(ABC):
    @abstractmethod
    def __str__(self) -> str: ...

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}: {self}>"

    @abstractmethod
    def is_subtype_of(self, other: 'Type') -> bool: ...

    def is_equivalent_to(self, other: 'Type') -> bool:
        return self.is_subtype_of(other) and other.is_subtype_of(self)

    @abstractmethod
    def __eq__(self, other) -> bool: ...

    @abstractmethod
    def __hash__(self) -> int: ...


# --- Singleton AnyType ---
class AnyType(Type):
    _instance = None

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


Any = AnyType()


# --- BasicType ---
class BasicType(Type):
    def __init__(self, name: str):
        if not name:
            raise ValueError("BasicType name cannot be empty")
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
        field_strs = [f"{name}: {str(t)}" for name, t in self._fields.items()]
        return f"record{{{', '.join(field_strs)}}}"

    @property
    def fields(self) -> Dict[str, Type]:
        return self._fields.copy()

    def is_subtype_of(self, other: 'Type') -> bool:
        if isinstance(other, AnyType):
            return True
        if isinstance(other, RecordType):
            for field, o_type in other._fields.items():
                if field not in self._fields:
                    return False
                if not self._fields[field].is_subtype_of(o_type):
                    return False
            return True
        return False

    def __eq__(self, other) -> bool:
        return isinstance(other, RecordType) and self._fields == other._fields

    def __hash__(self) -> int:
        return hash(("record", tuple(self._fields.items())))


# --- Register and Relate Built-in Types ---
for t in ["int", "float", "str", "bool", "void", "any"]:
    TYPE_GRAPH.register_type(t)

TYPE_GRAPH.add_subtype("bool", "int")
TYPE_GRAPH.add_subtype("int", "float")
TYPE_GRAPH.add_subtype("float", "any")
TYPE_GRAPH.add_subtype("str", "any")
TYPE_GRAPH.add_subtype("void", "any")


# --- Built-in Type Instances ---
Int = BasicType("int")
Float = BasicType("float")
Str = BasicType("str")
Bool = BasicType("bool")
Void = BasicType("void")


# --- Utilities ---
STRING_TO_TYPE = {
    "int": Int,
    "float": Float,
    "str": Str,
    "bool": Bool,
    "void": Void,
    "any": Any,
}


def string_to_type(type_str: str) -> Type:
    if not type_str:
        return Any

    if type_str in STRING_TO_TYPE:
        return STRING_TO_TYPE[type_str]

    list_match = re.fullmatch(r'list\[(.+)\]', type_str)
    if list_match:
        return ListType(string_to_type(list_match.group(1)))

    record_match = re.fullmatch(r'record\{(.*)\}', type_str)
    if record_match:
        fields = {}
        content = record_match.group(1).strip()
        if content:
            for field in content.split(','):
                name, typeval = map(str.strip, field.split(":"))
                fields[name] = string_to_type(typeval)
        return RecordType(fields)

    raise ValueError(f"Unknown type string: {type_str}")

def type_to_pycode(t: Type) -> str:
    if isinstance(t, AnyType):
        return "Any"
    elif isinstance(t, BasicType):
        return {
            "int": "int",
            "float": "float",
            "str": "str",
            "bool": "bool",
            "void": "None"
        }.get(t.name, "Any")
    elif isinstance(t, ListType):
        return f"List[{type_to_pycode(t.element_type)}]"
    elif isinstance(t, RecordType):
        items = ", ".join(f'"{k}": {type_to_pycode(v)}' for k, v in t.fields.items())
        return f"TypedDict('Rec', {{{items}}})"
    raise ValueError(f"Unknown type object: {t}")