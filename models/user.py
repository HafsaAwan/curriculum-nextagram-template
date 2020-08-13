from models.base_model import BaseModel
import peewee as pw
from werkzeug.security import generate_password_hash
import re
from flask_login import UserMixin
from playhouse.hybrid import hybrid_property


class User(UserMixin,BaseModel):
    username = pw.CharField(unique=True, null=False)
    email = pw.CharField(unique=True, null=False)
    password_hash = pw.TextField(null=False)
    password = None
    image_path = pw.TextField(null=True)
    is_private = pw.BooleanField(default=False)

    @hybrid_property
    def full_image_path(self):
        if self.image_path:
            from app import app
            return app.config.get("S3_LOCATION") + self.image_path
        else:
            return ""
    
    def follow_status(self, idol):
        from models.fanidol import FanIdol
        return FanIdol.get_or_none(FanIdol.fan==self.id, FanIdol.idol==idol.id)
           

    def follow(self, idol):
        from models.fanidol import FanIdol
        # if relationship/row exists, return false
        if FanIdol.get_or_none(FanIdol.fan == self.id, FanIdol.idol == idol.id):
            return False
        else:
            if idol.is_private:
                FanIdol.create(fan = self.id, idol=idol.id, is_approved=False)
            else:
                FanIdol.create(fan=self.id, idol=idol.id, is_approved=True)

            return True
    
    def unfollow(self,idol):
        from models.fanidol import FanIdol
        FanIdol.delete().where(self.id == FanIdol.fan and idol == FanIdol.idol).execute()
        return True

    @hybrid_property
    def fans(self):
        from models.fanidol import FanIdol
        fans = FanIdol.select().where(FanIdol.idol == self.id, FanIdol.is_approved==True)
        fans_list = []
        for fan in fans:
            fans_list.append(fan.fan)
        return fans_list
    
    @hybrid_property
    def idols(self):
        from models.fanidol import FanIdol
        # get a list of idols
        idols = FanIdol.select().where(FanIdol.fan == self.id, FanIdol.is_approved==True)
        idols_list = []
        for idol in idols:
            idols_list.append(idol.idol)
        return idols_list
        # another way:
        # idols = FanIdol.select(FanIdol.idol).where(FanIdol.fan==self.id, FanIdol.is_approved==True)   
        # return User.select().where( User.id.in_(idols) )


    @hybrid_property
    def idol_requests(self):
        from models.fanidol import FanIdol
        idols = FanIdol.select(FanIdol.idol).where(FanIdol.fan==self.id, FanIdol.is_approved==False) 
        return User.select().where( User.id.in_(idols) )
        # another way:
        # idols_request = []
        # for idol in idols_request:
        #     idols_request.append(idol.idol)
        # return idols_request

    @hybrid_property
    def fan_requests(self):
        from models.fanidol import FanIdol
        fans = FanIdol.select(FanIdol.fan).where(FanIdol.idol==self.id, FanIdol.is_approved==False)   
        return User.select().where( User.id.in_(fans) )
    
    @hybrid_property
    def approve_request(self,fan):
        from models.fanidol import FanIdol
        # get the relationship
        relationship = fan.follow_status(self)
        # update the is_approved to true
        relationship.is_approved = True
        return relationship.save()
        
    def validate(self):
        # Email should be unique
        existing_user_email = User.get_or_none(User.email==self.email)
        if existing_user_email and existing_user_email.id != self.id:
            self.errors.append(f"User with email {self.email} already exists!")
        # Username should be unique
        existing_user_username = User.get_or_none(User.username==self.username)
        # also check if current userid is not same as the newly created user so we can update details
        if existing_user_username and existing_user_username.id != self.id:
            self.errors.append(f"User with username {self.username} already exists!")
        
        # Password should be longer than 6 characters
        if self.password:
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