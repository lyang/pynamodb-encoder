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


def test_encode_custom_map_attribute(encoder):
    class Human(MapAttribute):
        name = UnicodeAttribute()
        age = NumberAttribute()

    class Pet(Model):
        name = UnicodeAttribute()
        age = NumberAttribute()
        owner = Human()

    pet = Pet(name="Garfield", age=43, owner=Human(name="Jon", age=70))

    assert encoder.encode(pet) == {"name": "Garfield", "age": 43, "owner": {"name": "Jon", "age": 70}}


def test_encode_dynamic_map_attribute(encoder):
    class Human(DynamicMapAttribute):
        name = UnicodeAttribute()

    class Pet(Model):
        name = UnicodeAttribute()
        age = NumberAttribute()
        owner = Human()

    pet = Pet(name="Garfield", age=43, owner=Human(name="Jon", occupation="Cartoonist"))

    assert encoder.encode(pet) == {"name": "Garfield", "age": 43, "owner": {"name": "Jon", "occupation": "Cartoonist"}}


def test_encode_typed_list_attribute(encoder):
    class Pet(Model):
        name = UnicodeAttribute()
        age = NumberAttribute()
        pets = ListAttribute(of=MapAttribute)

    pet = Pet(name="Garfield", age=43, pets=[MapAttribute(name="Pooky")])

    assert encoder.encode(pet) == {"name": "Garfield", "age": 43, "pets": [{"name": "Pooky"}]}


def test_encode_polymorphic_attribute(encoder):
    class Pet(MapAttribute):
        cls = DiscriminatorAttribute()

    class Cat(Pet, discriminator="Cat"):
        name = UnicodeAttribute()

    class Dog(Pet, discriminator="Dog"):
        breed = UnicodeAttribute()

    cat = Cat(name="Garfield")
    assert encoder.encode(cat) == {"cls": "Cat", "name": "Garfield"}

    dog = Dog(breed="Terrier")
    assert encoder.encode(dog) == {"cls": "Dog", "breed": "Terrier"}


def test_encode_polymorphic_model(encoder):
    class Pet(Model):
        cls = DiscriminatorAttribute()

    class Cat(Pet, discriminator="Cat"):
        name = UnicodeAttribute()

    class Dog(Pet, discriminator="Dog"):
        breed = UnicodeAttribute()

    cat = Cat(name="Garfield")
    assert encoder.encode(cat) == {"cls": "Cat", "name": "Garfield"}

    dog = Dog(breed="Terrier")
    assert encoder.encode(dog) == {"cls": "Dog", "breed": "Terrier"}


def test_encode_complex_model(encoder):
    class Pet(DynamicMapAttribute):
        cls = DiscriminatorAttribute()
        name = UnicodeAttribute()

    class Cat(Pet, discriminator="Cat"):
        pass

    class Dog(Pet, discriminator="Dog"):
        pass

    class Human(MapAttribute):
        name = UnicodeAttribute()
        pets = ListAttribute(of=Pet)

    jon = Human(name="Jon", pets=[Cat(name="Garfield", age=43), Dog(name="Odie")])
    assert encoder.encode(jon) == {
        "name": "Jon",
        "pets": [{"cls": "Cat", "name": "Garfield", "age": 43}, {"cls": "Dog", "name": "Odie"}],
    }
