from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models.user import User
import peewee as pw
from werkzeug.security import check_password_hash
from flask_login import login_user, logout_user, login_required
from instagram_web.util.google_oauth import oauth

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
    # if username exists check for password
    if user:
        hashed_password = user.password_hash # password hash stored in database for a specific user
        result = check_password_hash(hashed_password, password_to_check)

        if result:
            # session["user_id"] = user.id
            flash("Successfuly Signed In!", "success")
            # save user id in browser session
            login_user(user)
            return redirect(url_for("users.show", username=user.username))  # then redirect to profile page
        else:
            flash("Password incorrect. Please try again","danger")
            return render_template('sessions/new.html')
    else:
        flash("User not found", "danger")
        return render_template("sessions/new.hrml")
    
@sessions_blueprint.route('/delete', methods=['POST'])
@login_required
def destroy():
    # remove user from the browser session
    logout_user()
    flash("Logout Successful!", "success")
    return redirect(url_for("sessions.new"))

@sessions_blueprint.route("/google_login")
def google_login():
    redirect_uri = url_for('sessions.authorize', _external = True)
    return oauth.google.authorize_redirect(redirect_uri)

@sessions_blueprint.route('/authorize/google')
def authorize():
    oauth.google.authorize_access_token()
    email = oauth.google.get('https://www.googleapis.com/oauth2/v2/userinfo').json()['email']
    user = User.get_or_none(User.email == email)

    if user:
        login_user(user)
        return redirect(url_for("users.show", username=user.username))
    else:
        flash("Login failed. Please try again!", "error")
        redirect(url_for('sessions.new'))