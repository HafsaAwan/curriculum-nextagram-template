from models.base_model import BaseModel
import peewee as pw
from models.user import User 

class FanIdol(BaseModel):
    fan = pw.ForeignKeyField(User, backref="myfans", on_delete="CASCADE")
    idol = pw.ForeignKeyField(User, backref="myidols", on_delete="CASCADE")
    is_approved = pw.BooleanField(default=False)

    class Meta:
        indexes = (
            # create unique rows
            (('fan', 'idol'), True),
        )