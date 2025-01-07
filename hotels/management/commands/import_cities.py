import csv
from typing import Optional

import requests
from django.core.management.base import BaseCommand
from requests.auth import HTTPBasicAuth

from hotels.models import City
from hotels.utils import CITY_CSV_URL, PASSWORD, USERNAME


class Command(BaseCommand):
    """
    Custom Django management command to import city data from a remote CSV file
    and populate the database with city records.
    """

    help = "Imports city data from a CSV file"

    def handle(self, *args: tuple, **kwargs: dict) -> Optional[str]:
        """
        Entry point for the command. Fetches city data from a remote CSV file,
        processes it, and updates the database.
        """
        try:
            # the HTTP request with authentication
            response = requests.get(
                CITY_CSV_URL,
                auth=HTTPBasicAuth(USERNAME, PASSWORD),
                timeout=10,  # Set timeout to prevent hanging
            )

            # Check if the response status is 200 OK
            if response.status_code != 200:
                self.stderr.write(
                    f"Failed to fetch city data. HTTP Status Code: {response.status_code}"
                )
                return

        except requests.RequestException as e:
            # Handle network errors or invalid requests
            self.stderr.write(f"Error fetching city data: {e}")
            return

        # Process the CSV data
        lines = response.text.strip().split("\n")
        reader = csv.reader(lines, delimiter=";", quotechar='"')

        for row in reader:
            # Ensure the row contains exactly two elements
            if len(row) != 2:
                self.stderr.write(f"Skipping malformed row: {row}")
                continue

            # Extract and clean city code and name
            city_code: str = row[0].strip()
            city_name: str = row[1].strip()

            # Create or retrieve the city record in the database
            city, created = City.objects.get_or_create(
                code=city_code, defaults={"name": city_name}
            )

            if created:
                self.stdout.write(f"Added city: {city_code} - {city_name}")
            else:
                self.stdout.write(
                    f"City already exists: {city_code} - {city_name}"
                )

        self.stdout.write("Cities imported successfully!")
