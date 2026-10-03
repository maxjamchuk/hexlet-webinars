from django.db import connection
from django.test.utils import CaptureQueriesContext

from catalog.models import Comic


def run():
    # Fresh QuerySets in each section: no result cache shared between measurements.
    with CaptureQueriesContext(connection) as queries:
        comics = Comic.objects.all()
        for comic in comics:
            _ = comic.series.publisher.name
    print("=== N+1: ForeignKey chain ===")
    print(f"Comics: {len(comics)}")
    print(f"Queries: {len(queries)}")

    with CaptureQueriesContext(connection) as queries:
        comics = Comic.objects.all()
        for comic in comics:
            list(comic.characters.all())
    print("\n=== N+1: ManyToMany ===")
    print(f"Comics: {len(comics)}")
    print(f"Queries: {len(queries)}")
