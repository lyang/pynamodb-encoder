from typing import Any, Union

from pynamodb.attributes import (
    Attribute,
    AttributeContainer,
    BinaryAttribute,
    BinarySetAttribute,
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

    def encode_attribute(self, attr: Attribute, data: Any) -> Union[int, float, bool, str, dict]:
        if isinstance(attr, (BinaryAttribute, BinarySetAttribute)):
            return attr.serialize(data)
        else:
            return data
