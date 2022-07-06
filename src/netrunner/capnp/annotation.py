from __future__ import annotations

from dataclasses import dataclass, fields
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
        if self.group:
            return self.group, {field_name: value}
        return field_name, value

    @classmethod
    def serialize_field(cls, field_name: str, field_type: Any, value: Any) -> tuple[str, Any]:
        name_parts = iter(field_name.split("_"))
        field_name = reduce(lambda n, ns: n + ns.capitalize(), name_parts, next(name_parts))
        if get_origin(field_type) is Annotated:
            for arg in get_args(field_type):
                if isinstance(arg, cls):
                    return arg.serialize_value(field_name, value)
        return field_name, value

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
