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
