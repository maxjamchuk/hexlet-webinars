import pytest

from catalog.demo_data import seed_demo_data
from catalog.models import Comic


@pytest.fixture
def seeded(db, settings):
    # Speed up user creation in tests only; the real local admin uses Django's default hasher.
    settings.PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]
    return seed_demo_data()


@pytest.fixture
def batman(seeded):
    return Comic.objects.get(series__title="Batman", issue_number=1)
