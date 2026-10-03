from decimal import Decimal

import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError, connection, transaction
from django.test.utils import CaptureQueriesContext

from catalog.models import Character, Comic, Publisher, Review, Series

pytestmark = pytest.mark.django_db


@pytest.mark.parametrize("model,name", [(Publisher, "DC Comics"), (Character, "Batman")])
def test_unique_names(seeded, model, name):
    with pytest.raises(IntegrityError), transaction.atomic():
        model.objects.create(name=name)


def test_series_unique_within_publisher(seeded):
    dc = Publisher.objects.get(name="DC Comics")
    with pytest.raises(IntegrityError), transaction.atomic():
        Series.objects.create(publisher=dc, title="Batman")
    other = Publisher.objects.get(name="Image Comics")
    assert Series.objects.create(publisher=other, title="Batman").title == "Batman"


def test_issue_number_unique_within_series(batman):
    fields = {
        "issue_number": 1,
        "title": "Temporary issue",
        "release_date": batman.release_date,
        "price": Decimal("2.00"),
        "pages": 24,
    }
    with pytest.raises(IntegrityError), transaction.atomic():
        Comic.objects.create(series=batman.series, **fields)
    # The same number is allowed in another (new) series.
    series = Series.objects.create(publisher=batman.series.publisher, title="Workshop")
    assert Comic.objects.create(series=series, **fields).issue_number == 1


def test_author_unique_within_comic(batman):
    with pytest.raises(IntegrityError), transaction.atomic():
        Review.objects.create(comic=batman, author="Alice", rating=5)
    other = Comic.objects.get(series__title="Batman", issue_number=3)
    assert Review.objects.create(comic=other, author="Alice", rating=5).rating == 5


@pytest.mark.parametrize("rating", [0, 6, -1])
def test_rating_validation_and_database_constraint(batman, rating):
    review = Review(comic=batman, author="New reader", rating=rating)
    with pytest.raises(ValidationError):
        review.full_clean()
    # save/create do not call full_clean: verify independent database protection too.
    with pytest.raises(IntegrityError), transaction.atomic():
        review.save()


@pytest.mark.parametrize("rating", [1, 5])
def test_rating_boundaries_and_blank_text(batman, rating):
    review = Review(comic=batman, author="New reader", rating=rating)
    review.full_clean()
    review.save()
    assert review.text == ""


@pytest.mark.parametrize(
    "field,value",
    [("price", Decimal("0")), ("price", Decimal("-1")), ("pages", 0), ("pages", -1)],
)
def test_positive_price_and_pages(batman, field, value):
    setattr(batman, field, value)
    with pytest.raises(ValidationError):
        batman.full_clean()
    with pytest.raises(IntegrityError), transaction.atomic():
        Comic.objects.filter(series__title="Batman", issue_number=1).update(**{field: value})


def test_reverse_relations_and_m2m_add_remove(batman):
    dc = Publisher.objects.get(name="DC Comics")
    assert list(dc.series.values_list("title", flat=True)) == ["Batman", "Watchmen"]
    series = dc.series.get(title="Batman")
    assert series.comics.count() == 5
    assert batman.reviews.count() == 3
    hero = Character.objects.get(name="Batman")
    assert hero.comics.count() == 5
    assert Comic.objects.filter(characters__name="Batman").count() == 5

    catwoman = Character.objects.get(name="Catwoman")
    assert not batman.characters.filter(name="Catwoman").exists()
    batman.characters.add(catwoman)
    batman.characters.add(catwoman)  # Repeated add does not duplicate the join-table row.
    assert batman.characters.filter(name="Catwoman").count() == 1
    assert catwoman.comics.filter(series__title="Batman", issue_number=1).exists()
    batman.characters.remove(catwoman)
    assert not catwoman.comics.filter(series__title="Batman", issue_number=1).exists()


def test_str_methods_never_fetch_relations(seeded):
    objects = [
        Publisher.objects.get(name="DC Comics"),
        Series.objects.get(title="Batman"),
        Comic.objects.get(series__title="Batman", issue_number=1),
        Character.objects.get(name="Batman"),
        Review.objects.get(comic__series__title="Batman", comic__issue_number=1, author="Alice"),
    ]
    with CaptureQueriesContext(connection) as queries:
        strings = [str(obj) for obj in objects]
    assert len(queries) == 0
    assert strings == ["DC Comics", "Batman", "#1 — Gotham at Midnight", "Batman", "Alice: 5/5"]


def test_comic_delete_cascades_reviews_and_links_but_keeps_characters(batman):
    old_links = Character.comics.through.objects.count()
    batman.delete()
    assert Comic.objects.count() == 39
    assert Review.objects.count() == 97
    assert Character.objects.count() == 20
    assert Character.comics.through.objects.count() == old_links - 2
