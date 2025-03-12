# Python on Netlify

**Version 1.0.0**

An example of how to deploy a Flask app to Netlify.

## Demo

Visit [https://trusting-lewin-7ad5f5.netlify.com/](https://trusting-lewin-7ad5f5.netlify.com/) to see the website in action.

## Get started with Flask Web App locally

Ensure you have Python and Flask installed, then:

``` bash
git clone https://github.com/ethanmiller1/Flask-Netlify.git
python –m venv venv
cd venv/Scripts && activate && cd ../..
pip install -r requirements.txt
set FLASK_APP=freeze.py
flask run --reload
```

(Note: Powershell is known to have problems with Python 3.7 commands. Activate cmd with `cmd`.)

### Entry Point

`freeze.py` contains all the routes for the project. Use `set FLASK_APP=freeze.py` to set it as Flask's entry point for the project. Flask serves the application to [localhost:5000](localhost:5000 "Port 5000") by default.

### Deploy to Netlify

Build command: `python freeze.py`.
Public directory: `build`.

![](https://miro.medium.com/max/700/1*kPMjcU3kUaoJ9DmamhlcRA.png)

## Contributors

---

- Ethan Miller <ethan.romans5.8@gmail.com>

---

## License & copyright

© Ethan Miller