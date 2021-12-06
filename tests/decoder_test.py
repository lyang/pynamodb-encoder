import pytest
from pynamodb.attributes import (
    BinaryAttribute,
    ListAttribute,
    MapAttribute,
    NumberAttribute,
    UnicodeAttribute,
)
from pynamodb.models import Model

from pynamodb_encoder.decoder import Decoder


@pytest.fixture(scope="module", autouse=True)
def decoder() -> Decoder:
    return Decoder()


def test_decode_simple_model(decoder):
    class Pet(Model):
        name = UnicodeAttribute()
        age = NumberAttribute()

    pet = decoder.decode(Pet, {"name": "Garfield", "age": 43})

    assert pet.name == "Garfield"
    assert pet.age == 43


def test_decode_skip_none_attribute(decoder):
    class Pet(Model):
        name = UnicodeAttribute()
        age = NumberAttribute()

    pet = decoder.decode(Pet, {"name": "Garfield"})
    assert pet.name == "Garfield"
    assert pet.age is None


def test_decode_binary_attribute(decoder):
    class Pet(Model):
        name = UnicodeAttribute()
        age = NumberAttribute()
        weight = BinaryAttribute()

    pet = decoder.decode(Pet, {"name": "Garfield", "age": 43, "weight": "KA=="})

    assert pet.name == "Garfield"
    assert pet.weight == bytes([40])


def test_decode_list_attribute(decoder):
    class Pet(Model):
        name = UnicodeAttribute()
        age = NumberAttribute()
        likes = ListAttribute()

    pet = decoder.decode(Pet, {"name": "Garfield", "age": 43, "likes": ["lasagna"]})

    assert pet.name == "Garfield"
    assert pet.age == 43
    assert pet.likes == ["lasagna"]


def test_decode_map_attribute(decoder):
    class Pet(Model):
        name = UnicodeAttribute()
        age = NumberAttribute()
        tags = MapAttribute()

    pet = decoder.decode(Pet, {"name": "Garfield", "age": 43, "tags": {"breed": "Tabby"}})

    assert pet.name == "Garfield"
    assert pet.age == 43
    assert pet.tags["breed"] == "Tabby"
