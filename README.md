# VideoBin

A Flask-based platform for sharing videos via direct links, functioning like Pastebin but for video content. Users can upload and share videos, customize embedded advertisements, and earn revenue from views.


## Installation

First, you need to clone this repository:

```bash
git clone git@github.com:Jisangain/VideoBin.git
```

Or:

```bash
git clone https://github.com/Jisangain/VideoBin.git
```

Then change into the `VideoBin` folder:

```bash
cd VideoBin
```
Install the requirements:

```
pip install -r requirements.txt
```
or
```
pip3 install -r requirements.txt
```

Set Environment Variables according to settings.py

## MySql Model Setup
Create a database and set the `sql_uri` variable in settings.py

Create model using python interpreter:
```python
from VideoBin import db, create_app, models
    db.create_all(app=create_app())
```

## Run Program

```bash
export FLASK_APP=VideoBin
```

You will need to run flask app and and `catbox_monetag.py` together:
```bash
flask run &
cd VideoBin && python3 catbox_monetag.py
```
Alternatively you can run `python3 catbox_monetag.py` in separate online/local server

### Live Demo

An underdevelopment live version is available at [picosi.pythonanywhere.com](https://picosi.pythonanywhere.com)
A django version is available at [picosi.tech](https://picosi.tech)

## Contributions

Any contribution is welcome, just fork and submit your PR.

## License

This project is licensed under the MIT License (see the `LICENSE` file for details).
