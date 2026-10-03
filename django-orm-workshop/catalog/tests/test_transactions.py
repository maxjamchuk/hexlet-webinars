import pytest
from django.core.management import call_command
from django.core.management.base import CommandError

from catalog.models import Character, Comic, Review
from catalog.scripts.transaction_demo import DEMO_TITLE, run

# Exercise real commits/rollbacks, without pytest-django's enclosing test transaction.
pytestmark = pytest.mark.django_db(transaction=True)


def test_rollback_removes_comic_review_and_m2m(seeded, capsys):
    baseline_links = Character.comics.through.objects.count()
    call_command("runscript", "transaction_demo", script_args=["rollback"])
    assert not Comic.objects.filter(title=DEMO_TITLE).exists()
    assert not Review.objects.filter(author="Workshop Reader").exists()
    assert (Comic.objects.count(), Review.objects.count()) == (40, 100)
    assert Character.comics.through.objects.count() == baseline_links
    output = capsys.readouterr().out
    assert "Transaction rolled back." in output
    assert output.count("False") == 3


def test_commit_repeat_and_rollback_after_commit(seeded, capsys):
    baseline_links = Character.comics.through.objects.count()
    for _ in range(2):
        call_command("runscript", "transaction_demo", script_args=["commit"])
        comic = Comic.objects.get(title=DEMO_TITLE)
        assert list(comic.characters.values_list("name", flat=True)) == ["Batman"]
        assert comic.reviews.get(author="Workshop Reader").rating == 5
        assert (Comic.objects.count(), Review.objects.count()) == (41, 101)
        assert Character.comics.through.objects.count() == baseline_links + 1
    output = capsys.readouterr().out
    assert output.count("Transaction committed.") == 2
    assert output.count("True") == 6

    call_command("runscript", "transaction_demo", script_args=["rollback"])
    assert (Comic.objects.count(), Review.objects.count()) == (40, 100)
    assert Character.comics.through.objects.count() == baseline_links
    assert not Comic.objects.filter(title=DEMO_TITLE).exists()


@pytest.mark.parametrize("args", [(), ("typo",), ("commit", "extra")])
def test_invalid_mode_does_not_remove_previous_commit(seeded, args):
    run("commit")
    with pytest.raises(CommandError, match="script-args"):
        run(*args)
    assert Comic.objects.filter(title=DEMO_TITLE).exists()
