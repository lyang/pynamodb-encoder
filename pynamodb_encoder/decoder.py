from typing import Any, Type, TypeVar, Union

from pynamodb.attributes import (
    Attribute,
    AttributeContainer,
    BinaryAttribute,
    DynamicMapAttribute,
    ListAttribute,
    MapAttribute,
)

AC = TypeVar("AC", bound=AttributeContainer)


class Decoder:
    def decode(self, cls: Type[AC], data: dict[str, Any]) -> AC:
        attributes = {}
        for name, attr in cls.get_attributes().items():
            if name in data:
                attributes[name] = self.decode_attribute(attr, data[name])
        return cls(**attributes)

    def decode_attribute(self, attr: Attribute, data):
        if isinstance(attr, BinaryAttribute):
            return attr.deserialize(data)
        elif isinstance(attr, ListAttribute):
            return self.decode_list(attr, data)
        elif isinstance(attr, MapAttribute):
            return self.decode_map(attr, data)
        else:
            return data

    def decode_list(self, attr: ListAttribute, data: list) -> list:
        return [self.decode_attribute(self.coerce(attr.element_type), value) for value in data]

    def coerce(self, element_type: Union[Type[Attribute], None]) -> Attribute:
        return (element_type or Attribute)()

    def decode_map(self, attr: MapAttribute, data: dict[str, Any]):
        if type(attr) == MapAttribute:
            return data
        elif isinstance(attr, DynamicMapAttribute):
            decoded = {}
            attributes = attr.get_attributes()
            for name, value in data.items():
                if name in attributes:
                    decoded[name] = self.decode_attribute(attributes[name], value)
                else:
                    decoded[name] = value
            return decoded
        else:
            return self.decode(type(attr), data)
