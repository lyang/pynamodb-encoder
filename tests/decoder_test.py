import pytest
from pynamodb.attributes import NumberAttribute, UnicodeAttribute
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
