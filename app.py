import os
from flask import Flask, request, send_from_directory
import config
from database import *
import click
import random
import string
import datetime

app = Flask(__name__)

UPLOAD_FOLDER = os.path.join('uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


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


@app.route('/upload', methods=['POST'])
def upload_file():
    api_key = request.form['api_key']
    if api_key != config.API_KEY:
        return
    file = request.files['d']

    # Check for collision
    new_image_db_inst = None
    while True:
        file_name = f"{generate_random_file_name()}.png".strip()
        try:
            ImageName.select().where(ImageName.alias == file_name).get()
            # There is a collision, try again
        except DoesNotExist as ex:
            # No collision
            try:
                new_image_db_inst = ImageName.create(file_name=file.filename, alias=file_name, date=datetime.datetime.now())
            except:
                pass

            break

        except Exception as ex:
            break

    if new_image_db_inst == None:
        return

    f = os.path.join(app.config['UPLOAD_FOLDER'], new_image_db_inst.file_name)
    file.save(f)

    return f"{config.BASE_URL}{new_image_db_inst.alias}"



if __name__ == '__main__':
    main()
