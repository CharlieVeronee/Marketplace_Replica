from flask import render_template, request, flash, redirect, url_for
from flask_login import current_user
from flask_paginate import Pagination, get_page_parameter
import datetime
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, IntegerField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo

from .models.product import Product
from .models.purchase import Purchase
from .models.inventory import Inventory

from flask import Blueprint
bp = Blueprint('invhub', __name__)

class QTYForm(FlaskForm):
    qty = IntegerField('Update Quantity', validators=[DataRequired()])
    submit = SubmitField('Update')

@bp.route('/invhub', methods=['GET', 'POST'])
def invhub():
    # get inventory for user if authenticated:

    page = request.args.get(get_page_parameter(), type=int, default=1)

    pagination = Pagination(page=page, total = Inventory.num_products(current_user.id), record_name='products', per_page=40)

    if current_user.is_authenticated:
        curr_selling = Inventory.get_inv(
            current_user.id, page=page)
    else:
        curr_selling = None
   
    # render the page by adding information to the index.html file
    return render_template('invhub.html',
                           selling_inv=curr_selling, pagination=pagination)


@bp.route('/delete', methods=['GET', 'POST'])
def delete():
    product_id = request.form.get('pid')
    
    Inventory.del_inv(current_user.id, product_id)

    # Have to check if all quantities of the product equal 0 before making it unavailable
    if Inventory.inv_prod_check(product_id) == 0:
        Inventory.upd_prodav(product_id)

    # if del_result and upd_result:
    #     flash('Deletion successful!', 'success')
    # else:
    #     flash('You can\'t delete a nonexistent item.', 'error')

    return redirect(url_for('invhub.invhub'))

@bp.route('/updateqty', methods=['GET', 'POST'])
def updateQTY():
    product_id = request.form.get('pid')

    form = QTYForm()

    new_quantity = request.form.get('qty_num')

    if new_quantity and int(new_quantity) >= 0:
        Inventory.upd_qty(product_id, new_quantity, current_user.id)
        if int(new_quantity) >= 1:
            Inventory.upd_prodavtr(product_id)
        elif int(new_quantity) == 0 and Inventory.inv_prod_check(product_id) == 0:
            Inventory.upd_prodav(product_id)
        flash('Quantity Successfully Updated')
    else:
        flash('Invalid Input')

    return redirect(url_for('invhub.invhub'))


# Shows seller the specific details about the order relating to them
@bp.route('/order_details/<order_id>', methods=['GET', 'POST'])
def order_details(order_id):

    rows, total_items = Inventory.get_order_details(order_id, current_user.id)
    return render_template('order_s_details.html', rows=rows, total=total_items)


# Allows user to set their part of the order to fulfilled
@bp.route('/fulfill', methods=['GET', 'POST'])
def fulfill_ord():

    oid = request.form.get('oid')

    Inventory.fulfill(oid, current_user.id)
    Inventory.time_fulfill(oid, current_user.id)

    flash("Order has been Fulfilled!")

    return redirect(url_for('inventory.see_orders'))

@bp.route('/statistics', methods=['GET', 'POST'])
def analytics():

    topTenProds = Inventory.topTenProducts(current_user.id)

    botTenProds = Inventory.botTenProducts(current_user.id)

    topFiveBuyers = Inventory.topFiveBuyers(current_user.id)

    totalProf = Inventory.totalProf(current_user.id)

    return render_template('seller_analytics.html', ten=topTenProds, bten=botTenProds, five=topFiveBuyers, profit=totalProf)
