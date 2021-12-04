from typing import Any, Type, Union

from pynamodb.attributes import (
    Attribute,
    AttributeContainer,
    BinaryAttribute,
    BinarySetAttribute,
    DiscriminatorAttribute,
    DynamicMapAttribute,
    ListAttribute,
    MapAttribute,
)
from pynamodb.models import Model


class Encoder:
    def encode(self, instance: Model) -> dict[str, Any]:
        return self.encode_attributes(instance)

    def encode_attributes(self, container: AttributeContainer) -> dict[str, Any]:
        encoded = {}
        for name, attr in container.get_attributes().items():
            value = getattr(container, name)
            if value:
                encoded[name] = self.encode_attribute(attr, value)
        return encoded

    def encode_attribute(self, attr: Attribute, data: Any) -> Union[int, float, bool, str, list, dict]:
        if isinstance(attr, (BinaryAttribute, BinarySetAttribute)):
            return attr.serialize(data)
        elif isinstance(attr, DiscriminatorAttribute):
            return str(attr.get_discriminator(data))
        elif isinstance(attr, ListAttribute):
            return self.encode_list(attr, data)
        elif isinstance(attr, MapAttribute):
            return self.encode_map(attr, data)
        else:
            return data

    def encode_list(self, attr: ListAttribute, data: list) -> list:
        return [self.encode_attribute(self.coerce(attr.element_type), value) for value in data]

    def coerce(self, element_type: Union[Type[Attribute], None]) -> Attribute:
        return (element_type or Attribute)()

    def encode_map(self, attr: MapAttribute, data: MapAttribute) -> dict:
        if type(attr) == MapAttribute:
            return {name: data[name] for name in data}
        elif isinstance(attr, DynamicMapAttribute):
            encoded = {}
            attributes = attr.get_attributes()
            for name in data:
                value = getattr(data, name)
                if name in attributes:
                    encoded[name] = self.encode_attribute(attributes[name], value)
                else:
                    encoded[name] = value
            return encoded
        else:
            return self.encode_attributes(data)
