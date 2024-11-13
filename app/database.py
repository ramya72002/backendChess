from pymongo import MongoClient
from gridfs import GridFS
import os

client = None
db = None
fs = None
admin_collection = None
users_collection = None
schoolform_coll=None
app_signup=None

def init_db(app):
    global client, db, fs, admin_collection, users_collection,schoolform_coll,app_signup
    mongo_uri = os.getenv('MONGO_URI')
    client = MongoClient(mongo_uri)
    db = client.chessDb
    admin_collection = db.admin_db
    users_collection = db.users
    schoolformdb=client.chessschool
    schoolform_coll=schoolformdb.kids
    app_signup=schoolformdb.app_signup
    fs = GridFS(db)
