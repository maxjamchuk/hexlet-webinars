from django.contrib import admin

from catalog.models import Character, Comic, Publisher, Review, Series

admin.site.site_header = "Comic Catalog — ORM Workshop"
admin.site.site_title = "Comic Catalog"
admin.site.index_title = "Состояние учебной базы"


@admin.register(Publisher)
class PublisherAdmin(admin.ModelAdmin):
    list_display = ["name"]
    search_fields = ["name"]


@admin.register(Series)
class SeriesAdmin(admin.ModelAdmin):
    list_display = ["title", "publisher"]
    list_filter = ["publisher"]
    search_fields = ["title"]


@admin.register(Comic)
class ComicAdmin(admin.ModelAdmin):
    list_display = ["title", "issue_number", "series", "release_date", "price", "pages"]
    list_filter = ["series__publisher", "series", "release_date"]
    search_fields = ["title", "series__title", "=issue_number"]
    ordering = ["series__title", "issue_number"]
    list_select_related = ["series"]


@admin.register(Character)
class CharacterAdmin(admin.ModelAdmin):
    list_display = ["name"]
    search_fields = ["name"]
    filter_horizontal = ["comics"]


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ["comic", "author", "rating"]
    list_filter = ["rating"]
    search_fields = ["author", "comic__title", "comic__series__title"]
