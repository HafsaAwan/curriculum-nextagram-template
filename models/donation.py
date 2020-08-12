import peewee as pw
from models.base_model import BaseModel
from models.user import User
from models.image import Image
from playhouse.hybrid import hybrid_property

class Donation(BaseModel):
    amount = pw.DecimalField()
    image = pw.ForeignKeyField(Image, backref="donations")
    sender = pw.ForeignKeyField(User, backref="donations")