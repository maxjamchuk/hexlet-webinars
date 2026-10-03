from datetime import date
from decimal import Decimal

from django.core.management.base import CommandError
from django.db import transaction

from catalog.models import Character, Comic, Review, Series

DEMO_TITLE = "Workshop Transaction Special"
DEMO_ISSUE_NUMBER = 1000


class DemoRollback(Exception):
    """Intentional failure after all three writes, to illustrate atomic rollback."""


def run(*args):
    if len(args) != 1 or args[0] not in {"rollback", "commit"}:
        raise CommandError("Use --script-args rollback or --script-args commit")
    mode = args[0]
    series = Series.objects.get(title="Batman", publisher__name="DC Comics")
    character = Character.objects.get(name="Batman")

    # Cleanup is intentionally BEFORE the transaction being demonstrated.
    # The previous commit must stay deleted even when this run rolls back.
    Comic.objects.filter(series=series, issue_number=DEMO_ISSUE_NUMBER, title=DEMO_TITLE).delete()

    try:
        with transaction.atomic():
            comic = Comic.objects.create(
                series=series,
                issue_number=DEMO_ISSUE_NUMBER,
                title=DEMO_TITLE,
                release_date=date(2026, 4, 1),
                price=Decimal("7.50"),
                pages=32,
            )
            comic.characters.add(character)
            Review.objects.create(comic=comic, author="Workshop Reader", rating=5)
            if mode == "rollback":
                raise DemoRollback
    except DemoRollback:
        print("Transaction rolled back.")
    else:
        print("Transaction committed.")

    demo_comics = Comic.objects.filter(series=series, issue_number=DEMO_ISSUE_NUMBER)
    print(f"Comic exists: {demo_comics.exists()}")
    print(f"Review exists: {Review.objects.filter(comic__in=demo_comics).exists()}")
    print(f"Character relation exists: {character.comics.filter(title=DEMO_TITLE).exists()}")
