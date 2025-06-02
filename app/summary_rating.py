from flask import render_template, redirect, url_for, flash, request
from werkzeug.urls import url_parse
from flask_login import login_user, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, IntegerField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo

from .models.summary_rating import Seller_Reviews
from .models.summary_rating import Product_Reviews


from flask import Blueprint
bp = Blueprint('summary_rating', __name__)

class FilterForm(FlaskForm):
    identifier = StringField(u'Enter the email of a seller or the name of a product:')
    requested_type = SelectField(u'Type:', choices=[('SELLER', 'Seller'), ('PRODUCT', 'Product')], validators=[DataRequired()])
    submit = SubmitField('Search')

@bp.route('/summary_rating', methods=['GET', 'POST'])
def summary_rating():
    form = FilterForm()
    summary_rating = Product_Reviews.get_summary_rating(form.identifier.data, form.requested_type.data)
    # if form.validate_on_submit():
    #     if form.filterAmount.data < 1 or form.filterAmount.data > 100:
    #         flash('You can only display 1 to 100 reviews at a time!')
    #         return redirect(url_for('reviews.reviews'))
    return render_template('summary_rating.html', summary_rating = summary_rating, form=form)
