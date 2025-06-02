from flask import render_template, redirect, url_for, flash, request
from werkzeug.urls import url_parse
from flask_login import login_user, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo

from decimal import Decimal, InvalidOperation


from .models.balances import BalanceItem


from flask import Blueprint
bp = Blueprint('balances', __name__)


class UIDForm(FlaskForm):
    uid = StringField('User ID', validators = [DataRequired()])
    submit = SubmitField('Search')


@bp.route('/balances', methods=['GET', 'POST'])
def balances():


    #form = UIDForm()
    #balances = BalanceItem.get_balance(form.uid.data)
    #return render_template('balance.html', balances = balances, form=form)


    if not current_user.is_authenticated:
        return redirect(url_for('users.login'))
    user_id = current_user.id
    balance = BalanceItem.get_balance(user_id)
    return render_template('balance.html', balances = balance)

@bp.route('/withdraw', methods=['POST'])
def withdraw():
    user_id = request.form.get('user_id')

    
    withdrawal_amount_str = request.form.get('withdrawal_amount')

    # Check if withdrawal_amount is a valid number
    try:
        withdrawal_amount = Decimal(withdrawal_amount_str)
    except InvalidOperation:
        flash('Invalid withdrawal amount. Please enter a valid number.', 'error')
        return redirect(url_for('balances.balances'))
    


    withdrawal_result = BalanceItem.withdraw(user_id, withdrawal_amount)

    if withdrawal_result is not False:
        flash('Withdrawal successful!', 'success')
    else:
        flash('You can\'t overdraw your account or withdrawal less than zero.', 'error')



    return redirect(url_for('balances.balances'))

@bp.route('/deposit', methods=['POST'])
def deposit():
    user_id = request.form.get('user_id')
    deposit_amount_str = request.form.get('deposit_amount')

    # Check if deposit_amount is a valid number
    try:
        deposit_amount = Decimal(deposit_amount_str)
    except InvalidOperation:
        flash('Invalid deposit amount. Please enter a valid number.', 'error')
        return redirect(url_for('balances.balances'))




    deposit_result = BalanceItem.deposit(user_id, deposit_amount)

    if deposit_result is not False:
        flash("Deposit Successful")
    else:
        flash('You can\'t deposit less than zero.', 'error')

    return redirect(url_for('balances.balances'))