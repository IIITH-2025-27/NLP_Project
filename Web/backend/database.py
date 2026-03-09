from pymongo import MongoClient
from config import MONGO_URL, DB_NAME

# Initialize MongoDB client
client = MongoClient(MONGO_URL)
db = client[DB_NAME]

# Collections
users_col = db["users"]
history_col = db["history"]
