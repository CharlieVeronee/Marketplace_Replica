from flask import render_template
from flask_login import current_user
import datetime
from flask import render_template, redirect, url_for, flash, request
from werkzeug.urls import url_parse
from flask_login import login_user, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, PasswordField, BooleanField, SubmitField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo



from .models.purchase import Purchase
from .models.cart import Cart

from humanize import naturaltime
def humanize_time_ago(dt):
    if dt:
        return naturaltime(dt)
    else:
        return "N/A"

def humanize_time(dt):
    if dt:
        return dt.strftime("%A, %B %d, %Y %I:%M%p")
    else:
        return "N/A"
    

from flask import jsonify
from flask import Blueprint
bp = Blueprint('purchases', __name__)

class UIDForm(FlaskForm):
    uid = IntegerField('User ID', validators = [DataRequired()])
    submit = SubmitField('Search')

@bp.route('/purchase', methods=['GET', 'POST'])
def get_purchase():
    # if current_user.is_authenticated:
        # purchase = PurchaseItem.get_purchase(current_user.id)
        # return render_template('purchase.html', purchase = purchase)

        #form = UIDForm()
        #purchase = Purchase.get_purchase(form.uid.data)
        #return render_template('purchase.html', purchases = purchase, form=form, humanize_time=humanize_time)


        if not current_user.is_authenticated:
            return redirect(url_for('users.login'))
        user_id = current_user.id
        sort_by = request.args.get('sort_by', 'time_newest')
        purchase = Cart.get_purchase(user_id, sort_by)
        return render_template('purchase.html', purchases = purchase, humanize_time=humanize_time, humanize_time_ago = humanize_time_ago)