from pydantic import BaseModel, EmailStr, Field, field_validator
from datetime import datetime
import re
import logging

VALID_USERNAME_PATTERN = re.compile(r"^[a-zA-Z0-9_]+$")
VALID_PASSWORD_PATTERN = re.compile(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*[0-9]).*$")

class UserSchema(BaseModel):
    full_name: str
    username : str
    email : EmailStr
    password : str
    created_at : datetime = Field(default_factory=datetime.now)

    @field_validator("username")
    @classmethod
    def validate_username(cls, value: str) -> str:
        username_length = len(value)
        if username_length < 3 or username_length > 20:
            raise ValueError("Username must be between 3 and 20 characters long.")
        if " " in value:
            raise ValueError("Username cannot have white spaces.")
        if not VALID_USERNAME_PATTERN.match(value):
            raise ValueError("Username can only contain alphanumeric characters and underscores.")

        return value
    
    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        if len(value) < 8:
            raise ValueError("Password must be at least 8 characters long.")
        if not VALID_PASSWORD_PATTERN.match(value):
            raise ValueError("Password must contain at least one lowercase letter, one uppercase letter and one digit.")
        
        return value
    

def validate_user(user_data: dict):
    try:
        UserSchema.model_validate(user_data)
        return True
    except ValueError as ex:
        logging.error(f"Invalid Data for Username {user_data.username}: {ex}")
        return False