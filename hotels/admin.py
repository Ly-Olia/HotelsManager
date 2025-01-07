from django.contrib import admin

from .models import City, Hotel


class HotelInline(admin.TabularInline):
    """
    Inline admin interface for the Hotel model, allowing hotels to be edited
    directly within the City model's page.
    """

    model = Hotel
    extra = 1


class CityAdmin(admin.ModelAdmin):
    """
    Custom admin interface for the City model. This provides a list view of cities with
    additional information about the number of hotels associated with each city.
    """

    list_display = ("code", "name", "get_hotels_count")
    search_fields = ("name",)
    inlines = [HotelInline]

    def get_hotels_count(self, obj: City) -> int:
        """
        Returns the count of hotels associated with a particular city.
        """

        return obj.hotels.count()

    get_hotels_count.short_description = "Number of Hotels"


class HotelAdmin(admin.ModelAdmin):
    """
    Custom admin interface for the Hotel model, allowing searching for hotels by
    name or city and filtering hotels by city.
    """

    list_display = (
        "name",
        "city",
        "code",
    )  # code in this model refers to hotel code
    search_fields = ("name", "city__name")
    list_filter = ("city",)
    ordering = ("name",)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """
        Customize the foreign key field for the city to exclude the empty option
        in the hotel creation form. This ensures that a hotel cannot be created
        without selecting an associated city.
        """

        if db_field.name == "city":
            kwargs["empty_label"] = None  # Remove the '---------' empty option
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


admin.site.register(
    City, CityAdmin
)
admin.site.register(
    Hotel, HotelAdmin
)
