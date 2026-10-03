from django.db import connection
from django.test.utils import CaptureQueriesContext

from catalog.models import Comic


def run():
    with CaptureQueriesContext(connection) as queries:
        comics = Comic.objects.select_related("series__publisher")
        for comic in comics:
            _ = comic.series.publisher.name
    print("=== select_related ===")
    print(f"Comics: {len(comics)}")
    print(f"Queries: {len(queries)}")

    with CaptureQueriesContext(connection) as queries:
        comics = Comic.objects.prefetch_related("characters")
        for comic in comics:
            list(comic.characters.all())
    print("\n=== prefetch_related ===")
    print(f"Comics: {len(comics)}")
    print(f"Queries: {len(queries)}")
