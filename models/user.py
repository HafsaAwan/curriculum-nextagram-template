from models.base_model import BaseModel
import peewee as pw
from werkzeug.security import generate_password_hash
import re
from flask_login import UserMixin

class User(UserMixin,BaseModel):
    username = pw.CharField(unique=True, null=False)
    email = pw.CharField(unique=True, null=False)
    password_hash = pw.TextField(null=False)
    password = None

    def validate(self):
        # Email should be unique
        existing_user_email = User.get_or_none(User.email==self.email)
        if existing_user_email:
            self.errors.append(f"User with email {self.email} already exists!")
        # Username should be unique
        existing_user_username = User.get_or_none(User.username==self.username)
        # also check if current userid is not same as the newly created user so we can update details
        if existing_user_username and existing_user_username.id != self.id:
            self.errors.append(f"User with username {self.username} already exists!")
        
            # Password should be longer than 6 characters
            if len(self.password) <= 6:
                self.errors.append("Password is less than 6 characters")
            # Password should have both uppercase and lowercase characters
            # Password should have at least one special character (REGEX comes in handy here)
            has_lower = re.search(r"[a-z]", self.password)
            has_upper = re.search(r"[A-Z]", self.password)
            has_special = re.search(r"[\[ \] \* \$ \% \^ \& \# \@ \? ]", self.password)

            if has_lower and has_upper and has_special:
                self.password_hash = generate_password_hash(self.password)
            else:
                self.errors.append("Password either does not have upper, lower or special characters!")