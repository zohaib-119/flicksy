# Flicksy - Social Media Application

Flicksy is a social media application built with Django that allows users to interact with posts, like and comment, and follow each other. It utilizes AJAX for smoother, more dynamic user interactions.

## Prerequisites

Make sure you have the following installed:

- [Python 3.x](https://www.python.org/downloads/)
- [Pipenv](https://pipenv.pypa.io/en/latest/) for managing Python dependencies

## Setting Up the Project

### 1. Clone the Repository

First, clone the repository to your local machine:

git clone https://github.com/zohaib-119/flicksy.git
```bash
cd flicksy
```
2. Install Dependencies
Create a virtual environment and install the required dependencies with pipenv:
```bash
pipenv install
```
3. Activate the Virtual Environment
Activate the virtual environment using:
```bash
pipenv shell
```
4. Set Up the Database
Run the following command to apply database migrations:
```bash
python manage.py migrate
```
5. Create a Superuser (Optional)
To create an admin user, run the following command and follow the prompts:
```bash
python manage.py createsuperuser
```
6. Start the Development Server
Now you can start the Django development server:
```bash
python manage.py runserver
```
The application will be running at http://127.0.0.1:8000/.

7. Access the Admin Panel (Optional)
You can access the Django admin panel at http://127.0.0.1:8000/admin/ using the superuser credentials you created.

### Features
User authentication (sign up, login)
Posting content
Like, comment, and save functionality
Follow/unfollow system
Search by username
