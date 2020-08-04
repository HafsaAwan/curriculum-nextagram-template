from models.base_model import BaseModel
import peewee as pw


class User(BaseModel):
    name = pw.CharField(unique=True)
    password = pw.TextField()
    email = pw.TextField(unique=True)
