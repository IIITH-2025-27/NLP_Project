"""
Database Connection
MongoDB client initialization and database connection
"""

from pymongo import MongoClient
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import MONGO_URL, DB_NAME

# Initialize MongoDB client
client = MongoClient(MONGO_URL)
db = client[DB_NAME]
