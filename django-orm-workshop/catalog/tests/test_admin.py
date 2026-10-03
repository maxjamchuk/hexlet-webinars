from decimal import Decimal

import pytest
from django.urls import reverse

from catalog.models import Character, Comic, Publisher, Review, Series

pytestmark = pytest.mark.django_db


@pytest.mark.parametrize("model", [Publisher, Series, Comic, Character, Review])
def test_admin_lists_and_change_forms(seeded, client, model):
    assert client.login(username="admin", password="workshop")
    name = model._meta.model_name
    response = client.get(reverse(f"admin:catalog_{name}_changelist"))
    assert response.status_code == 200
    # Resolve an actual object, never assume a numeric primary key.
    obj = model.objects.first()
    response = client.get(reverse(f"admin:catalog_{name}_change", args=[obj.pk]))
    assert response.status_code == 200


@pytest.mark.parametrize("search", ["Batman", "X-Men", "Spider-Man"])
def test_admin_searches_series_names(seeded, client, search):
    assert client.login(username="admin", password="workshop")
    response = client.get(reverse("admin:catalog_comic_changelist"), {"q": search})
    assert response.status_code == 200
    comics = list(response.context["cl"].queryset)
    assert len(comics) == 5
    assert all(search in comic.series.title for comic in comics)


def test_admin_edit_and_validation(batman, client):
    assert client.login(username="admin", password="workshop")
    url = reverse("admin:catalog_comic_change", args=[batman.pk])
    data = {
        "series": batman.series_id,
        "issue_number": batman.issue_number,
        "title": batman.title,
        "release_date": batman.release_date.isoformat(),
        "price": "8.99",
        "pages": batman.pages,
        "_save": "Save",
    }
    assert client.post(url, data).status_code == 302
    batman.refresh_from_db()
    assert batman.price == Decimal("8.99")
    data["price"] = "0"
    response = client.post(url, data)
    assert response.status_code == 200
    assert "price" in response.context["adminform"].form.errors
    batman.refresh_from_db()
    assert batman.price == Decimal("8.99")
