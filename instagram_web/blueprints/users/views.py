from flask import Blueprint, render_template, request, redirect, url_for, flash
from models.user import User
import re
from flask_login import login_user, logout_user, login_required, current_user
from instagram_web.util.helpers import upload_file_to_s3
from werkzeug import secure_filename

users_blueprint = Blueprint('users',
                            __name__,
                            template_folder='templates')


@users_blueprint.route('/new', methods=['GET'])
def new():
    return render_template('users/new.html')

@users_blueprint.route('/', methods=['POST'])
def create():
    params = request.form
    new_user = User(username=params.get("username"), email=params.get("email"), password=params.get("password"))
  
    if new_user.save():
        flash("Successfully Signed Up!","success")
        return redirect(url_for("users.show", username=new_user.username))  # then redirect to profile page
    else:
        flash(new_user.errors, "danger")
        return redirect(url_for("users.new"))
        


@users_blueprint.route('/<username>', methods=["GET"])  # user profile page
@login_required   # only can access this route after signed in
def show(username):
    user = User.get_or_none(User.username == username) # check whether user exist in database
    if user:
        return render_template("users/show.html",user=user)
    else:
        flash(f"No {username} user found.", "danger" )
        return redirect(url_for('home'))


@users_blueprint.route('/', methods=["GET"])
def index():
    users = User.select()
    return render_template('home.html', users=users)


@users_blueprint.route('/<id>/edit', methods=['GET'])
@login_required
def edit(id):
    user = User.get_or_none(User.id == id)
    if user:
        if current_user.id == int(id):
            return render_template('users/edit.html',user=user)
        else:
            flash("Edit not allowed for other users")
            redirect(url_for("users.show", username = user.username))
    else:
        flash("No user found. Please login or sign up")
        redirect(url_for("home"))  
    


@users_blueprint.route('/<id>', methods=['POST'])
def update(id):
    user = User.get_or_none(User.id == id)

    if user:
        if current_user.id == int(id):
            params = request.form

            user.username = params.get("username")
            user.email = params.get("email")

            password = params.get("password")
            if len(password) > 0:
                user.password = password
            if user.save():
                flash("Successfully updated details!")
                return redirect(url_for("users.show", username= user.username))
            else:
                flash("Unable to edit!")
                for err in user.errors:
                    flash(err)
                return redirect(url_for("users.edit", id=user.id))
        else:
            flash("Cannot edit users other than yourself!")
            return redirect(url_for("users.show", username=user.username))
    else:
        flash("No such user!")
        redirect(url_for("home"))

@users_blueprint.route('/<id>/upload', methods=['POST'] )
@login_required
def upload(id):
    user = User.get_or_none(User.id == id)

    if user:
        if current_user.id == int(id):
            # We check the request.files object for a user_file key. (user_file is the name of the file input on our form). If it's not there, we return an error message.
            if "profile_image" not in request.files:
                flash("No file provided!")
                return redirect(url_for('users.edit', id = id))

            # If the key is in the object, we save it in a variable called file.
            file = request.files["profile_image"]
            
            # we sanitize the filename using the secure_filename helper function provided by the werkzeurg.security module.
            file.filename = secure_filename(file.filename)

            # get path to image on S3 bucket using function in helper.py
            image_path = upload_file_to_s3(file, user.username)

            # update user with image path
            user.image_path = image_path
 
            # if user save successfull, redirect to show user show page
            if user.save():
                flash("Yayyy! Avatar uploaded!", "success")
                return redirect(url_for("users.show", username = user.username))
            else:
                # flash error message and redirect to edit page 
                flash("Failed to upload avatar. Please try again!")
                return redirect(url_for("users.edit", id = id))
        else:
            # current user is not same as one trying to upload
            flash("Cannot edit avatar of other users!","danger")
            return redirect(url_for("users.show", username = user.username))
    else:
        # if no no user
        flash("No such user found!", "danger")
        return redirect(url_for('home')) 

                