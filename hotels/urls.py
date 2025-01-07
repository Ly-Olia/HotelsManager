# URLConf for the `hotels` app
# This file defines all the URL patterns for views related to hotels, including user authentication,
# hotel management, and city-related hotel data.

from django.urls import path

from hotels.views import custom_login, logout_view, signup

from . import views

urlpatterns = [
    # URL for viewing the hotels in a city, restricted to manager roles
    path(
        "manager_hotels/", views.city_hotels_view_manager, name="manager_hotels"
    ),
    # URL for handling the city autocomplete functionality (for city selection)
    path("autocomplete/", views.city_autocomplete, name="city_autocomplete"),
    # URL for the login page, using custom_login view for authentication
    path("login/", custom_login, name="login"),
    # URL for the signup page, where new users can register
    path("signup/", signup, name="signup"),
    # URL for deleting a hotel, requires hotel_id as a path parameter
    path(
        "manager/hotels/delete/<int:hotel_id>/",
        views.delete_hotel,
        name="delete_hotel",
    ),
    # URL for editing a hotel, requires hotel_id as a path parameter
    path("<int:hotel_id>/edit/", views.edit_hotel, name="hotel_edit"),
    # URL for logging out the user, using the logout_view function
    path("logout/", logout_view, name="logout"),
    # URL for getting hotels by the city
    path(
        "<str:city_code>/", views.get_hotels_by_city, name="get_hotels_by_city"
    ),
]
