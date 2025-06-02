from flask import render_template, redirect, url_for, flash, request
from werkzeug.urls import url_parse
from flask_login import login_user, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, IntegerField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
from flask_ckeditor import CKEditorField
from flask_paginate import Pagination, get_page_parameter
from flask_login import current_user

from .models.inventory import Inventory

from flask import Blueprint
bp = Blueprint('inventory', __name__)


class UIDForm(FlaskForm):
    uid = StringField('Seller ID', validators=[DataRequired()])
    submit = SubmitField('Search')

@bp.route('/inventory', methods=['GET', 'POST'])
def inventory():
    # get all available products in a sellers inventory:
    form = UIDForm()

    page = request.args.get(get_page_parameter(), type=int, default=1)

    products = Inventory.get_inv(form.uid.data, page=page)

    # fix pagination issue where inputted id does not save
    pagination = Pagination(page=page, total = Inventory.num_products(form.uid.data), record_name='products', per_page=40)

    if not form.uid.data:
        return render_template('inventory.html', form=form, pagination=pagination)
    

    return render_template('inventory.html',
                        selling_products=products,
                        form = form, pagination=pagination)

@bp.route('/addInv', methods=['GET', 'POST'])
def addToInv():
    product_id = request.form.get('pid')

    # Check to see if the user inventory already sells the product before adding it 
    if Inventory.inv_prod(current_user.id, product_id):
        flash("You already sell this product")
    else:  
        Inventory.set_inv(current_user.id, product_id, 0)
    

    # if del_result and upd_result:
    #     flash('Deletion successful!', 'success')
    # else:
    #     flash('You can\'t delete a nonexistent item.', 'error')

    return redirect(url_for('invhub.invhub'))

@bp.route('/seller_orders', methods=['GET', 'POST'])
def see_orders():

    page = request.args.get(get_page_parameter(), type=int, default=1)

    seller_id = current_user.id

    pagination = Pagination(page=page, total = Inventory.num_orders(seller_id), record_name='orders', per_page=40)

    orders = Inventory.get_orders(seller_id, page=page)

    return render_template('seller_orders.html',
                        seller_ord = orders, pagination=pagination)