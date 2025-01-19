from io import StringIO
from unittest.mock import patch, Mock

import requests
from django.core.management import call_command
from django.test import TestCase
from requests import RequestException

from hotels.models import City, Hotel


class ImportCommandTests(TestCase):
    def setUp(self):
        # Setup mock data for testing
        self.city_data = "CCA;CityA\nCCB;CityB"
        self.hotel_data = "CCA;CCA01;Hotel01\nCCA;CCA02;Hotel02"

    def tearDown(self):
        # Clean up database after tests
        City.objects.all().delete()
        Hotel.objects.all().delete()

    def create_mock_response(self, text, status_code=200):
        """
        Helper function to create a mock response object.
        """
        mock_response = Mock(
            spec=requests.Response)
        mock_response.status_code = status_code
        mock_response.text = text
        mock_response.raise_for_status = Mock()
        return mock_response

    @patch("requests.get")
    def test_import_cities_success(self, mock_get):
        """
        Test the success scenario for importing cities.
        """

        mock_get.return_value = self.create_mock_response(self.city_data)

        out = StringIO()
        call_command("import_cities", stdout=out)

        # Assert that cities were imported correctly
        self.assertEqual(City.objects.count(), 2)
        self.assertTrue(City.objects.filter(code="CCA", name="CityA").exists())
        self.assertTrue(City.objects.filter(code="CCB", name="CityB").exists())
        self.assertIn("Added city: CCA - CityA", out.getvalue())
        self.assertIn("Added city: CCB - CityB", out.getvalue())

    @patch("requests.get")
    def test_import_cities_malformed_rows(self, mock_get):
        """
        Test the scenario where there are malformed rows in the CSV.
        """
        csv_data = "CCA;CityA\nCityC\nCCB;CityB;123"
        mock_get.return_value = self.create_mock_response(csv_data)

        out = StringIO()
        call_command("import_cities", stdout=out, stderr=out)

        # Assert that only valid city was imported
        self.assertEqual(City.objects.count(), 1)
        self.assertTrue(City.objects.filter(code="CCA", name="CityA").exists())
        self.assertIn("Added city: CCA - CityA", out.getvalue())
        self.assertIn("Skipping malformed row", out.getvalue())

    @patch("requests.get")
    def test_import_hotels_success(self, mock_get):
        """
        Test the success scenario for importing hotels.
        """
        # Create a city in the database
        city = City.objects.create(code="CCA", name="CityA")
        mock_get.return_value = self.create_mock_response(self.hotel_data)

        out = StringIO()
        call_command("import_hotels", stdout=out)

        # Assert that hotels were imported correctly
        self.assertEqual(Hotel.objects.count(), 2)
        self.assertTrue(
            Hotel.objects.filter(code="CCA01", name="Hotel01", city=city).exists()
        )
        self.assertTrue(
            Hotel.objects.filter(code="CCA02", name="Hotel02", city=city).exists()
        )
        self.assertIn("Added hotel: Hotel01 (CCA01) in CityA", out.getvalue())
        self.assertIn("Added hotel: Hotel02 (CCA02) in CityA", out.getvalue())

    @patch("requests.get")
    def test_import_hotels_missing_city(self, mock_get):
        """
        Test the scenario where the hotel references a non-existent city.
        """
        csv_data = "CCA;CCA01;Hotel01"
        mock_get.return_value = self.create_mock_response(csv_data)

        out = StringIO()
        call_command("import_hotels", stdout=out, stderr=out)

        # Assert that no hotels were imported
        self.assertEqual(Hotel.objects.count(), 0)
        self.assertIn(
            "City with code CCA not found. Skipping hotel: CCA01 - Hotel01", out.getvalue()
        )

    @patch("requests.get")
    def test_import_hotels_malformed_rows(self, mock_get):
        """
        Test the scenario where there are malformed rows in the hotel CSV.
        """
        city = City.objects.create(code="CCA", name="CityA")

        csv_data = "CCA;CCA01;Hotel01\nCCA;CCA02;Hotel02;123\nCCA;Hotel03"
        mock_get.return_value = self.create_mock_response(csv_data)

        out = StringIO()
        call_command("import_hotels", stdout=out, stderr=out)

        # Assert that only valid hotel was imported
        self.assertEqual(Hotel.objects.count(), 1)
        self.assertTrue(
            Hotel.objects.filter(code="CCA01", name="Hotel01", city=city).exists()
        )
        self.assertIn("Skipping malformed row", out.getvalue())

    @patch("requests.get")
    def test_import_http_error(self, mock_get):
        """
        Test the scenario where there is an HTTP error.
        """
        # Mock an HTTP error
        mock_get.return_value = self.create_mock_response("", status_code=404)

        out = StringIO()
        call_command("import_cities", stdout=out, stderr=out)
        call_command("import_hotels", stdout=out, stderr=out)

        self.assertEqual(City.objects.count(), 0)
        self.assertIn("Failed to fetch city data. HTTP Status Code: 404", out.getvalue())
        self.assertEqual(Hotel.objects.count(), 0)
        self.assertIn("Failed to fetch hotel data. HTTP Status Code: 404", out.getvalue())

    @patch("requests.get")
    def test_import_empty_csv(self, mock_get):
        """
        Test when the CSV data is empty.
        """
        mock_get.return_value = self.create_mock_response("")

        out = StringIO()
        call_command("import_cities", stdout=out)
        call_command("import_hotels", stdout=out)
        self.assertEqual(City.objects.count(), 0)
        self.assertEqual(Hotel.objects.count(), 0)
        self.assertIn("Cities imported successfully!", out.getvalue())
        self.assertIn("Hotels imported successfully!", out.getvalue())

    @patch("requests.get")
    def test_import_cities_with_extra_spaces(self, mock_get):
        """
        Test when city data has extra spaces.
        """
        csv_data = "CCA ; CityA  \n CCB ; CityB "
        mock_get.return_value = self.create_mock_response(csv_data)

        out = StringIO()
        call_command("import_cities", stdout=out)

        self.assertEqual(City.objects.count(), 2)
        self.assertTrue(City.objects.filter(code="CCA", name="CityA").exists())
        self.assertTrue(City.objects.filter(code="CCB", name="CityB").exists())

    @patch("requests.get")
    def test_import_hotels_with_extra_spaces(self, mock_get):
        """
        Test when hotel data has extra spaces.
        """
        # Create a city in the database
        city = City.objects.create(code="CCA", name="CityA")
        csv_data = "CCA ; CCA01 ; Hotel01 \n  CCA ; CCA02 ;  Hotel02 "
        mock_get.return_value = self.create_mock_response(csv_data)

        out = StringIO()
        call_command("import_hotels", stdout=out)

        # Assert that hotels were imported correctly
        self.assertEqual(Hotel.objects.count(), 2)
        self.assertTrue(
            Hotel.objects.filter(code="CCA01", name="Hotel01", city=city).exists()
        )
        self.assertTrue(
            Hotel.objects.filter(code="CCA02", name="Hotel02", city=city).exists()
        )
        self.assertIn("Added hotel: Hotel01 (CCA01) in CityA", out.getvalue())
        self.assertIn("Added hotel: Hotel02 (CCA02) in CityA", out.getvalue())

    @patch("requests.get")
    def test_import_cities_request_exception(self, mock_get):
        """Test handling of RequestException during fetch."""
        mock_get.side_effect = RequestException("Connection error")

        out = StringIO()
        err = StringIO()

        call_command("import_cities", stdout=out, stderr=err)

        # Ensure no hotels were imported
        self.assertIn("Error fetching city data: Connection error", err.getvalue())

    @patch("requests.get")
    def test_import_hotels_request_exception(self, mock_get):
        """Test handling of RequestException during fetch."""
        mock_get.side_effect = RequestException("Connection error")

        out = StringIO()
        err = StringIO()

        call_command("import_hotels", stdout=out, stderr=err)

        # Ensure no hotels were imported
        self.assertIn("Error fetching hotel data: Connection error", err.getvalue())

