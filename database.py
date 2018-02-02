from peewee import *

db = SqliteDatabase('image.db')



class BaseModel(Model):
    class Meta:
        database = db

class ImageName(BaseModel):
    file_name = CharField()
    alias = CharField()
    date = DateTimeField()


def init_db():
    db.create_tables([ImageName])

def connect():
    db.connect()