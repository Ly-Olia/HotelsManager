from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.test import TestCase

from hotels.models import City, Hotel, User


class CityModelTest(TestCase):
    """
    Tests for the City model.
    These tests ensure the correct functionality of the City model, including its constraints and relationships.
    """

    def setUp(self):
        """
        Set up test data for City model tests.
        This method is called before each test case is executed.
        """

        # Clean the database before running each test
        City.objects.all().delete()

        # Create sample cities
        self.city_sfo = City.objects.create(name="San Francisco", code="SFO")
        self.city_nyc = City.objects.create(name="New York", code="NYC")

    def test_city_create(self):
        """
        Test creating a city and ensuring its attributes are correct.
        """

        sfo = City.objects.get(name="San Francisco")
        self.assertEqual(sfo.code, "SFO")
        self.assertEqual(sfo.name, "San Francisco")
        self.assertEqual(str(sfo), "San Francisco")

    def test_city_code_uniqueness(self):
        """
        Test that creating two cities with the same code raises an exception.
        """

        with self.assertRaises(Exception):
            City.objects.create(code="SFO", name="Duplicate City")

    def test_city_name_empty(self):
        """
        Test that a city cannot be created with an empty name.
        """

        city = City(code="NYC", name="")
        with self.assertRaises(ValidationError):
            city.full_clean()

    def test_multiple_city_creation(self):
        """
        Test creating multiple cities using bulk_create to ensure performance and functionality.
        """

        # Ensure the database is clean before running the test
        City.objects.all().delete()

        # Create a list of cities
        cities = [City(name=f"City{i}", code=f"C{i}") for i in range(100)]
        City.objects.bulk_create(cities)

        # Verify the count of cities
        self.assertEqual(City.objects.count(), 100)


class HotelModelTest(TestCase):
    """
    Tests for the Hotel model. These tests ensure the correct functionality of the Hotel model, including validation,
    relationships, and constraints.
    """

    def setUp(self):
        # Create a city to associate with the hotels
        self.city = City.objects.create(code="AMS", name="Amsterdam")

    def test_create_hotel(self):
        """
        Test creating a hotel and ensuring its attributes are correct.
        """

        hotel = Hotel.objects.create(
            code="H001", name="Grand Amsterdam", city=self.city
        )
        self.assertEqual(hotel.code, "H001")
        self.assertEqual(hotel.name, "Grand Amsterdam")
        # Ensure hotel is associated with the correct city
        self.assertEqual(hotel.city_id, self.city.code)
        # Ensure the relationship is correct
        self.assertEqual(hotel.city, self.city)
        self.assertEqual(str(hotel), "Grand Amsterdam")

    def test_hotel_city_relationship(self):
        """
        Test the relationship between the Hotel and City models.
        Ensure the hotel is linked to the correct city and appears in the city's hotels.
        """

        hotel = Hotel.objects.create(
            code="H002", name="Luxury Inn", city=self.city
        )
        self.assertEqual(hotel.city.name, "Amsterdam")
        # Ensure hotel is listed in the city's hotels
        self.assertIn(hotel, self.city.hotels.all())

    def test_invalid_city_for_hotel(self):
        """
        Test that a hotel cannot be created with an invalid city ID.
        """

        with self.assertRaises(ValidationError):
            Hotel.objects.create(
                code="H006", name="Invalid City Hotel", city_id="INVALID"
            )

    def test_hotel_missing_city(self):
        """
        Test that a hotel cannot be created without a city.
        """

        with self.assertRaises(ValidationError):
            Hotel.objects.create(code="H004", name="Missing City Hotel")

    def test_hotel_code_uniqueness(self):
        """
        Test that a hotel cannot be created with a duplicate code.
        """

        Hotel.objects.create(code="H005", name="Unique Hotel", city=self.city)
        with self.assertRaises(IntegrityError):
            Hotel.objects.create(
                code="H005", name="Duplicate Hotel", city=self.city
            )


class UserModelTest(TestCase):
    """
    Tests for the User model. These tests ensure the correct functionality of the User model, including user
    creation, password validation, and constraints.
    """

    def setUp(self):
        # Create a city to associate with the user
        self.city = City.objects.create(code="AMS", name="Amsterdam")

    def test_create_user(self):
        """
        Test creating a manager and ensuring their attributes are correct.
        """

        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpassword",
            city=self.city,
        )
        self.assertEqual(user.username, "testuser")
        self.assertEqual(user.email, "test@example.com")
        self.assertTrue(user.check_password("testpassword"))
        self.assertEqual(user.role, "manager")
        self.assertFalse(user.is_superuser)
        self.assertEqual(user.city, self.city)

    def test_create_superuser(self):
        """
        Test creating a superuser with elevated privileges.
        """

        superuser = User.objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="adminpassword",
        )
        self.assertTrue(superuser.is_staff)
        self.assertTrue(superuser.is_superuser)

    def test_create_user_without_username(self):
        """
        Test that a user cannot be created without a username.
        """

        user = User.objects.create_user(
            username="", email="test@example.com", password="testpassword"
        )
        with self.assertRaises(ValidationError):
            user.full_clean()

    def test_create_user_without_password(self):
        """
        Test that a user cannot be created without a password.
        """

        user = User(username="test01", email="test01@example.com", password="")
        with self.assertRaises(ValidationError):
            user.full_clean()

    def test_create_user_with_duplicate_username(self):
        """
        Test that a user cannot be created with a duplicate username.
        """

        User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpassword",
        )
        with self.assertRaises(IntegrityError):
            User.objects.create_user(
                username="testuser",
                email="another@example.com",
                password="newpassword",
            )

    def test_create_user_invalid_username(self):
        """
        Test that a user cannot be created with an invalid username (contains spaces or special characters).
        """

        user = User.objects.create_user(
            username="invalid username!",
            email="test6@example.com",
            password="testpassword",
        )
        with self.assertRaises(ValidationError):
            user.full_clean()
