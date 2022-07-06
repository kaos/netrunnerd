from __future__ import annotations

from dataclasses import dataclass, fields, is_dataclass
from functools import reduce
from typing import Annotated, Any, Callable, get_args, get_origin, get_type_hints


@dataclass(frozen=True)
class CapAn:
    """Annotation type for serializing a dataclass field to capnp."""

    field_name: str | None = None
    convert: Callable | None = None
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

    @classmethod
    def default_convert(cls, value: Any) -> Any:
        if is_dataclass(value):
            return cls.serialize_dataclass(value)
        if isinstance(value, (list, tuple)):
            return type(value)(map(cls.default_convert, value))
        return value

    @classmethod
    def serialize_field(cls, field_name: str, field_type: Any, value: Any) -> tuple[str, Any]:
        name_parts = iter(field_name.split("_"))
        field_name = reduce(lambda n, ns: n + ns.capitalize(), name_parts, next(name_parts))
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
