#!/bin/bash

# Activate the virtual environment
# This command activates the virtual environment where your Django project dependencies are installed.
source /Users/lyolia/PycharmProjects/IntegratingThirdParties/.venv/bin/activate

# Navigate to the project directory
# This command changes the current working directory to your Django project folder.
cd /Users/lyolia/PycharmProjects/IntegratingThirdParties

# Run the import commands
# These commands will run the Django management commands to import cities and hotels data.
# Make sure the corresponding custom management commands (import_cities, import_hotels) are implemented in your Django project.
python manage.py import_cities
python manage.py import_hotels

# Deactivate the virtual environment
# This command deactivates the virtual environment after the task is completed.
deactivate
