import csv

import requests
from django.core.management.base import BaseCommand
from requests.auth import HTTPBasicAuth

from hotels.models import City, Hotel
from hotels.utils import HOTEL_CSV_URL, PASSWORD, USERNAME


class Command(BaseCommand):
    help = "Imports hotel data from a CSV file"

    def handle(self, *args, **kwargs):
        """
        Entry point for the custom Django command. This method fetches hotel data
        from a CSV file, validates it, and updates or creates records in the database.
        """
        try:
            response = requests.get(
                HOTEL_CSV_URL,
                auth=HTTPBasicAuth(USERNAME, PASSWORD),
                timeout=10,
            )

            if response.status_code != 200:
                self.stderr.write(
                    f"Failed to fetch hotel data. HTTP Status Code: {response.status_code}"
                )
                return

        except requests.RequestException as e:
            self.stderr.write(f"Error fetching hotel data: {e}")
            return

        # Parse the CSV content
        lines = response.text.strip().split("\n")
        reader = csv.reader(
            lines, delimiter=";", quotechar='"'
        )  # Parse semicolon-separated values

        for row in reader:
            if len(row) != 3:  # Ensure the row has the expected 3 fields
                self.stderr.write(f"Skipping malformed row: {row}")
                continue

            # Extract and clean data from the row
            city_code, hotel_code, hotel_name = map(str.strip, row)

            # Retrieve the related city
            try:
                city = City.objects.get(code=city_code)
            except City.DoesNotExist:
                self.stderr.write(
                    f"City with code {city_code} not found. Skipping hotel: {hotel_code} - {hotel_name}"
                )
                continue

            # Create or get the hotel record
            hotel, created = Hotel.objects.get_or_create(
                code=hotel_code, city=city, defaults={"name": hotel_name}
            )

            if created:
                self.stdout.write(
                    f"Added hotel: {hotel_name} ({hotel_code}) in {city.name}"
                )
            else:
                self.stdout.write(
                    f"Hotel already exists: {hotel_name} ({hotel_code}) in {city.name}"
                )

        self.stdout.write("Hotels imported successfully!")
