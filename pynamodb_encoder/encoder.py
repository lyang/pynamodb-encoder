from typing import Any, Type, Union

from pynamodb.attributes import (
    Attribute,
    AttributeContainer,
    BinaryAttribute,
    BinarySetAttribute,
    DiscriminatorAttribute,
    ListAttribute,
    MapAttribute,
)
from pynamodb.models import Model


class Encoder:
    def encode(self, instance: Model) -> dict[str, Any]:
        return self.encode_attributes(instance)

    def encode_attributes(self, container: AttributeContainer) -> dict[str, Any]:
        attributes = {}
        for name, attr in container.get_attributes().items():
            value = getattr(container, name)
            if value:
                attributes[name] = self.encode_attribute(attr, value)
        return attributes

    def encode_attribute(self, attr: Attribute, data: Any) -> Union[int, float, bool, str, list, dict]:
        if isinstance(attr, (BinaryAttribute, BinarySetAttribute)):
            return attr.serialize(data)
        elif isinstance(attr, DiscriminatorAttribute):
            return str(attr.get_discriminator(data))
        elif isinstance(attr, ListAttribute):
            return self.encode_list(attr, data)
        elif isinstance(attr, MapAttribute):
            return {name: data[name] for name in data}
        else:
            return data

    def encode_list(self, attr: ListAttribute, data: list) -> list:
        return [self.encode_attribute(self.coerce(attr.element_type), value) for value in data]

    def coerce(self, element_type: Union[Type[Attribute], None]) -> Attribute:
        return (element_type or Attribute)()
