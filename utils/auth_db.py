import sqlite3
from pymongo import MongoClient
from bson.objectid import ObjectId
import bcrypt
import pandas as pd
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from config import MONGODB_URI, DATABASE, COLLECTION
from logging_config import get_logger


logger = get_logger(__name__)

client = MongoClient(MONGODB_URI)
db = client[DATABASE]
users_collection = db[COLLECTION]

def init_db():
    users_collection.create_index("username", unique = True)


def add_user(username: str, password: str):
    password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    try:
        user_count = users_collection.count_documents({})

        # the first user will be automatically assigned as admin
        if user_count == 0:
            role = "admin"
        else:
            role = "user"

        if role == "admin":
            status = "approved"
        else:
            status = "pending"

        users_collection.insert_one({
            "username": username,
            "password_hash": password_hash,
            "role": role,
            "status": status
        })
        
        return True
    
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return False
   
    

def authenticate_user(username: str, password: str):
    user = users_collection.find_one({"username": username})
    if user and user.get("status") == "approved":
        return bcrypt.checkpw(password.encode(), user.get("password_hash").encode())
    return False


def get_all_users():
    users = list(users_collection.find({}, {"username": 1, "role": 1, "status": 1}))
    return pd.DataFrame(users)


def approve_user(user_id: str):
    try:
        result = users_collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"status": "approved"}}
        )
        logger.info(f"Approved user ID: {user_id}")
    except Exception as e:
        logger.error(f"Error approving user {user_id}: {e}")
    


def get_user_role(username: str):
    user = users_collection.find_one({"username": username})
    return user.get("role") if user else None


def promote_user_to_admin(user_id: str):
    try:
        users_collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"role": "admin"}}
        )
    except Exception as e:
        logger.error(f"Error promoting user {user_id}: {e}")
    
    
def delete_user(user_id: str):
    try:
        users_collection.delete_one({"_id": ObjectId(user_id)})
        logger.info(f"Deleted user id: {user_id}")
    except Exception as e:
        logger.error(f"Error deleting user: {e}")
