import json

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from hotels.models import City, Hotel

User = get_user_model()


class HotelsViewsTest(TestCase):
    def setUp(self):
        # Create test user
        self.manager_user = User.objects.create_user(
            username="manager",
            password="manager123",
            role="manager",
            email="manager@gmail.com"
        )
        self.city = City.objects.create(name="Amsterdam", code="AMS")
        self.manager_user.city = self.city
        self.manager_user.save()

        self.hotel = Hotel.objects.create(
            name="Test Hotel", code="H001", city=self.city
        )

    def test_city_hotels_view_without_city_filter(self):
        """Test that the home page loads without selecting a city."""
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "home_page.html")
        self.assertContains(response, "Choose a City")

    def test_city_autocomplete_no_results(self):
        """Test city autocomplete when there are no matching results."""
        response = self.client.get(reverse('city_autocomplete'), {'q': 'Q'})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data, [])

    def test_city_autocomplete(self):
        """Test city_autocomplete view for suggestions."""
        response = self.client.get(reverse("city_autocomplete"), {"q": "Amst"})
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            response.content.decode(),
            [{"id": "AMS", "name": "Amsterdam"}],
        )

    def test_signup(self):
        """Test signup view."""
        test_city = City.objects.create(name="Test City", code="TTC")
        response = self.client.post(
            reverse("signup"),
            {
                "username": "new_manager",
                "email": "new.manager@gmail.com",
                "password1": "securePassword123",
                "password2": "securePassword123",
                "city": test_city.code,
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username="new_manager").exists())

    def test_custom_login(self):
        """Test login view."""
        response = self.client.post(
            reverse("login"),
            {"username": "manager", "password": "manager123"},
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("manager_hotels"))

    def test_city_hotels_view_manager(self):
        """Test manager view to see hotels."""
        self.client.login(username="manager", password="manager123")
        response = self.client.get(reverse("manager_hotels"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["selected_city"], self.city)

    def test_add_hotel_as_manager(self):
        """Test adding a hotel as a manager."""
        self.client.login(username="manager", password="manager123")
        response = self.client.post(
            reverse("manager_hotels"),
            {"name": "New Hotel", "code": "NH01"},
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            Hotel.objects.filter(name="New Hotel", city=self.city).exists()
        )

    def test_delete_hotel_as_manager(self):
        """Test deleting a hotel as a manager."""
        self.client.login(username="manager", password="manager123")
        self.assertTrue(Hotel.objects.filter(id=self.hotel.id).exists())
        response = self.client.post(
            reverse("delete_hotel", args=[self.hotel.id])
        )
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Hotel.objects.filter(id=self.hotel.id).exists())

    def test_edit_hotel_as_manager(self):
        """Test editing a hotel as a manager."""
        self.client.login(username="manager", password="manager123")
        response = self.client.post(
            reverse("hotel_edit", args=[self.hotel.id]),
            {"name": "Updated Hotel", "code": "H001"},
        )
        self.assertEqual(response.status_code, 302)
        self.hotel.refresh_from_db()
        self.assertEqual(self.hotel.name, "Updated Hotel")

    def test_logout(self):
        """Test logout view."""
        self.client.login(username="manager", password="manager123")
        response = self.client.get(reverse("logout"))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("home"))

    def test_get_hotels_by_city(self):
        """Test API to get hotels by city."""
        response = self.client.get(reverse("get_hotels_by_city", args=["AMS"]))
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            response.content.decode(),
            {'hotels':[{"name": self.hotel.name, "code": self.hotel.code}]},
        )

        # Test invalid city code
        response = self.client.get(reverse("get_hotels_by_city", args=["XXX"]))
        self.assertEqual(response.status_code, 404)
        self.assertJSONEqual(response.content.decode(), {"error": "City not found"})
