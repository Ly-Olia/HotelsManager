# HotelsManager

## Setup Instructions

### 1. Clone the repository

To get started with the project, clone the repository to your local machine:

```bash
git clone https://github.com/Ly-Olia/HotelsManager.git
cd HotelsManager
```


### 2. Install dependencies using pipenv
Install pipenv if you haven't already:

```bash
pip install pipenv
```
Create a virtual environment and install the required dependencies using pipenv:

```bash
pipenv install
```
This will automatically create a Pipfile and Pipfile.lock with all the dependencies required for the project.

### 3. Activate the virtual environment
Once the dependencies are installed, activate the virtual environment:

``` bash
pipenv shell
```
### 4. Apply Migrations
Run migrations to create the necessary database tables:

```bash
python manage.py migrate
```
### 5. Create the SQLite Database from initial_data.json
We can create an initial database with some predefined data using the initial_data.json file. This file contains initial data for cities, hotels, and users.

To load the data into your SQLite database, run the following command:

```bash
python manage.py loaddata initial_data.json
```
This will populate the database with the data from initial_data.json before proceeding with migrations.


### 6. Create a Superuser (Optional)
To access the Django admin panel, create a superuser:

```bash
python manage.py createsuperuser
```
Follow the prompts to set the username, email, and password. 

or use the one from database fixture (username: admin, password: admin)

### 7. Run the Development Server
Start the Django development server:

```bash
python manage.py runserver
```
Your application will be available at http://127.0.0.1:8000/.

### 8. Setting Up Cron Job for Daily Data Import
To automate the process of importing data from the CSV files every day, you can set up a cron job that will run at a specified time (in this case, every day at 2:00 AM).

Follow these steps to set up the cron job:

Open the Crontab Configuration:

Run the following command to open the crontab file for editing:

```bash
crontab -e
```
This will open the crontab editor for the current user. If you're prompted to select an editor, choose your preferred one (e.g., nano or vim).

Add the Cron Job:

In the crontab file, add the following line to schedule the data import script:

```ruby
0 2 * * * /bin/bash /path/to/your/project/hotels/scripts/import_data.sh >> /path/to/your/project/logs/import.log 2>&1
```
Replace /path/to/your/project/ with the actual path to your HotelsManager project directory. 
The line should look like:

```bash
0 2 * * * /bin/bash /home/user/HotelsManager/hotels/scripts/import_data.sh >> /home/user/HotelsManager/logs/import.log 2>&1
```
This line will execute the script import_data.sh at 2:00 AM daily, redirecting the output to the import.log file for logging purposes.
