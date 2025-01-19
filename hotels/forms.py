# forms.py
# This file contains the forms for user registration and hotel management.
# The forms are used to handle user input and validate data before it's saved to the database.

from django import forms
from django.contrib.auth.forms import UserCreationForm

from hotels.models import City, Hotel, User


class CustomUserCreationForm(UserCreationForm):
    """
    A custom form for user registration, extending Django's built-in UserCreationForm.
    This form captures additional fields like 'city' to provide more context about the user,
    particularly for users who are hotel managers.
    """

    city = forms.ModelChoiceField(
        queryset=City.objects.all(),  # Query to get all available cities
        empty_label=None,  # Removes the default "--------" option in the dropdown
        label="City",  # Label to display on the form
        help_text="Select the city you are managing hotels in.",
    )

    class Meta:
        """
        Metadata for the user registration form.
        Specifies the model and fields to be used in the form.
        """

        model = User
        fields = ("username", "email", "password1", "password2", "city")


class HotelForm(forms.ModelForm):
    """
    Form for creating or editing a hotel. It is designed to allow hotel managers
    to modify hotel information, specifically 'name' and 'code', without altering other fields.
    """

    class Meta:
        """
        Metadata for the hotel management form.
        Specifies the model and fields to be used in the form.
        """

        model = Hotel
        fields = ("name", "code")
