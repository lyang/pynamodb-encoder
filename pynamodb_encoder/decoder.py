from typing import Any, Type, TypeVar

from pynamodb.attributes import (
    Attribute,
    AttributeContainer,
    BinaryAttribute,
    DynamicMapAttribute,
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
        elif isinstance(attr, MapAttribute):
            return self.decode_map(attr, data)
        else:
            return data

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
