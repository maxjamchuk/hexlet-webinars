from decimal import Decimal

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Publisher(models.Model):
    name = models.CharField(max_length=120, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Series(models.Model):
    title = models.CharField(max_length=160)
    publisher = models.ForeignKey(Publisher, on_delete=models.CASCADE, related_name="series")

    class Meta:
        ordering = ["title"]
        verbose_name_plural = "series"
        constraints = [
            models.UniqueConstraint(fields=["publisher", "title"], name="unique_publisher_series"),
        ]

    def __str__(self):
        return self.title


class Comic(models.Model):
    series = models.ForeignKey(Series, on_delete=models.CASCADE, related_name="comics")
    issue_number = models.PositiveIntegerField()
    title = models.CharField(max_length=200)
    release_date = models.DateField()
    price = models.DecimalField(
        max_digits=6, decimal_places=2, validators=[MinValueValidator(Decimal("0.01"))]
    )
    pages = models.PositiveIntegerField(validators=[MinValueValidator(1)])

    class Meta:
        ordering = ["title", "issue_number"]
        constraints = [
            models.UniqueConstraint(fields=["series", "issue_number"], name="unique_series_issue"),
            models.CheckConstraint(condition=models.Q(price__gt=0), name="comic_price_positive"),
            models.CheckConstraint(condition=models.Q(pages__gt=0), name="comic_pages_positive"),
        ]

    def __str__(self):
        return f"#{self.issue_number} — {self.title}"


class Character(models.Model):
    name = models.CharField(max_length=120, unique=True)
    comics = models.ManyToManyField(Comic, related_name="characters", blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Review(models.Model):
    comic = models.ForeignKey(Comic, on_delete=models.CASCADE, related_name="reviews")
    author = models.CharField(max_length=120)
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    text = models.TextField(blank=True)

    class Meta:
        ordering = ["author"]
        constraints = [
            models.UniqueConstraint(fields=["comic", "author"], name="unique_comic_author"),
            models.CheckConstraint(
                condition=models.Q(rating__gte=1, rating__lte=5), name="review_rating_1_to_5"
            ),
        ]

    def __str__(self):
        return f"{self.author}: {self.rating}/5"
