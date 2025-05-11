from abc import ABC, abstractmethod
from typing import List, Dict, Union, TypeVar, Tuple, Sequence

_T = TypeVar('_T', bound='Type')

class Type(ABC):
    """
    类型的抽象基类
    """

    @abstractmethod
    def __str__(self) -> str:
        """返回类型的字符串表示"""
        pass

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}: {str(self)}>"

    @abstractmethod
    def isSubtypeOf(self, other: 'Type') -> bool:
        """
        检查当前类型是否是 other 类型的子类型
        """
        pass

    def isEquivalentTo(self, other: 'Type') -> bool:
        """
        检查当前类型是否与 other 类型等价
        """
        if not isinstance(other, Type):
            return False
        return self.isSubtypeOf(other) and other.isSubtypeOf(self)

    @abstractmethod
    def __eq__(self, other) -> bool:
        """
        类型相等性比较。对于复合类型，它要求结构完全相同
        """
        pass

    @abstractmethod
    def __hash__(self) -> int:
        """
        与 __eq__ 一致的哈希码，以便类型对象可以用作字典键或集合元素
        """
        pass

# Dynamic
class AnyType(Type):
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AnyType, cls).__new__(cls)
        return cls._instance

    def __str__(self) -> str:
        return "any"

    def isSubtypeOf(self, other: 'Type') -> bool:
        return True

    def __eq__(self, other) -> bool:
        return isinstance(other, AnyType)

    def __hash__(self) -> int:
        return hash("any")

ANY = AnyType()

# Basic types
class BasicType(Type):
    def __init__(self, name: str):
        if not name:
            raise ValueError("BasicType name cannot be empty")
        self._name = name

    def __str__(self) -> str:
        return self._name

    @property
    def name(self) -> str:
        return self._name

    def isSubtypeOf(self, other: 'Type') -> bool:
        if isinstance(other, AnyType):
            return True
        if isinstance(other, BasicType):
            if self._name == "int" and other._name == "float":
                return True
            return self._name == other._name
        return False

    def __eq__(self, other) -> bool:
        return isinstance(other, BasicType) and self._name == other._name

    def __hash__(self) -> int:
        return hash(self._name)

IntType = BasicType("int")
FloatType = BasicType("float")
StrType = BasicType("str")
BoolType = BasicType("bool")
VoidType = BasicType("void")

# Extension
class ListType(Type):
    def __init__(self, element_type: Type):
        if not isinstance(element_type, Type):
            raise TypeError("ListType element_type must be a Type instance.")
        self._element_type = element_type

    @property
    def element_type(self) -> Type:
        return self._element_type

    def __str__(self) -> str:
        return f"list[{str(self._element_type)}]"

    def isSubtypeOf(self, other: 'Type') -> bool:
        if isinstance(other, AnyType):
            return True
        if isinstance(other, ListType):
            if self._element_type is ANY and other._element_type is ANY:
                return True
            if self._element_type is ANY:
                return self._element_type.isSubtypeOf(other._element_type)
            if other._element_type is ANY:
                return self._element_type.isSubtypeOf(other._element_type)
            return self._element_type.isSubtypeOf(other._element_type)
        return False

    def __eq__(self, other) -> bool:
        return isinstance(other, ListType) and self._element_type == other._element_type

    def __hash__(self) -> int:
        return hash(("list", self._element_type))

class RecordType(Type):
    def __init__(self, fields: Dict[str, Type]):
        for name, field_type in fields.items():
            if not isinstance(field_type, Type):
                raise TypeError(f"Field '{name}' type must be a Type instance, got {type(field_type)}")
        self._fields = dict(sorted(fields.items()))

    @property
    def fields(self) -> Dict[str, Type]:
        return self._fields.copy()

    def __str__(self) -> str:
        if not self._fields:
            return "record{}"
        field_strs = [f"{name}: {str(ftype)}" for name, ftype in self._fields.items()]
        return f"record{{{', '.join(field_strs)}}}"

    def isSubtypeOf(self, other: 'Type') -> bool:
        if isinstance(other, AnyType):
            return True
        if isinstance(other, RecordType):
            for other_field_name, other_field_type in other._fields.items():
                if other_field_name not in self._fields:
                    return False
                if not self._fields[other_field_name].isSubtypeOf(other_field_type):
                    return False
            return True
        return False

    def __eq__(self, other) -> bool:
        if not isinstance(other, RecordType):
            return False
        if len(self._fields) != len(other._fields):
            return False
        other_sorted_fields = dict(sorted(other._fields.items()))
        return self._fields == other_sorted_fields

    def __hash__(self) -> int:
        return hash(("record", tuple(self._fields.items())))