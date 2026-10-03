"""Invented teaching data, not a bibliographic reference. No random values or fixed IDs."""

from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.db import transaction

from catalog.models import Character, Comic, Publisher, Review, Series

# Each series uses this same progression to make price/date/page lookups easy to predict.
ISSUE_DETAILS = [
    (date(2024, 11, 6), Decimal("3.99"), 24),
    (date(2025, 2, 12), Decimal("4.99"), 32),
    (date(2025, 6, 18), Decimal("6.50"), 40),
    (date(2026, 1, 7), Decimal("10.00"), 48),
    (date(2026, 3, 11), Decimal("12.50"), 64),
]
REVIEW_AUTHORS = ["Alice", "Boris", "Charlie", "Dana"]

# Each issue: (title, character names, ratings in REVIEW_AUTHORS order).
# Its position in the list determines issue_number (1..5).
SERIES_DATA = [
    {
        "publisher": "DC Comics",
        "title": "Batman",
        "issues": [
            ("Gotham at Midnight", ("Batman", "Joker"), (5, 4, 3)),
            ("The Cat's Trail", ("Batman", "Catwoman"), (4, 5)),
            ("Dark Rooftops", ("Batman", "Catwoman"), ()),
            ("Joker's Last Laugh", ("Batman", "Joker"), (2, 3, 4, 3)),
            ("Dawn over Gotham", ("Batman", "Joker", "Catwoman"), (5, 5, 4)),
        ],
    },
    {
        "publisher": "DC Comics",
        "title": "Watchmen",
        "issues": [
            ("The Broken Clock", ("Rorschach", "Doctor Manhattan"), (5, 4, 5, 4)),
            ("Footprints in the Rain", ("Rorschach", "Doctor Manhattan"), (3, 4, 3)),
            ("A Blue Horizon", ("Doctor Manhattan",), (5,)),
            ("Masks of the City", ("Rorschach", "Doctor Manhattan"), (2, 4)),
            ("Before the Final Hour", ("Rorschach", "Doctor Manhattan"), (4, 5, 4, 5)),
        ],
    },
    {
        "publisher": "Marvel Comics",
        "title": "Amazing Spider-Man",
        "issues": [
            ("Webs over Queens", ("Spider-Man", "Mary Jane"), (5, 5, 4, 4)),
            ("The Bridge Chase", ("Spider-Man", "Green Goblin"), (4, 3, 4)),
            ("Goblin Night", ("Spider-Man", "Green Goblin", "Mary Jane"), (5, 4, 5)),
            ("A Letter to Mary Jane", ("Spider-Man", "Mary Jane"), ()),
            ("The Last Web", ("Spider-Man", "Green Goblin"), (5, 5)),
        ],
    },
    {
        "publisher": "Marvel Comics",
        "title": "X-Men",
        "issues": [
            ("A New Class", ("Wolverine", "Cyclops", "Storm"), (5, 5, 4, 5)),
            ("Storm Warning", ("Cyclops", "Storm"), (5, 4)),
            ("Mutant Crossroads", ("Wolverine", "Cyclops"), (4, 4, 4)),
            ("The Silent Sentinel", ("Wolverine", "Storm"), (3, 3, 4)),
            ("Home beyond the School", ("Wolverine", "Cyclops", "Storm"), (5,)),
        ],
    },
    {
        "publisher": "Image Comics",
        "title": "Saga",
        "issues": [
            ("Escape from Landfall", ("Alana", "Marko"), (4, 5, 4)),
            ("The Forest Ship", ("Alana", "Marko"), (3, 4, 5)),
            ("Stars between Us", ("Alana", "Marko"), (5, 4)),
            ("A Quiet Planet", ("Alana", "Marko"), ()),
            ("Family under Fire", ("Alana", "Marko"), (1, 2, 3, 4)),
        ],
    },
    {
        "publisher": "Image Comics",
        "title": "Invincible",
        "issues": [
            ("First Flight", ("Mark Grayson", "Atom Eve"), (4, 4, 5)),
            ("After the Rescue", ("Mark Grayson", "Atom Eve"), (3, 4)),
            ("A Hero's Promise", ("Mark Grayson", "Atom Eve"), (5, 4, 5, 4)),
            ("City in the Sky", ("Mark Grayson", "Atom Eve"), (2,)),
            ("No Easy Victory", ("Mark Grayson", "Atom Eve"), (3, 3, 4)),
        ],
    },
    {
        "publisher": "Dark Horse Comics",
        "title": "Hellboy",
        "issues": [
            ("The Red Door", ("Hellboy", "Abe Sapien"), (4, 4, 3)),
            ("Bells in the Dark", ("Hellboy", "Liz Sherman"), (5, 4, 3, 4)),
            ("The Sunken Chapel", ("Hellboy", "Abe Sapien"), ()),
            ("Fire beneath the Hill", ("Hellboy", "Liz Sherman"), (2, 3)),
            ("The Long Way Home", ("Hellboy", "Abe Sapien", "Liz Sherman"), (5, 4, 5)),
        ],
    },
    {
        "publisher": "Dark Horse Comics",
        "title": "Black Hammer",
        "issues": [
            ("Welcome to the Farm", ("Black Hammer", "Golden Gail"), (3, 4)),
            ("The Empty Road", ("Black Hammer", "Golden Gail"), (4, 4, 5)),
            ("Echoes of Spiral City", ("Black Hammer", "Golden Gail"), (1, 3, 4, 2)),
            ("Night beyond the Fence", ("Black Hammer", "Golden Gail"), (3,)),
            ("The Way Back", ("Black Hammer", "Golden Gail"), (5, 4)),
        ],
    },
]


@transaction.atomic
def seed_demo_data():
    """Replace the entire teaching catalog atomically; preserve existing Django users."""
    # CASCADE removes series, comics, reviews and the corresponding M2M rows.
    Publisher.objects.all().delete()
    Character.objects.all().delete()

    for series_data in SERIES_DATA:
        publisher, _ = Publisher.objects.get_or_create(name=series_data["publisher"])
        series = Series.objects.create(title=series_data["title"], publisher=publisher)
        issues = zip(series_data["issues"], ISSUE_DETAILS, strict=True)
        for issue_number, (issue, details) in enumerate(issues, start=1):
            title, character_names, ratings = issue
            release_date, price, pages = details
            comic = Comic.objects.create(
                series=series,
                issue_number=issue_number,
                title=title,
                release_date=release_date,
                price=price,
                pages=pages,
            )
            for name in character_names:
                character, _ = Character.objects.get_or_create(name=name)
                comic.characters.add(character)
            for author, rating in zip(REVIEW_AUTHORS, ratings, strict=False):
                Review.objects.create(
                    comic=comic,
                    author=author,
                    rating=rating,
                    text=f"{author} rates {title}: {rating}/5.",
                )

    user, created = get_user_model().objects.get_or_create(
        username="admin", defaults={"is_staff": True, "is_superuser": True}
    )
    if created:
        user.set_password("workshop")
        user.save(update_fields=["password"])

    return {
        "publishers": Publisher.objects.count(),
        "series": Series.objects.count(),
        "comics": Comic.objects.count(),
        "characters": Character.objects.count(),
        "reviews": Review.objects.count(),
    }
