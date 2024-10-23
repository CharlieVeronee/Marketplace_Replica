from flask import render_template
from flask_login import current_user
import datetime
from flask import render_template, redirect, url_for, flash, request
from werkzeug.urls import url_parse
from flask_login import login_user, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, PasswordField, BooleanField, SubmitField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
from flask import current_app as app
from flask import g
from humanize import naturaltime




from .models.myprofile_model import User_Info
from .models.reviews import Product_Reviews
from .models.user import User

from flask import jsonify
from flask import Blueprint
bp = Blueprint('myprofile', __name__)

def humanize_time(dt):
    return naturaltime(datetime.datetime.now() - dt)

class UIDForm(FlaskForm):
    uid = StringField('User ID', validators = [DataRequired()])
    submit = SubmitField('Search')

class UserLookupForm(FlaskForm):
    firstname = StringField('First Name')
    lastname = StringField('Last Name')
    submit = SubmitField('Search')


@bp.route('/profilepage', methods=['GET', 'POST'])
def profilepage():
    # if current_user.is_authenticated:
        # purchase = PurchaseItem.get_purchase(current_user.id)
        # return render_template('purchase.html', purchase = purchase)

        #form = UIDForm()
        #purchase = Purchase.get_purchase(form.uid.data)
        #return render_template('purchase.html', purchases = purchase, form=form, humanize_time=humanize_time)


    if not current_user.is_authenticated:
        return redirect(url_for('users.login'))
    user_id = current_user.id
    stuff = User_Info.get_info(user_id)

    user_photo = app.db.execute("SELECT photo FROM Users WHERE id = :user_id", user_id=user_id)
    g.user_photo = user_photo[0] if user_photo else None


    return render_template('profilepage.html', user =  current_user, reviews = Product_Reviews.get_seller_reviews(user_id), stars = Product_Reviews.get_average_seller_review(user_id), humanize_time = humanize_time)
    


@bp.route('/edit_email', methods=['POST'])
def edit_my_email():
    user_id = request.form.get('user_id')
    new_email = (request.form.get('new_email'))

    if '@' not in new_email or '.' not in new_email:
        flash('Error: Invalid email address. Please include "@" and "."', 'error')
        return redirect(url_for('myprofile.profilepage'))

    if User.email_exists(new_email):
        flash('Error: This email is already in use. Please choose another one.', 'error')
        return redirect(url_for('myprofile.profilepage'))

    result = User.edit_email(user_id, new_email)

    return redirect(url_for('myprofile.profilepage'))

@bp.route('/edit_password', methods=['POST'])
def edit_my_password():
    user_id = request.form.get('user_id')
    new_password = (request.form.get('new_password'))
    result = User.edit_password(user_id, new_password)

    return redirect(url_for('myprofile.profilepage'))

@bp.route('/edit_firstname', methods=['POST'])
def edit_my_firstname():
    user_id = request.form.get('user_id')
    new_firstname = (request.form.get('new_firstname'))
    result = User.edit_firstname(user_id, new_firstname)

    return redirect(url_for('myprofile.profilepage'))

@bp.route('/edit_lastname', methods=['POST'])
def edit_my_lastname():
    user_id = request.form.get('user_id')
    new_lastname = (request.form.get('new_lastname'))
    result = User.edit_lastname(user_id, new_lastname)

    return redirect(url_for('myprofile.profilepage'))

@bp.route('/edit_address', methods=['POST'])
def edit_my_address():
    user_id = request.form.get('user_id')
    new_address = (request.form.get('new_address'))
    result = User.edit_address(user_id, new_address)

    return redirect(url_for('myprofile.profilepage'))

@bp.route('/edit_isSeller', methods=['POST'])
def edit_my_isSeller():
    user_id = request.form.get('user_id')
    new_isSeller = request.form.get('new_isSeller') == 'on'
    result = User.edit_isSeller(user_id, new_isSeller)

    if new_isSeller == False:
        app.db.execute('''
        DELETE FROM Inventory
        WHERE user_id = :user_id    
    ''', user_id=user_id)


    return redirect(url_for('myprofile.profilepage'))

@bp.route('/edit_photo', methods=['POST'])
def edit_my_photo():
    user_id = request.form.get('user_id')
    new_photo = (request.form.get('new_photo'))

    app.db.execute('''
        UPDATE Users
        SET photo = :new_photo
        WHERE id = :user_id
    ''', user_id=user_id, new_photo=new_photo)

    return redirect(url_for('myprofile.profilepage'))


@bp.route('/profiles/<id>', methods=['GET', 'POST'])
def public_profile(id):
    # Fetch user data including the photo
    user_data = app.db.execute("""
        SELECT id, email, firstname, lastname, address, isSeller, photo
        FROM Users
        WHERE id = :user_id
    """, user_id=id)

    if user_data:
        user_data = user_data[0]

    if not user_data:
        # Handle case when user is not found
        flash('User not found', 'error')
        user = {}
        return render_template('variable_profiles.html', user=user, reviews = Product_Reviews.get_seller_reviews(id), num_reviews = Product_Reviews.num_seller_reviews(id), humanize_time=humanize_time)

    user = {
        'id': user_data[0],
        'email': user_data[1],
        'firstname': user_data[2],
        'lastname': user_data[3],
        'address': user_data[4],
        'isSeller': user_data[5],
        'photo': user_data[6]
    }

    return render_template('variable_profiles.html', user=user, reviews = Product_Reviews.get_seller_reviews(id), stars = Product_Reviews.get_average_seller_review(id), num_reviews = Product_Reviews.num_seller_reviews(id), humanize_time=humanize_time)

@bp.route('/userlookup', methods=['GET', 'POST'])
def userlookup():
    form = UserLookupForm()

    firstname_input = 'xxxxx' # Default value
    lastname_input = 'xxxxx'



    if form.validate_on_submit():
        firstname_input = form.firstname.data
        lastname_input = form.lastname.data

    
    firstname_input = '%' + firstname_input + '%' # change format of search string to %search_term% before using with SQL LIKE
    lastname_input = '%' + lastname_input + '%'
    


    rows = app.db.execute("""
        SELECT id, firstname, lastname, isSeller
        FROM Users
        WHERE LOWER(firstname) LIKE LOWER(:firstname_input) AND LOWER(lastname) LIKE LOWER(:lastname_input)
        """, firstname_input = firstname_input, lastname_input = lastname_input)


    users = []

    for row in rows:
        user_data = {
            'id': row[0],
            'firstname': row[1],
            'lastname': row[2],
            'isSeller':row[3]
        }
        users.append(user_data)

    if firstname_input != '%xxxxx%' and users == []:
        flash('User Does Not Exist')

    return render_template('user_database.html', users=users, form=form)

