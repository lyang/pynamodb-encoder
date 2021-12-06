from typing import Any, Type, TypeVar

from pynamodb.attributes import AttributeContainer

AC = TypeVar("AC", bound=AttributeContainer)


class Decoder:
    def decode(self, cls: Type[AC], data: dict[str, Any]) -> AC:
        return cls(**data)
