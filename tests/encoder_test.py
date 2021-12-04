import pytest
from pynamodb.attributes import BinaryAttribute, NumberAttribute, UnicodeAttribute
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


def test_encode_skip_none_attribute(encoder):
    class Pet(Model):
        name = UnicodeAttribute()
        age = NumberAttribute()

    pet = Pet(name="Garfield")

    assert encoder.encode(pet) == {"name": "Garfield"}


def test_encode_binary_attribute(encoder):
    class Pet(Model):
        name = UnicodeAttribute()
        age = NumberAttribute()
        weight = BinaryAttribute()

    pet = Pet(name="Garfield", age=43, weight=bytes([40]))

    assert encoder.encode(pet) == {"name": "Garfield", "age": 43, "weight": "KA=="}
