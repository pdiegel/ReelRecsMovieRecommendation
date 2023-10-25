# Movie Recommendation App

## ReelRecs

A Flask-based web application that uses the TMDB (The Movie Database) API to fetch and display movie details, portraits, images, and other related data.

## Features

- User Login and Authentication
- Movie Recommendations
- Fetch and Display Movie Details and Images
- Movie Search

## Pre-requisites

Before you start, you will need to have the following tools installed on your machine:

- Git
- Python 3.7 or above
- Pip (Python package installer)

It is also good to have an editor to work with the code like [VSCode](https://code.visualstudio.com/).

## Running the Application

### Cloning the Repository

``` bash
# Clone this repository 
$ git clone https://github.com/pdiegel/ReelRecsMovieRecommendation.git

# Access the project folder in the terminal/cmd
$ cd movie-recommendation-app
```

### Creating a Virtual Environment

It's best to create and use a virtual environment while running Python applications. Use the following commands to create a new virtual environment and activate it:

``` bash
# Creating a virtual environment 
$ python -m venv env  

# Activating the virtual environment 
$ source env/bin/activate
```

### Installing Dependencies

The project dependencies are listed in the `requirements.txt` file. After activating the virtual environment, install these dependencies using pip:

``` bash
# Install dependencies
$ pip install -r requirements.txt
```

### Setting up Environment Variables

This application uses certain environment variables that need to be set in the `.env` file. Make sure to create this file in the root directory (if not already present) and add your TMDB API keys and other necessary details:

``` bash
# .env file  

API_ACCESS_TOKEN=<Your TMDB API Token> 
ACCOUNT_OBJECT_ID=<Account Object ID> 
FLASK_DEBUG=True 
API_KEY=<Your TMDB API Key> 
ACCOUNT_ID=<Your Account ID>
```

Replace `<Your TMDB API Token>`, `<Account Object ID>`, `<Your TMDB API Key>`, and `<Your Account ID>` with your actual TMDB API details. Make sure not to include the angle brackets.

### Running the Server

Run the following command in your terminal:

``` bash
# Running the application
$ python src/main.py
```

After running the server, the application should be accessible via `http://localhost:5000` in your web browser (or a different port, if you've configured it differently).

## Technology Stack

- Python
- Flask
- TMDB API
- Jinja2 (template engine for Python)
- HTML/CSS
- JavaScript

## Contact

If you encounter any issues or have suggestions for improvements, feel free to open an issue or submit a pull request. Contributions are always welcome!

_Please note that TMDB API details are sensitive information and should not be shared publicly._
