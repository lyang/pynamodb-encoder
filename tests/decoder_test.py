import pytest
from pynamodb.attributes import (
    BinaryAttribute,
    DiscriminatorAttribute,
    DynamicMapAttribute,
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


def test_decode_simple_model(decoder: Decoder):
    class Pet(Model):
        name = UnicodeAttribute()
        age = NumberAttribute()

    pet = decoder.decode(Pet, {"name": "Garfield", "age": 43})

    assert pet.name == "Garfield"
    assert pet.age == 43


def test_decode_skip_none_attribute(decoder: Decoder):
    class Pet(Model):
        name = UnicodeAttribute()
        age = NumberAttribute()

    pet = decoder.decode(Pet, {"name": "Garfield"})
    assert pet.name == "Garfield"
    assert pet.age is None


def test_decode_binary_attribute(decoder: Decoder):
    class Pet(Model):
        name = UnicodeAttribute()
        age = NumberAttribute()
        weight = BinaryAttribute()

    pet = decoder.decode(Pet, {"name": "Garfield", "age": 43, "weight": "KA=="})

    assert pet.name == "Garfield"
    assert pet.weight == bytes([40])


def test_decode_list_attribute(decoder: Decoder):
    class Pet(Model):
        name = UnicodeAttribute()
        age = NumberAttribute()
        likes = ListAttribute()

    pet = decoder.decode(Pet, {"name": "Garfield", "age": 43, "likes": ["lasagna"]})

    assert pet.name == "Garfield"
    assert pet.age == 43
    assert pet.likes == ["lasagna"]


def test_decode_map_attribute(decoder: Decoder):
    class Pet(Model):
        name = UnicodeAttribute()
        age = NumberAttribute()
        tags = MapAttribute()

    pet = decoder.decode(Pet, {"name": "Garfield", "age": 43, "tags": {"breed": "Tabby"}})

    assert pet.name == "Garfield"
    assert pet.age == 43
    assert isinstance(pet.tags, MapAttribute)
    assert pet.tags["breed"] == "Tabby"


def test_decode_custom_map_attribute(decoder: Decoder):
    class Human(MapAttribute):
        name = UnicodeAttribute()
        age = NumberAttribute()

    class Pet(Model):
        name = UnicodeAttribute()
        age = NumberAttribute()
        owner = Human()

    pet = decoder.decode(Pet, {"name": "Garfield", "age": 43, "owner": {"name": "Jon", "age": 70, "job": "Cartoonist"}})

    assert pet.name == "Garfield"
    assert pet.age == 43
    assert isinstance(pet.owner, Human)
    assert pet.owner["name"] == "Jon"
    assert pet.owner["age"] == 70


def test_decode_dynamic_map_attribute(decoder: Decoder):
    class Human(DynamicMapAttribute):
        name = UnicodeAttribute()
        age = NumberAttribute()

    class Pet(Model):
        name = UnicodeAttribute()
        age = NumberAttribute()
        owner = Human()

    pet = decoder.decode(Pet, {"name": "Garfield", "age": 43, "owner": {"name": "Jon", "age": 70, "job": "Cartoonist"}})

    assert pet.name == "Garfield"
    assert pet.age == 43
    assert isinstance(pet.owner, Human)
    assert pet.owner["name"] == "Jon"
    assert pet.owner["age"] == 70
    assert pet.owner["job"] == "Cartoonist"


def test_decode_typed_list_attribute(decoder: Decoder):
    class Pet(MapAttribute):
        name = UnicodeAttribute()
        age = NumberAttribute()

    class Human(Model):
        name = UnicodeAttribute()
        age = NumberAttribute()
        pets = ListAttribute(of=Pet)

    jon = decoder.decode(Human, {"name": "Jon", "age": 70, "pets": [{"name": "Garfield", "age": 43}]})

    assert jon.name == "Jon"
    assert jon.age == 70
    assert isinstance(jon.pets, list)
    assert len(jon.pets) == 1
    assert isinstance(jon.pets[0], Pet)
    assert jon.pets[0]["name"] == "Garfield"


def test_decode_polymorphic_attribute(decoder: Decoder):
    class Pet(MapAttribute):
        cls = DiscriminatorAttribute()

    class Cat(Pet, discriminator="Cat"):
        name = UnicodeAttribute()

    class Dog(Pet, discriminator="Dog"):
        breed = UnicodeAttribute()

    cat = decoder.decode_container(Pet, {"cls": "Cat", "name": "Garfield"})

    assert isinstance(cat, Cat)
    assert cat.name == "Garfield"

    dog = decoder.decode_container(Pet, {"cls": "Dog", "breed": "Terrier"})
    assert isinstance(dog, Dog)
    assert dog.breed == "Terrier"


def test_decode_polymorphic_model(decoder: Decoder):
    class Pet(Model):
        cls = DiscriminatorAttribute()

    class Cat(Pet, discriminator="Cat"):
        name = UnicodeAttribute()

    class Dog(Pet, discriminator="Dog"):
        breed = UnicodeAttribute()

    cat = decoder.decode(Pet, {"cls": "Cat", "name": "Garfield"})

    assert isinstance(cat, Cat)
    assert cat.name == "Garfield"

    dog = decoder.decode(Pet, {"cls": "Dog", "breed": "Terrier"})
    assert isinstance(dog, Dog)
    assert dog.breed == "Terrier"


def test_decode_complex_model(decoder: Decoder):
    class Pet(DynamicMapAttribute):
        cls = DiscriminatorAttribute()

    class Cat(Pet, discriminator="Cat"):
        name = UnicodeAttribute()

    class Dog(Pet, discriminator="Dog"):
        breed = UnicodeAttribute()

    class Human(Model):
        name = UnicodeAttribute()
        age = NumberAttribute()
        pets = ListAttribute(of=Pet)

    jon = decoder.decode(
        Human,
        {
            "name": "Jon",
            "age": 70,
            "pets": [{"cls": "Cat", "name": "Garfield"}, {"cls": "Dog", "breed": "Terrier"}],
        },
    )

    assert jon.name == "Jon"
    assert jon.age == 70
    assert isinstance(jon.pets, list)
    assert len(jon.pets) == 2
    assert isinstance(jon.pets[0], Cat)
    assert jon.pets[0].name == "Garfield"
    assert isinstance(jon.pets[1], Dog)
    assert jon.pets[1].breed == "Terrier"
