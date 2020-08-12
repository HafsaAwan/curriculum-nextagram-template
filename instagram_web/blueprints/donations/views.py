from flask import Blueprint,render_template,redirect,url_for,flash, request
from werkzeug import secure_filename
from instagram_web.util.helpers import gateway
from models.donation import Donation
from models.user import User
from flask_login import current_user,login_required
import requests

donations_blueprint = Blueprint('donations',
                            __name__,
                            template_folder='templates')


@donations_blueprint.route("/new", methods=["GET"])
@login_required
def new(image_id):
    client_token= gateway.client_token.generate()
    return render_template("donations/new.html", client_token=client_token, image_id=image_id)


@donations_blueprint.route("/", methods=["POST"])
@login_required
def create(image_id):
    amount= request.form["amount"]
    result = gateway.transaction.sale({
    "amount": amount,
    "payment_method_nonce": request.form["payment_method_nonce"],
    "options": {
        "submit_for_settlement": True
    }
    })

    if result.is_success or result.transaction:
        donation = Donation(sender=User.get_by_id(current_user.id), image_id=image_id, amount=amount)
        donation.save()
        return redirect(url_for('images.show', id=image_id))
    else:
        flash("Failed to donate. Please try again", "error")
        return redirect(url_for('donations.new', image_id=image_id))