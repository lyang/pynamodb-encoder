from typing import Any, Type, TypeVar

from pynamodb.attributes import Attribute, AttributeContainer, BinaryAttribute

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
        else:
            return data
