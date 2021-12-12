# pynamodb-encoder ![Build](https://github.com/lyang/pynamodb-encoder/actions/workflows/build.yml/badge.svg) ![CodeQL](https://github.com/lyang/pynamodb-encoder/actions/workflows/codeql-analysis.yml/badge.svg) [![codecov](https://codecov.io/gh/lyang/pynamodb-encoder/branch/main/graph/badge.svg?token=P51YVL86N8)](https://codecov.io/gh/lyang/pynamodb-encoder) [![Maintainability](https://api.codeclimate.com/v1/badges/1e5c3b615dedb2bffb0c/maintainability)](https://codeclimate.com/github/lyang/pynamodb-encoder/maintainability)

## Introduction
`pynamodb-encoder` provides helper classes that can convert [PynamoDB](https://github.com/pynamodb/PynamoDB) `Model` objects into `JSON` serializable `dict`. It can also decode such `dict` back into those `Model` objects. [Polymorphic](https://pynamodb.readthedocs.io/en/latest/polymorphism.html) models and attributes are also supported.

## Examples
```python
def test_encode_complex_model(encoder: Encoder):
    class Pet(DynamicMapAttribute):
        cls = DiscriminatorAttribute()
        name = UnicodeAttribute()

    class Cat(Pet, discriminator="Cat"):
        pass

    class Dog(Pet, discriminator="Dog"):
        pass

    class Human(Model):
        name = UnicodeAttribute()
        pets = ListAttribute(of=Pet)

    jon = Human(name="Jon", pets=[Cat(name="Garfield", age=43), Dog(name="Odie")])
    assert encoder.encode(jon) == {
        "name": "Jon",
        "pets": [{"cls": "Cat", "name": "Garfield", "age": 43}, {"cls": "Dog", "name": "Odie"}],
    }

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
```

More examples can be found in [encoder_test.py](tests/encoder_test.py) and [decoder_test.py](tests/decoder_test.py)
