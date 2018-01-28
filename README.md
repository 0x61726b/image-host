# Self hosted image upload web app

## How to run

- python -m venv venv
- venv/bin/activate
- pip install -U -r requirements.txt
- touch config.py
- vim config.py
Add 2 lines of options like this
```angular2html
BASE_URL = "http://arkn.xyz/"
API_KEY = ''
```
- python app.py db init
- sudo FLASK_APP=app.py ./venv/bin/python -m flask run --host=0.0.0.0 --port=80
