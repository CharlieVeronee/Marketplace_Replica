from flask import render_template
from flask_login import current_user
from flask import render_template, redirect, url_for, flash, request
from flask_wtf import FlaskForm
from wtforms import IntegerField, SubmitField
from wtforms import StringField
from wtforms.validators import DataRequired
from flask_babel import _, lazy_gettext as _l
from flask import current_app
from flask_login import current_user


from .models.user import User
from .models.cart import Cart
from .models.balances import BalanceItem
from .models.inventory import Inventory


from flask import jsonify
from flask import Blueprint
bp = Blueprint('cart', __name__)

import datetime

def humanize_time(dt):
    if dt:
        return dt.strftime("%A, %B %d, %Y %I:%M%p")
    else:
        return "N/A"


#initial cart search for previous milestone

#class UIDForm(FlaskForm):
    #uid = IntegerField('User ID', validators = [DataRequired()])
    #submit = SubmitField('Search')

#@bp.route('/cart/search', methods=['GET', 'POST'])
#def get_cart1():
        #form = UIDForm()
        #cart = Cart.get_cart(form.uid.data)
        #return render_template('cartsearch.html', cart = cart, form=form)


@bp.route('/add-to-cart', methods=['POST'])
def add_to_cart():
    product_id = request.form.get('product_id')
    seller_id = request.form.get('seller')
    quantity = request.form.get('quantity')
    if quantity == '':
         quantity = 1
    if not current_user.is_authenticated:
        return redirect(url_for('users.login'))
    if product_id and seller_id:
        available = Inventory.get_quantity(float(seller_id), float(product_id))
        if float(quantity) > float(available):
            return render_template('inventory_warning.html')
    Cart.add_item_to_cart(current_user.id, product_id, seller_id, quantity)
    user_id = current_user.id
    balance = float(BalanceItem.get_balance(user_id)[0][0])
    cart = Cart.get_cart(user_id)
    checkout = checkout2()
    totalPrice = 0.00
    # arrays for diff changes to cart
    adjustq = []
    remove= []
    save = []
    for i in range(0, len(cart)):
            cart_item = cart[i]
            totalPrice += float(cart[i].price) * float(cart[i].quantity)
            adjust_quantity = adjustQuantity(prefix = cart_item.name + str(cart_item.seller_id))
            remove_product = removeProduct(prefix = cart_item.name + str(cart_item.seller_id))
            save_product = saveProduct(prefix = str(cart_item.product_id) + str(cart_item.seller_id))
            adjustq.append(adjust_quantity)
            remove.append(remove_product)
            save.append(save_product)


            if adjust_quantity.submit.data and adjust_quantity.validate_on_submit():
                available= Inventory.get_quantity(cart[i].seller_id, cart[i].product_id)
                if available == 0:
                        flash(f"{cart[i].seller} currently has none of \'{cart[i].name}\' in stock. Either remove the product or check in later.")
                if adjust_quantity.quantity.data < 0:
                    flash("no negative quantities cmon now")
                elif adjust_quantity.quantity.data > available:
                    flash(f"{cart[i].seller} does not have the inventory to accommodate the new desired quantity for \'{cart[i].name}\'")
                else:
                    Cart.adjust_quantity(user_id, cart_item.product_id, cart_item.seller_id, adjust_quantity.quantity.data)
                return redirect(url_for('cart.get_cart2'))
               
            if save_product.validate_on_submit():
                Cart.check_saved(user_id, cart_item.seller_id, cart_item.product_id)
                return redirect(url_for('cart.return_saved'))


            if remove_product.validate_on_submit():
                Cart.remove_product(user_id, cart_item.product_id, cart_item.seller_id)
                return redirect(url_for('cart.get_cart2'))
            
            if checkout.validate_on_submit():
                return redirect(url_for('cart.checkout'))
           
    return render_template('cart.html', cart = cart, adjustq = adjustq, remove = remove, save = save, totalPrice=round(totalPrice, 2), balance = round(balance,2), checkout = checkout)


class adjustQuantity(FlaskForm):
    quantity = IntegerField(_l('Qty'), validators=[DataRequired()])
    submit = SubmitField('Adjust Quantity')


class removeProduct(FlaskForm):
    submit = SubmitField('Remove')


class saveProduct(FlaskForm):
    submit = SubmitField('Save For Later')


