# models.py
# This file contains the definitions for the models in the 'hotels' app.
# Models define the structure of the database and any relationships between data entities.
from __future__ import annotations

from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.exceptions import ValidationError
from django.db import models


class City(models.Model):
    """
    Represents a city in which hotels are located.
    Stores information such as the city's unique code and name.
    A City can have many associated Hotels.
    """

    # A unique code to identify the city.
    code = models.CharField(max_length=10, unique=True, primary_key=True)
    # The name of the city.
    name = models.CharField(max_length=100)

    class Meta:
        verbose_name_plural = "Cities"

    def __str__(self) -> str:
        """
        String representation of the City object, returning its name.
        This is used when a City object is printed or logged.
        """

        return self.name


class Hotel(models.Model):
    """
    Represents a hotel located in a specific city.
    Stores information such as the hotel's unique code, name, and the city it belongs to.
    A Hotel belongs to exactly one City.
    """

    # The unique code to identify the hotel.
    code = models.CharField(max_length=10, unique=True)
    # The name of the hotel.
    name = models.CharField(max_length=200)
    # The foreign key to the City model, indicating the city the hotel is located in.
    city = models.ForeignKey(
        "City", on_delete=models.CASCADE, related_name="hotels"
    )

    def save(self, *args, **kwargs) -> None:
        """
        Custom save method to ensure the hotel is linked to an existing city.
        """

        # Check if the city exists
        if not City.objects.filter(code=self.city_id).exists():
            raise ValidationError(
                f"City with code {self.city_id} does not exist."
            )
        # Call the parent save method to save the hotel object.
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        """
        String representation of the Hotel object, returning its name.
        This is used when a Hotel object is printed or logged.
        """

        return self.name


class UserManager(BaseUserManager):
    """
    Custom manager for the 'User' model.
    Contains methods for creating regular users and superusers.
    """

    def create_user(
        self, username, email, password=None, **extra_fields
    ) -> User:
        """
        Create and return a regular user with an email, username, and password.
        """

        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(
        self, username, email, password=None, **extra_fields
    ) -> User:
        """
        Create and return a superuser with an email, password, and extra fields.
        The superuser is granted staff and superuser privileges by default.
        """

        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        return self.create_user(username, email, password, **extra_fields)


class User(AbstractUser):
    """
    Custom User model that extends the base Django user model.
    Adds additional fields like 'city' (linked to the City model) and 'role' to define the user's role (e.g., manager).
    """

    # The city the user is associated with, linked to the City model.
    city = models.ForeignKey(
        "hotels.City", on_delete=models.SET_NULL, null=True, blank=True
    )
    # The role of the user (e.g., 'manager').
    role = models.CharField(max_length=50, default="manager")

    # Use the custom manager for creating users
    objects = UserManager()

    def __str__(self) -> str:
        """
        String representation of the User object, returning its username.
        This is used when a User object is printed or logged.
        """

        return self.username
