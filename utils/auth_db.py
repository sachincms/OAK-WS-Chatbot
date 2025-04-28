from bson.objectid import ObjectId
import bcrypt
import pandas as pd
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from config import USER_COLLECTION
from models.user import UserSchema, validate_user
from handlers.MongoDBHandler import MongoDBHandler
from logging_config import get_logger


mongodb_handler = MongoDBHandler(USER_COLLECTION)
logger = get_logger(__name__)


def init_db():
    mongodb_handler.create_index("username")

def get_usernames():
    users = list(mongodb_handler.read_data({}))
    return [user["username"] for user in users]

def add_user(user_data: dict):
    if user_data["username"] in get_usernames():
        return False
    
    password_hash = bcrypt.hashpw(user_data["password"].encode(), bcrypt.gensalt())

    try:
        if validate_user(user_data):
            data_to_insert = {
                "full_name": user_data["full_name"],
                "username": user_data["username"],
                "email": user_data["email"],
                "password_hash": password_hash,
                "created_at": user_data["created_at"],
                "role": "user",
                "status": "pending"
            }
            print(data_to_insert)

            mongodb_handler.insert_data(data_to_insert)
            
            return True
        
        else:
            logger.error(f"Cannot Add User {user_data["username"]}:  Validation Failed.")
            return False
    
    except Exception as ex:
        logger.error(f"Unexpected Error: {ex}")
        return False
   
    

def authenticate_user(username: str, password: str):
    documents = mongodb_handler.read_data({"username": username})
    if len(documents) == 0:
        logger.error(f"User {username} not found.")
        return False
    
    user = documents[0]
    if user and user.get("status") == "approved":
        return bcrypt.checkpw(password.encode(), user.get("password_hash"))
    return False


def get_all_users():
    users = list(mongodb_handler.read_data())
    return pd.DataFrame(users)


def approve_user(user_id: str):
    try:
        mongodb_handler.update_data(
            {"_id": ObjectId(user_id)},
            {"status": "approved"}
        )
        logger.info(f"Approved User ID: {user_id}")
        return True
    except Exception as ex:
        logger.error(f"Error Approving User {user_id}: {ex}")
        return False
    


def get_user_role(username: str):
    documents = mongodb_handler.read_data({"username": username})
    if len(documents) == 0:
        logger.error(f"User {username} not found.")
        return None
    user = documents[0]
    return user.get("role") if user else None


def promote_user_to_admin(user_id: str):
    try:
        mongodb_handler.update_data(
            {"_id": ObjectId(user_id)},
            {"role": "admin"}
        )
    except Exception as ex:
        logger.error(f"Error Promoting User {user_id}: {ex}")
    
    
def delete_user(user_id: str):
    try:
        mongodb_handler.delete_data({"_id": ObjectId(user_id)})
        logger.info(f"Deleted User ID: {user_id}")
    except Exception as ex:
        logger.error(f"Error Deleting User: {ex}")