@bp.route('/cart/', methods=['GET', 'POST'])
def get_cart2():
        if not current_user.is_authenticated:
            return redirect(url_for('users.login'))
        user_id = current_user.id
        balance = float(BalanceItem.get_balance(user_id)[0][0])
        cart = Cart.get_cart(user_id)
        checkout = checkout2()
        totalPrice = 0.00
        # arrays for diff changes to cart
        adjustq = []
        remove= []
        save = []
        for i in range(0, len(cart)):
               cart_item = cart[i]
               totalPrice += float(cart[i].price) * float(cart[i].quantity)
               adjust_quantity = adjustQuantity(prefix = cart_item.name + str(cart_item.seller_id))
               remove_product = removeProduct(prefix = cart_item.name + str(cart_item.seller_id))
               save_product = saveProduct(prefix = str(cart_item.product_id) + str(cart_item.seller_id))
               adjustq.append(adjust_quantity)
               remove.append(remove_product)
               save.append(save_product)

               if adjust_quantity.submit.data and adjust_quantity.validate_on_submit():
                    available= Inventory.get_quantity(cart[i].seller_id, cart[i].product_id)
                    if available == 0:
                        flash(f"{cart[i].seller} currently has none of \'{cart[i].name}\' in stock. Either remove the product or check in later.")
                    if adjust_quantity.quantity.data < 0:
                         flash("No Negative Quantities Cmon Now")
                    elif adjust_quantity.quantity.data > available:
                        flash(f"{cart[i].seller} does not have the inventory to accommodate the new desired quantity for \'{cart[i].name}\'")
                    else:
                        Cart.adjust_quantity(user_id, cart_item.product_id, cart_item.seller_id, adjust_quantity.quantity.data)
                    return redirect(url_for('cart.get_cart2'))
                
    
               if save_product.validate_on_submit():
                    Cart.check_saved(user_id, cart_item.seller_id, cart_item.product_id)
                    return redirect(url_for('cart.return_saved'))


               if remove_product.validate_on_submit():
                    Cart.remove_product(user_id, cart_item.product_id, cart_item.seller_id)
                    return redirect(url_for('cart.get_cart2'))
               
               if checkout.validate_on_submit():
                    return redirect(url_for('cart.checkout'))


        return render_template('cart.html', cart = cart, adjustq = adjustq, remove = remove, save = save, totalPrice=round(totalPrice, 2), balance = round(balance,2), checkout = checkout)


class moveToCart(FlaskForm):
    submit = SubmitField('Move to Cart')



@bp.route('/saved/', methods=['GET', 'POST'])
def return_saved():
    if not current_user.is_authenticated:
        return redirect(url_for('users.login'))
    user_id = current_user.id
   
    saved_items = Cart.get_saved(user_id)
    remove = []
    send = []


    for i in range(0, len(saved_items)):
        saved_item = saved_items[i]
        remove_product = removeProduct(prefix = saved_item.name + str(saved_item.seller_id))
        to_cart = moveToCart(prefix = str(saved_item.product_id) + str(saved_item.seller_id))
        remove.append(remove_product)
        send.append(to_cart)


        if remove_product.validate_on_submit():
            Cart.remove_product(user_id, saved_item.product_id, saved_item.seller_id)
            return redirect(url_for('cart.return_saved'))


        if to_cart.validate_on_submit():
            Cart.check_saved(user_id, saved_item.seller_id, saved_item.product_id)
            return redirect(url_for('cart.get_cart2'))
        
    return render_template('saved.html', saved_items = saved_items, remove = remove, send = send)




class checkout2(FlaskForm):
    submit = SubmitField('Checkout')


