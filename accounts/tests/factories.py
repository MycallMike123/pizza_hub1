import factory
from accounts.models import User
from django.contrib.auth.hashers import make_password


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    email = factory.sequence(lambda n: f'user{n}@example.com'.format(n))
    password = make_password('defaultpassword123')