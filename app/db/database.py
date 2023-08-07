from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()

db_password = os.getenv("DB_PASSWORD")


class Database:
    def __init__(self):
        CONNECTION_STRING = "mongodb+srv://admin:" + \
            db_password + "@cluster0.0maxtet.mongodb.net"
        self.client = MongoClient(CONNECTION_STRING)["crypto"]