@bp.route('/checkout', methods=['GET', 'POST'])
def checkout():
    if not current_user.is_authenticated:
        return redirect(url_for('users.login'))
    checkout = checkout2()
    user_id = current_user.id
    totalPrice = 0.00
    cart = Cart.get_cart(user_id)
    balance = float(BalanceItem.get_balance(user_id)[0][0])



    for i in range(0, len(cart)):
        totalPrice += float(cart[i].price) * float(cart[i].quantity)
        available= Inventory.get_quantity(cart[i].seller_id, cart[i].product_id)
        if available == 0:
                flash(f"{cart[i].seller} currently has none of \'{cart[i].name}\' in stock. Either remove the product or check in later.")
        if cart[i].quantity > available:
             flash(f"{cart[i].seller} does not have the inventory to accommodate the desired purchase quantity for \'{cart[i].name}\'")
             break
        else:
            if (totalPrice > balance):
                flash('You do not have enough money in your account to complete this purchase.')
                break
            else:
                BalanceItem.update_balance(user_id, balance - totalPrice)
                Cart.new_order(user_id)
                new_order_id = Cart.get_max_id()[0][0]
                for i in range(0, len(cart)):
                    # decrement seller inventory
                    total_quantity = Inventory.get_quantity(cart[i].seller_id, cart[i].product_id)
                    quantity_remaining = total_quantity - cart[i].quantity
                    Inventory.upd_qty(cart[i].product_id, quantity_remaining, cart[i].seller_id)
                    # to increment seller balance
                    current_seller_balance = float(BalanceItem.get_balance(cart[i].seller_id)[0][0])
                    item_total_price =  float(cart[i].price * cart[i].quantity)
                    BalanceItem.update_balance(cart[i].seller_id, current_seller_balance + item_total_price)
                    Cart.set_order(cart[i].id, new_order_id)
                return redirect(url_for('cart.order_results', order_id = new_order_id))
    adjustq = []
    remove= []
    save = []
    for i in range(0, len(cart)):
            cart_item = cart[i]
            totalPrice += float(cart[i].price) * float(cart[i].quantity)
            adjust_quantity = adjustQuantity(prefix = cart_item.name + str(cart_item.seller_id))
            remove_product = removeProduct(prefix = cart_item.name + str(cart_item.seller_id))
            save_product = saveProduct(prefix = str(cart_item.product_id) + str(cart_item.seller_id))
            adjustq.append(adjust_quantity)
            remove.append(remove_product)
            save.append(save_product)


            if adjust_quantity.submit.data and adjust_quantity.validate_on_submit():
                    available= Inventory.get_quantity(cart[i].seller_id, cart[i].product_id)
                    if available == 0:
                        flash(f"{cart[i].seller} currently has none of \'{cart[i].name}\' in stock. Either remove the product or check in later.")
                    if adjust_quantity.quantity.data < 0:
                         flash("No Negative Quantities Cmon Now")
                    elif adjust_quantity.quantity.data > available:
                        flash(f"{cart[i].seller} does not have the inventory to accommodate the new desired quantity for \'{cart[i].name}\'")
                    else:
                        Cart.adjust_quantity(user_id, cart_item.product_id, cart_item.seller_id, adjust_quantity.quantity.data)
                    return redirect(url_for('cart.get_cart2'))
               
            if save_product.validate_on_submit():
                Cart.check_saved(user_id, cart_item.seller_id, cart_item.product_id)
                return redirect(url_for('cart.return_saved'))


            if remove_product.validate_on_submit():
                Cart.remove_product(user_id, cart_item.product_id, cart_item.seller_id)
                return redirect(url_for('cart.get_cart2'))
            
    return render_template('cart.html', cart = cart, adjustq = adjustq, remove = remove, save = save, totalPrice=round(totalPrice, 2), balance = round(balance,2), checkout = checkout)
    
class DeliveryAddressForm(FlaskForm):
    delivery_address = StringField('Delivery Address', validators=[DataRequired()])
    submit = SubmitField('Add Address')
    def __str__(self):
        return f"DeliveryAddressForm(delivery_address={self.delivery_address.data})"

@bp.route('/order/<order_id>/success', methods=['GET', 'POST'])
def order_results(order_id):
    delivery_addy = DeliveryAddressForm(prefix = str(order_id))
    order_items = Cart.get_from_order_id(order_id)
    totalPrice = 0
    for i in range(0, len(order_items)):
        totalPrice += order_items[i].total
    
    if delivery_addy.submit.data and delivery_addy.validate_on_submit():
         delivery_addy_str = str(delivery_addy.delivery_address.data)
         Cart.set_delivery_addy(order_id, delivery_addy_str)
         return render_template('congrats_order.html')

    return render_template('indv_order.html', order_id=order_id, order_items = order_items,
                           total_price=round(totalPrice, 2), form = delivery_addy)

@bp.route('/orders')
def get_orders():
    if not current_user.is_authenticated:
        return redirect(url_for('users.login'))
    user_id = current_user.id

    users_orders = Cart.get_orders(user_id)

    total_order_items = Cart.get_all_orders(user_id)

    total_prices = []
    for order in users_orders:
         total_price = 0.00
         indv_order = Cart.get_from_order_id(order.id)
         order_fulfilled = True
         for line in indv_order:
              if line.fulfilled == False:
                   order_fulfilled = False
              total_price += float(line.total)
        
         if order_fulfilled:
            Cart.set_fulfilled(order.id)
         total_prices.append(total_price)


    return render_template('buyer_orders.html', users_orders = users_orders, total_prices = total_prices, total_order_items = total_order_items, humanize_time=humanize_time)
