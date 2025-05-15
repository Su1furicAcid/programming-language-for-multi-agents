from abc import ABC, abstractmethod
from typing import Dict, List, Union, Tuple, Set, Optional
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


# --- Utilities ---
def string_to_type(type_str: str) -> Type:
    """Convert a type string to a Type instance."""
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
    """Convert a Type instance to Python type annotation."""
    if isinstance(t, AnyType):
        return "Any"
    if isinstance(t, BasicType):
        return {
            "int": "int",
            "float": "float",
            "str": "str",
            "bool": "bool",
            "void": "None",
        }.get(t.name, "Any")
    if isinstance(t, ListType):
        return f"List[{type_to_pycode(t.element_type)}]"
    if isinstance(t, RecordType):
        items = ", ".join(f'"{k}": {type_to_pycode(v)}' for k, v in t.fields.items())
        return f"TypedDict('Rec', {{{items}}})"
    raise ValueError(f"Unknown type object: {t}")


# --- Built-in Type Instances ---
STRING_TO_TYPE = {
    "int": BasicType("int"),
    "float": BasicType("float"),
    "str": BasicType("str"),
    "bool": BasicType("bool"),
    "void": BasicType("void"),
    "any": Any,
}

# Register subtype relationships
TYPE_GRAPH.add_subtype("bool", "int")
TYPE_GRAPH.add_subtype("int", "float")
TYPE_GRAPH.add_subtype("float", "any")
TYPE_GRAPH.add_subtype("str", "any")
TYPE_GRAPH.add_subtype("void", "any")