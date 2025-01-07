from django.apps import AppConfig


class HotelsConfig(AppConfig):
    """
    Configuration class for the 'hotels' app.

    This class is used to configure the application settings within Django.
    Specifically, it defines the app's name and the type of primary key to use.
    The 'hotels' app will manage functionality related to hotel and city data.
    """

    default_auto_field = "django.db.models.BigAutoField"

    name = "hotels"
