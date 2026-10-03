from unittest.mock import patch

import pytest
from django.contrib.auth import get_user_model
from django.db.models import Count

from catalog.demo_data import seed_demo_data
from catalog.models import Character, Comic, Publisher, Review, Series

pytestmark = pytest.mark.django_db

EXPECTED_COUNTS = {"publishers": 4, "series": 8, "comics": 40, "characters": 20, "reviews": 100}


def catalog_snapshot():
    """Compare every logical field and relation without assuming any primary keys."""
    return {
        "publishers": list(Publisher.objects.order_by("name").values_list("name", flat=True)),
        "series": list(Series.objects.order_by("title").values_list("publisher__name", "title")),
        "characters": list(Character.objects.order_by("name").values_list("name", flat=True)),
        "comics": list(
            Comic.objects.order_by("series__title", "issue_number").values_list(
                "series__publisher__name",
                "series__title",
                "issue_number",
                "title",
                "release_date",
                "price",
                "pages",
            )
        ),
        "reviews": list(
            Review.objects.order_by(
                "comic__series__title", "comic__issue_number", "author"
            ).values_list("comic__series__title", "comic__issue_number", "author", "rating", "text")
        ),
        "links": list(
            Character.objects.order_by(
                "name", "comics__series__title", "comics__issue_number"
            ).values_list("name", "comics__series__title", "comics__issue_number")
        ),
    }


def test_seed_counts_and_review_distribution(seeded):
    assert seeded == EXPECTED_COUNTS
    assert set(Publisher.objects.values_list("name", flat=True)) == {
        "DC Comics",
        "Marvel Comics",
        "Image Comics",
        "Dark Horse Comics",
    }
    assert set(Series.objects.annotate(n=Count("comics")).values_list("n", flat=True)) == {5}
    assert set(Comic.objects.annotate(n=Count("reviews")).values_list("n", flat=True)) == {
        0,
        1,
        2,
        3,
        4,
    }
    assert set(Review.objects.values_list("rating", flat=True)) == {1, 2, 3, 4, 5}
    assert Comic.objects.annotate(n=Count("characters")).filter(n__gte=2).count() == 39


def test_seed_recreates_identical_logical_catalog_and_removes_edits(seeded):
    baseline = catalog_snapshot()
    Comic.objects.filter(series__title="Batman", issue_number=1).update(title="Edited in Admin")
    Publisher.objects.create(name="Temporary publisher")
    Character.objects.create(name="Temporary character")
    assert seed_demo_data() == EXPECTED_COUNTS
    assert catalog_snapshot() == baseline
    assert seed_demo_data() == EXPECTED_COUNTS
    assert catalog_snapshot() == baseline


def test_seed_preserves_users_and_existing_admin_password(seeded):
    users = get_user_model().objects
    admin = users.get(username="admin")
    assert admin.is_staff and admin.is_superuser and admin.check_password("workshop")
    admin.set_password("changed-by-teacher")
    admin.save()
    student = users.create_user(username="student", password="local-student")
    original_users = list(users.order_by("username").values())
    seed_demo_data()
    assert list(users.order_by("username").values()) == original_users
    admin.refresh_from_db()
    student.refresh_from_db()
    assert admin.check_password("changed-by-teacher")
    assert student.check_password("local-student")


def test_seed_failure_rolls_back_deletion_and_partial_inserts(seeded):
    baseline = catalog_snapshot()
    original_save = Comic.save

    def fail_on_second_issue(comic, *args, **kwargs):
        if comic.issue_number == 2:
            raise RuntimeError("Simulated failure halfway through reset")
        return original_save(comic, *args, **kwargs)

    with patch.object(Comic, "save", fail_on_second_issue):
        with pytest.raises(RuntimeError, match="Simulated failure"):
            seed_demo_data()
    assert catalog_snapshot() == baseline
    assert get_user_model().objects.get(username="admin").check_password("workshop")
