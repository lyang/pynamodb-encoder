from typing import Any

from pynamodb.attributes import AttributeContainer
from pynamodb.models import Model


class Encoder:
    def encode(self, instance: Model) -> dict[str, Any]:
        return self.encode_attributes(instance)

    def encode_attributes(self, container: AttributeContainer) -> dict[str, Any]:
        return {name: getattr(container, name) for name in container.get_attributes()}
