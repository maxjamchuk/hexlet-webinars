from decimal import Decimal
from io import StringIO

import pytest
from django.core.management import call_command
from django.db import connection
from django.db.models import Avg, Count, F, Q
from django.test.utils import CaptureQueriesContext

from catalog.models import Comic, Review

pytestmark = pytest.mark.django_db


@pytest.mark.parametrize(
    "lookup,count",
    [
        ({"price__lt": 5}, 16),
        ({"price__lte": 5}, 16),
        ({"price__gt": 10}, 8),
        ({"price__gte": 10}, 16),
        ({"title__icontains": "night"}, 3),
        ({"release_date__year": 2025}, 16),
        ({"series__title__in": ["Batman", "X-Men"]}, 10),
        ({"reviews__isnull": True}, 4),
        ({"price__lt": 10, "pages__gte": 30}, 16),
    ],
)
def test_documented_lookups(seeded, lookup, count):
    assert Comic.objects.filter(**lookup).count() == count


def test_get_exclude_order_and_limit(seeded):
    assert Comic.objects.get(series__title="Batman", issue_number=1).title == "Gotham at Midnight"
    with pytest.raises(Comic.DoesNotExist):
        Comic.objects.get(series__title="Batman", issue_number=999)
    with pytest.raises(Comic.MultipleObjectsReturned):
        Comic.objects.get(series__title="Batman")
    assert Comic.objects.exclude(series__publisher__name="Marvel Comics").count() == 30
    comics = list(Comic.objects.order_by("-release_date", "series__title")[:5])
    assert len(comics) == 5
    assert all(comic.issue_number == 5 for comic in comics)
    assert "LIMIT 5" in str(Comic.objects.order_by("-release_date")[:5].query)


def test_queryset_is_lazy_and_caches_results(seeded):
    with CaptureQueriesContext(connection) as queries:
        qs = Comic.objects.filter(price__lt=10)
        assert len(queries) == 0
        assert "SELECT" in str(qs.query)
        assert len(queries) == 0
        first = list(qs)
        assert len(queries) == 1
        assert list(qs) == first
        assert len(queries) == 1
    assert len(first) == 24


def test_aggregate_and_annotate_include_zero_reviews(seeded):
    result = Review.objects.aggregate(reviews_count=Count("id"), average_rating=Avg("rating"))
    assert result["reviews_count"] == 100
    assert result["average_rating"] == pytest.approx(3.94)
    qs = Comic.objects.annotate(
        reviews_count=Count("reviews"), average_rating=Avg("reviews__rating")
    )
    empty = qs.get(series__title="Batman", issue_number=3)
    assert empty.reviews_count == 0 and empty.average_rating is None
    sql = str(qs.filter(reviews_count__gte=3).query)
    assert "GROUP BY" in sql and "HAVING" in sql


def test_final_query_exact_order_averages_and_two_queries(seeded):
    comics = (
        Comic.objects.filter(series__publisher__name="Marvel Comics")
        .annotate(reviews_count=Count("reviews"), average_rating=Avg("reviews__rating"))
        .filter(reviews_count__gte=3, average_rating__gte=4)
        .select_related("series__publisher")
        .prefetch_related("characters")
        .order_by("-average_rating")
    )
    with CaptureQueriesContext(connection) as queries:
        rows = [
            (
                comic.series.title,
                comic.issue_number,
                comic.average_rating,
                comic.reviews_count,
                comic.series.publisher.name,
                [character.name for character in comic.characters.all()],
            )
            for comic in comics
        ]
    assert len(queries) == 2
    assert [(row[0], row[1]) for row in rows] == [
        ("X-Men", 1),
        ("Amazing Spider-Man", 3),
        ("Amazing Spider-Man", 1),
        ("X-Men", 3),
    ]
    assert [row[2] for row in rows] == pytest.approx([4.75, 14 / 3, 4.5, 4.0])
    assert [row[3] for row in rows] == [4, 3, 4, 3]
    assert all(row[4] == "Marvel Comics" and len(row[5]) >= 2 for row in rows)


@pytest.mark.parametrize("optimized,expected", [(False, 81), (True, 1)])
def test_fk_chain_query_count(seeded, optimized, expected):
    comics = Comic.objects.all()
    if optimized:
        comics = comics.select_related("series__publisher")
    with CaptureQueriesContext(connection) as queries:
        names = [comic.series.publisher.name for comic in comics]
    assert len(names) == 40
    assert len(queries) == expected


@pytest.mark.parametrize("optimized,expected", [(False, 41), (True, 2)])
def test_m2m_query_count(seeded, optimized, expected):
    comics = Comic.objects.all()
    if optimized:
        comics = comics.prefetch_related("characters")
    with CaptureQueriesContext(connection) as queries:
        characters = [list(comic.characters.all()) for comic in comics]
    assert len(characters) == 40
    assert all(characters)
    assert len(queries) == expected


@pytest.mark.parametrize("script,counts", [("n_plus_one", [81, 41]), ("optimized_queries", [1, 2])])
def test_runscript_discovery_and_measured_output(seeded, capsys, script, counts):
    call_command("runscript", script)
    output = capsys.readouterr().out
    assert output.count("Comics: 40") == 2
    assert [
        int(line.split(": ")[1]) for line in output.splitlines() if line.startswith("Queries:")
    ] == counts


def test_shell_plus_autoimports_and_print_sql(seeded, capsys):
    output = StringIO()
    call_command(
        "shell_plus",
        command="print([m.objects.count() for m in (Publisher, Series, Comic, Character, Review)])",
        print_sql=True,
        stdout=output,
    )
    text = capsys.readouterr().out + output.getvalue()
    assert "[4, 8, 40, 20, 100]" in text
    assert "SELECT" in text


def test_optional_q_f_values(batman):
    assert (
        Comic.objects.filter(Q(title__icontains="night") | Q(title__icontains="dark")).count() == 5
    )
    original = batman.price
    Comic.objects.filter(series__title="Batman", issue_number=1).update(price=F("price") + 1)
    batman.refresh_from_db()
    assert batman.price == original + Decimal("1.00")
    row = Comic.objects.values("title", "series__title", "series__publisher__name").get(
        series__title="Batman", issue_number=1
    )
    assert row == {
        "title": "Gotham at Midnight",
        "series__title": "Batman",
        "series__publisher__name": "DC Comics",
    }
