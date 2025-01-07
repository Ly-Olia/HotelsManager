#!/bin/bash

# Make sure to change the path to your actual .venv directory
source /Users/lyolia/PycharmProjects/HotelsManager/.venv/bin/activate

# Ensure the path is correct for your project location
cd /Users/lyolia/PycharmProjects/HotelsManager/

# Run the import commands
python manage.py import_cities
python manage.py import_hotels
