import pytest
from pynamodb.attributes import NumberAttribute, UnicodeAttribute
from pynamodb.models import Model

from pynamodb_encoder.encoder import Encoder


@pytest.fixture(scope="module", autouse=True)
def encoder() -> Encoder:
    return Encoder()


def test_encode_simple_model(encoder):
    class Pet(Model):
        name = UnicodeAttribute()
        age = NumberAttribute()

    pet = Pet(name="Garfield", age=43)

    assert encoder.encode(pet) == {"name": "Garfield", "age": 43}
