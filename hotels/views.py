# hotels/views.py

from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.decorators import method_decorator

from .forms import CustomUserCreationForm, HotelForm
from .models import City, Hotel, User
from django.views import View


def is_manager(user: User) -> bool:
    return (
            user.is_authenticated
            and user.role == "manager"
    )


def manager_required(function):
    """
    Decorator to ensure the user is a manager.
    """

    def wrapper(request, *args, **kwargs):
        if not is_manager(request.user):
            return redirect("home")
        return function(request, *args, **kwargs)

    return wrapper


class CityHotelsManagerView(LoginRequiredMixin, View):
    """
    Class-based view for managers to view and add hotels in their assigned city.
    """

    @method_decorator(manager_required)
    def get(self, request: HttpRequest) -> HttpResponse:
        user = request.user

        city = user.city
        hotels = Hotel.objects.filter(city=city)
        form = HotelForm()  # Create an empty form

        return render(
            request,
            "manager_hotels.html",
            {
                "selected_city": city,
                "hotels": hotels,
                "manager": user.username,
                "form": form,
            },
        )

    @method_decorator(manager_required)
    def post(self, request: HttpRequest) -> HttpResponse:
        user = request.user

        city = user.city
        form = HotelForm(request.POST)
        if form.is_valid():
            hotel = form.save(commit=False)
            hotel.city = city  # Assign the manager's city to the hotel
            hotel.save()
            return redirect("manager_hotels")  # Redirect after successful submission

        # If the form is invalid, re-render the page with errors
        hotels = Hotel.objects.filter(city=city)
        return render(
            request,
            "manager_hotels.html",
            {
                "selected_city": city,
                "hotels": hotels,
                "manager": user.username,
                "form": form,
            },
        )


def city_hotels_view(request: HttpRequest) -> HttpResponse:
    """
    View for the user to see cities and the hotels in those cities.
    """

    return render(
        request,
        "home_page.html",

    )


def city_autocomplete(request: HttpRequest) -> HttpResponse:
    """
    Provides city suggestions for the user as they type.
    """

    query = request.GET.get(
        "q", ""
    )  # Get the query parameter from the GET request
    # Filter cities starting with the query string
    cities = (
        City.objects.filter(name__istartswith=query)
        if query
        else City.objects.none()
    )
    suggestions = [
        {"id": city.code, "name": city.name} for city in cities
    ]  # Prepare city suggestions
    return JsonResponse(suggestions, safe=False)


def signup(request: HttpRequest) -> HttpResponse:
    """
    View for manager signup. Allows new managers to create an account.
    """

    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()  # Save the new user
            return redirect(
                "login"
            )  # Redirect to login after successful signup
    else:
        form = CustomUserCreationForm()  # Initialize an empty form
    return render(request, "signup.html", {"form": form})


def custom_login(request: HttpRequest) -> HttpResponse:
    """
    Custom login view.
    """

    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            if user.is_superuser:
                return redirect("/admin/")  # Redirect to the admin panel
            else:
                return redirect(
                    "manager_hotels"
                )  # Redirect to manager's hotels page
    else:
        form = AuthenticationForm()  # Initialize empty login form

    return render(request, "login.html", {"form": form})


@login_required
@manager_required
def delete_hotel(request: HttpRequest, hotel_id: int) -> HttpResponse:
    """
    View to delete a hotel.
    Only managers of the hotel’s city can delete it.
    """

    hotel = get_object_or_404(Hotel, id=hotel_id, city=request.user.city)
    hotel.delete()
    return redirect("manager_hotels")


@login_required
@manager_required
def edit_hotel(request: HttpRequest, hotel_id: int) -> HttpResponse:
    """
    View to edit the details of an existing hotel.
    """

    hotel = get_object_or_404(Hotel, id=hotel_id, city=request.user.city)

    if request.method == "POST":
        form = HotelForm(request.POST, instance=hotel)
        if form.is_valid():
            form.save()
            return redirect(
                "manager_hotels"
            )  # Redirect after successful update
    else:
        form = HotelForm(instance=hotel)

    return render(request, "edit_hotel.html", {"form": form, "hotel": hotel})


def logout_view(request: HttpRequest) -> HttpResponse:
    """
    Logs the user out and redirects to the home page.
    """

    logout(request)
    return redirect("home")  # Redirect to the home page after logout


def get_hotels_by_city(request, city_code) -> JsonResponse:
    try:
        city = City.objects.get(code=city_code)

        hotels = Hotel.objects.filter(city=city)

        hotel_data = [
            {"name": hotel.name, "code": hotel.code} for hotel in hotels
        ]

        return JsonResponse({"hotels": hotel_data})

    except City.DoesNotExist:
        return JsonResponse({"error": "City not found"}, status=404)
