from __future__ import annotations

from dataclasses import dataclass, fields, is_dataclass
from functools import reduce
from typing import Annotated, Any, Callable, get_args, get_origin, get_type_hints, TypeVar


CapnpMessage = Any
T = TypeVar("T", bound=object)


@dataclass(frozen=True)
class CapAn:
    """Annotation type for serializing a dataclass field to capnp."""

    field_name: str | None = None
    convert: Callable | None = None
    deserializer: Callable | None = None
    group: str | None = None
    skip: bool = False

    def serialize_value(self, field_name: str, value: Any) -> tuple[str, Any]:
        if self.skip or value is None:
            return "", None
        if self.field_name:
            field_name = self.field_name
        if self.convert:
            value = self.convert(value)
        value = self.default_convert(value)
        if self.group:
            return self.group, {field_name: value}
        return field_name, value

    def deserialize_value(self, field_name: str, field_type: Any, src: CapnpMessage) -> tuple[str, Any]:
        if self.skip:
            return "", None
        if self.field_name:
            field_name = self.field_name
        if self.group:
            src = getattr(src, self.group)
        value = getattr(src, field_name)
        if self.deserializer:
            value = self.deserializer(value)
        value = self.default_deserializer(field_type, value)
        return field_name, value

    @classmethod
    def default_convert(cls, value: Any) -> Any:
        if is_dataclass(value):
            return cls.serialize_dataclass(value)
        if isinstance(value, (list, tuple)):
            return type(value)(map(cls.default_convert, value))
        return value

    @classmethod
    def default_deserializer(cls, field_type: Any, value: Any) -> Any:
        if is_dataclass(field_type):
            return cls.deserialize_dataclass(field_type, value)
        if get_origin(field_type) in (list, tuple):
            sub_type_it = cycle(arg for arg in get_args(field_type) if arg is not Ellipsis)
            return get_origin(field_type)(map(cls.default_deserializer(sub_type_it(), v), value))
        return value

    @staticmethod
    def capnp_field_name(py_field_name: str) -> str:
        name_parts = iter(py_field_name.split("_"))
        return reduce(lambda n, ns: n + ns.capitalize(), name_parts, next(name_parts))

    @classmethod
    def serialize_field(cls, field_name: str, field_type: Any, value: Any) -> tuple[str, Any]:
        field_name = cls.capnp_field_name(field_name)
        if get_origin(field_type) is Annotated:
            for arg in get_args(field_type):
                if isinstance(arg, cls):
                    return arg.serialize_value(field_name, value)
        return field_name, cls.default_convert(value)

    @classmethod
    def serialize_dataclass(cls, data: object) -> dict[str, Any]:
        values: dict[str, Any] = {}
        field_types = get_type_hints(type(data), include_extras=True)
        serialized = (
            cls.serialize_field(
                field.name,
                field_types[field.name],
                getattr(data, field.name),
            )
            for field in fields(data)
        )
        for field_name, field_value in serialized:
            if not field_name:
                continue
            if field_name in values:
                values[field_name].update(field_value)
            else:
                values[field_name] = field_value
        return values
    
    @classmethod
    def deserialize_field(cls, field_name: str, field_type: Any, src: CapnpMessage) -> tuple[str, Any]:
        field_name = cls.capnp_field_name(field_name)
        if get_origin(field_type) is Annotated:
            args = iter(get_args(field_type))
            field_type = next(args)
            for arg in args:
                if isinstance(arg, cls):
                    return arg.deserialize_value(field_name, field_type, src)
        return field_name, cls.default_deserializer(field_type, getattr(src, field_name))

    @classmethod
    def deserialize_dataclass(cls, dst: type[T], src: CapnpMessage) -> T:
        values: dict[str, Any] = {}
        field_types = get_type_hints(dst, include_extras=True)
        for field in fields(dst):
            valid, value = cls.deserialize_field(field.name, field_types[field.name], src)
            if valid:
                values[field.name] = value
        return dst(**values)


class NDB:
    """Map netrunner.core.card field to a NetrunnerDB card field."""

    field_names: tuple[str, ...]
    convert: Callable | None

    def __init__(self, *field_name: str, convert: Callable | None = None, skip: bool = False):
        if len(field_name) > 1:
            assert convert

        self.field_names = field_name
        self.convert = convert

    def field_value(self, field_name: str, data: dict[str, Any]) -> Any:
        values = (data.get(field) for field in self.field_names or (field_name,))
        if self.convert:
            return self.convert(*values)
        else:
            return next(values)

    @classmethod
    def field_values_for(cls, card_type: type, data: dict[str, Any]) -> dict[str, Any]:
        field_values = {}
        field_types = get_type_hints(card_type, include_extras=True)
        for field in fields(card_type):
            field_values[field.name] = cls.get_value_for_type(
                field_types[field.name], field.name, data
            )
        return field_values

    @classmethod
    def get_value_for_type(cls, field_type: Any, field_name: str, data: dict[str, Any]) -> Any:
        if get_origin(field_type) is Annotated:
            for arg in get_args(field_type):
                if isinstance(arg, cls):
                    return arg.field_value(field_name, data)
        return data.get(field_name)
