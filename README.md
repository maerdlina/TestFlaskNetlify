## Overview

This Flask application displays my family's favorite recipes!  [Frozen-Flask](https://pythonhosted.org/Frozen-Flask/) is
used to generate the static files based on the routes specified in the Flask app.  These static files are hosted on
[Netlify](https://www.netlify.com):

![Kennedy Family Recipes](project/static/img/flask_recipe_app_screenshot.png?raw=true "Kennedy Family Recipes")

For details on how this Flask app generates static files, check out the [Generating a Static Site with Flask and Deploying it to Netlify](https://testdriven.io/blog/) blog post on [TestDriven](https://testdriven.io/).

## Website

[https://www.kennedyrecipes.com/](https://www.kennedyrecipes.com/)

## Installation Instructions

Pull down the source code from this GitLab repository:

```sh
git clone git@gitlab.com:patkennedy79/flask-recipe-app.git
```

Create a new virtual environment:

```sh
$ cd flask-recipe-app
$ python3 -m venv venv
```

Activate the virtual environment:

```sh
$ source venv/bin/activate
```

Install the python packages in requirements.txt:

```sh
(venv) $ pip install -r requirements.txt
```

## Run the Development Server

Run development server to serve the Flask application:

```sh
(venv) $ flask --app app --debug run
```

Navigate to 'http://127.0.0.1:5000/' in your favorite web browser to view the website!

## Key Python Modules Used

* **Flask**: micro-framework for web application development which includes the following dependencies:
  * click: package for creating command-line interfaces (CLI)
  * itsdangerous: cryptographically sign data 
  * Jinja2: templating engine
  * MarkupSafe: escapes characters so text is safe to use in HTML and XML
  * Werkzeug: set of utilities for creating a Python application that can talk to a WSGI server
* **Frozen-Flask** - generates static files from Flask routes
* **Markdown** - text-to-HTML conversion tool
* **pytest**: framework for testing Python projects
* **pytest-cov**: pytest extension for running coverage.py to check code coverage of tests
* **flake8**: static analysis tool

This application is written using Python 3.11.0.

## Unit Testing

To run all the tests:

```sh
(venv) $ python -m pytest
```

To check the code coverage of the tests:

```sh
(venv) $ python -m pytest --cov-report term-missing --cov=project
```

## Adding a New Recipe

1. Add the new image to *project/static/img/*.
2. Copy *project/recipes/template/markdown/recipe_starter.md* to a new file in the same directory with the recipe name as the filename.
3. Update the new *project/recipes/template/markdown/<recipe_name>.md* file with the recipe description, ingredients, and steps.
4. Generate the HTML file for the new recipe:
```sh
$ python project/recipes/templates/md_to_html.py
```
5. Add a new section to the applicable recipe section HTML file (i.e. *project/recipes/template/recipes/baked_good.html*, *project/recipes/template/recipes/dinner.html*, etc.).
6. Add the recipe name to the top of *project/recipes/routes.py*.

Lastly, run the tests to make sure everything is working as expected:
```sh
(venv) $ python -m pytest
```

### Build the Static Files

In the top-level directory, run the build script:

```sh
(venv) $ python build.py
```

The static files are generated in the */project/build/* directory, which can then be hosted on Netlify.
