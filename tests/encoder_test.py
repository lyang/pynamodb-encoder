import pytest
from pynamodb.attributes import (
    BinaryAttribute,
    ListAttribute,
    MapAttribute,
    NumberAttribute,
    UnicodeAttribute,
)
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


def test_encode_list_attribute(encoder):
    class Pet(Model):
        name = UnicodeAttribute()
        age = NumberAttribute()
        likes = ListAttribute()

    pet = Pet(name="Garfield", age=43, likes=["lasagna"])

    assert encoder.encode(pet) == {"name": "Garfield", "age": 43, "likes": ["lasagna"]}


def test_encode_map_attribute(encoder):
    class Pet(Model):
        name = UnicodeAttribute()
        age = NumberAttribute()
        tags = MapAttribute()

    pet = Pet(name="Garfield", age=43, tags={"breed": "Tabby"})

    assert encoder.encode(pet) == {"name": "Garfield", "age": 43, "tags": {"breed": "Tabby"}}


def test_encode_typed_list_attribute(encoder):
    class Pet(Model):
        name = UnicodeAttribute()
        age = NumberAttribute()
        pets = ListAttribute(of=MapAttribute)

    pet = Pet(name="Garfield", age=43, pets=[MapAttribute(name="Pooky")])

    assert encoder.encode(pet) == {"name": "Garfield", "age": 43, "pets": [{"name": "Pooky"}]}
