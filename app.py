import os
from flask import Flask, request, send_from_directory
import config
from database import *
import click
import random
import string
import datetime
import requests
import posixpath
from urllib.parse import urlsplit, unquote

app = Flask(__name__)

UPLOAD_FOLDER = os.path.join('uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def url_to_filename(url):
    urlpath = urlsplit(url).path
    basename = posixpath.basename(unquote(urlpath))
    if (os.path.basename(basename) != basename or unquote(posixpath.basename(urlpath)) != basename):
        return None
    return basename

def url_to_file_ext(url):
    urlpath = urlsplit(url).path
    return os.path.splitext(urlpath)[1]


@click.group(invoke_without_command=True, options_metavar='[options]')
@click.pass_context
def main(ctx):
    if ctx.invoked_subcommand is None:
        while True:
            connect()
            app.run(host='0.0.0.0', port=config.PORT)
            print("Restarting...")

@main.group(short_help='database stuff', options_metavar='[options]')
def db():
    """Initializes the database."""
    connect()

@db.command(short_help='Init all tables', options_metavar='[options]')
@click.option('-q', '--quiet', help='less verbose output', is_flag=True)
def init(quiet):
    init_db()
    print('Initialized the database.')

@app.route('/<filename>/')
def static_subdir(filename=None):
    # Find the requested file name in database to match its original file name
    try:
        image_db_inst = ImageName.select().where(ImageName.alias == str(filename).strip()).get()
        return send_from_directory(app.config['UPLOAD_FOLDER'], image_db_inst.file_name)
    except Exception as ex:
        pass


def generate_random_file_name():
    return ''.join([random.choice(string.ascii_letters + string.digits + '-‌​_') for ch in range(8)])

def save_upload(r_file_name, ext):
    # Check for collision
    new_image_db_inst = None
    while True:
        file_name = f"{generate_random_file_name()}{ext}".strip()
        try:
            ImageName.select().where(ImageName.alias == file_name).get()
            # There is a collision, try again
        except DoesNotExist as ex:
            # No collision
            try:
                return ImageName.create(file_name=r_file_name, alias=file_name,
                                                     date=datetime.datetime.now())
            except:
                pass

            break

        except Exception as ex:
            break

    return None

@app.route('/upload', methods=['POST'])
def upload_file():
    api_key = request.form['api_key']
    if api_key != config.API_KEY:
        return
    file = request.files['d']

    file_name = url_to_filename(file.filename)
    file_ext = url_to_file_ext(file.filename)

    new_image_db_inst = save_upload(file.filename, file_ext)
    if new_image_db_inst == None:
        return

    f = os.path.join(app.config['UPLOAD_FOLDER'], new_image_db_inst.file_name)
    file.save(f)

    return f"{config.BASE_URL}{new_image_db_inst.alias}"

@app.route('/upload_from_url', methods=['POST'])
def upload_from_url():
    api_key = request.form['api_key']
    if api_key != config.API_KEY:
        return

    url = request.form['image_url']
    if url == None:
        return

    file_name = url_to_filename(url)
    file_ext = url_to_file_ext(url)
    r = requests.get(url)

    new_image_db_inst = save_upload(file_name, file_ext)
    if new_image_db_inst == None:
        return

    with open(os.path.join(app.config['UPLOAD_FOLDER'], file_name), 'wb') as f:
        f.write(r.content)
        return f"{config.BASE_URL}{new_image_db_inst.alias}"



if __name__ == '__main__':
    main()
