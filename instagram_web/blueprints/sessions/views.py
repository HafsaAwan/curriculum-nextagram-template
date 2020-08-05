from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models.user import User
import peewee as pw
from werkzeug.security import check_password_hash

sessions_blueprint = Blueprint('sessions',
                            __name__,
                            template_folder='templates')

@sessions_blueprint.route('/new', methods=['GET'])
def new():
    return render_template('sessions/new.html')

@sessions_blueprint.route('/', methods=['POST'])
def create():
    params = request.form
    username = params.get('username')
    password_to_check = params.get('password')
    
    user = User.get(User.username == username)
    if user:
        hashed_password = user.password_hash # password hash stored in database for a specific user
        result = check_password_hash(hashed_password, password_to_check)

        if result:
            session["user_id"] = user.id
            flash("Successfuly Signed In!")
            return redirect(url_for('home'))
    else:
        self.errors.append(f"Username does not exist. Please try again")
        return render_template('sessions/new.html')
    
@sessions_blueprint.route('/', methods=['POST'])
def destroy():
    session.destroy()
    return render_template('home.html')