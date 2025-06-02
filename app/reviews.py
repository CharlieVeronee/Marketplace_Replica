import os
import uuid
import datetime
from flask import current_app as app
from flask import render_template, redirect, url_for, flash, request
from werkzeug.urls import url_parse
from flask_login import login_user, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, PasswordField, BooleanField, SubmitField, SelectField, IntegerField, MultipleFileField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, InputRequired, NumberRange
from flask import Flask
from werkzeug.utils import secure_filename
from flask_paginate import Pagination, get_page_parameter
from flask_ckeditor import CKEditor, CKEditorField
from humanize import naturaltime

from .models.reviews import Seller_Reviews
from .models.reviews import Product_Reviews

from datetime import datetime

from flask import Blueprint
bp = Blueprint('reviews', __name__)

def humanize_time(dt):
    return naturaltime(datetime.now() - dt)

class AllForm(FlaskForm):
    filterType = SelectField(u'Filter by:', choices=[('RECENT', 'Most Recent - Oldest'), ('OLDEST', 'Oldest - Most Recent'), ('HIGHEST', 'Highest Review - Lowest Review')], validators=[DataRequired()])
    submit = SubmitField('Search')

class AllForm2(FlaskForm):
    filterType = SelectField(u'Filter by:', choices=[('RECENT', 'Most Recent - Oldest'), ('OLDEST', 'Oldest - Most Recent'), ('HIGHEST', 'Highest Review - Lowest Review')], validators=[DataRequired()])
    submit = SubmitField('Search')

@bp.route('/reviews', methods=['GET', 'POST'])
def reviews():
    form2 = AllForm2()
    if current_user.is_authenticated:
        if request.method == 'POST' and form2.validate():
            # print(current_user.id, form.filterType.data, form.filterAmount.data)
            if form2.filterAmount.data < 1 or form2.filterAmount.data > 100:
                flash('Please enter a number between 1 and 100!')
                return redirect(url_for('reviews.reviews'))
        print(current_user.id, form2.filterType.data, form2.filterAmount.data)
        reviews = Product_Reviews.get_reviews_of_me(current_user.id, form2.filterType.data, form2.filterAmount.data)
            # print(reviews)
        if request.method == 'POST' and form2.validate():
            # print(current_user.id, form.filterType.data, form.filterAmount.data)
            if reviews is None:
                flash('You do not have any reviews of yourself!')
                return redirect(url_for('reviews.reviews'))
    # reviews = Product_Reviews.get_reviews(user_id, form.filterType.data, form.filterAmount.data)
    # if request.method == 'POST' and form.validate():
    #     if Product_Reviews.validate_id(user_id):
    #         flash('This User ID does not exist!')
    #         return redirect(url_for('reviews.reviews'))
    #     if len(reviews) == 0:
    #         flash('This user has not created any reviews!')
    #         return redirect(url_for('reviews.reviews'))
        return render_template('user_reviews.html', user_reviews = reviews, form=form2)
    else:
        flash('You must be logged in to view reviews of yourself!')
        return redirect(url_for('users.login'))

class CreateReviewForm(FlaskForm):
    reviewType = SelectField(u'Type of Review:', choices=[('SELLER', 'Seller'), ('PRODUCT', 'Product')], validators=[DataRequired()])
    identifier = StringField(u'Enter the email of the seller or the product to be reviewed:')
    comments = TextAreaField('Comments:')
    num_stars = IntegerField('Number of Stars:', validators=[InputRequired(), NumberRange(min=1, max=5)])
    # uploads = MultipleFileField(u'Review Images:')
    time_reviewed = datetime.now().strftime('%a %b %d %Y %H:%M:%S')
    submit = SubmitField('Create Review', validators=[DataRequired()])

@bp.route('/create-review', methods=['GET', 'POST'])
def create_review():
    form = CreateReviewForm()
    if request.method == 'POST' and form.validate():
        valid = True
        if Product_Reviews.verify_review(form.reviewType.data, form.identifier.data):
            if form.reviewType.data == 'SELLER':
                flash('This seller does not exist!') 
                return redirect(url_for('reviews.create_review'))
            if form.reviewType.data == 'PRODUCT':
                flash('This product does not exist!')
                return redirect(url_for('reviews.create_review'))
            valid = False
        # files = request.files.getlist("uploads") 
        # for file in files:
        #     if file.filename == '':
        #         flash('No selected file')
        #         valid = False
        #     else:
        #         if not allowed_file(file.filename):
        #             flash('Invalid file type(s)')
        #             valid = False
        if Product_Reviews.check_identifier(current_user.id, form.reviewType.data, form.identifier.data):
            if form.reviewType.data == 'SELLER':
                flash('You already reviewed this seller!') 
                return redirect(url_for('reviews.create_review'))
            if form.reviewType.data == 'PRODUCT':
                flash('You already reviewed this product!')
                return redirect(url_for('reviews.create_review'))
            valid = False
        if not current_user.is_authenticated:
            flash('You must be logged in to create a new review!')
            valid = False
        if valid:
            user_id = current_user.id
            Product_Reviews.create_review(form.reviewType.data, user_id, form.time_reviewed, form.identifier.data, form.comments.data, form.num_stars.data)
            # index = 0
            # for file in files: 
            #     if file and allowed_file(file.filename):
            #         filename = secure_filename(file.filename)
            #         basedir = os.path.abspath(os.path.dirname(__file__))
            #         hash_value = uuid.uuid4().hex + "." + filename.rsplit('.', 1)[1].lower() 
            #         # create hash value to make sure image upload does not have same value as an image currently already stored
            #         # add . + file format at the end to help with HTML later on
            #         file_url = os.path.join(basedir, app.config['UPLOAD_FOLDER'], hash_value)
            #         # max file size currently at 64MB, but not throwing error if > 5 GB
            #         file.save(file_url, buffer_size = 64 * 1024 * 1024)
            #         if form.reviewType.data == "SELLER":
            #             Product_Reviews.add_product_review_file(review_id, hash_value, index, "IMG")
            #         if form.reviewType.data == "PRODUCT":
            #             Product_Reviews.add_product_review_file(review_id, hash_value, index, "IMG")
            #         index += 1
            flash('Successfully created a new review!')
            return redirect(url_for('reviews.create_review'))
    if current_user.is_authenticated:
        return render_template('create_review.html', title='Create Review Page', form = form)
    else:
        flash('You must be logged in to create a new review!')
        return redirect(url_for('users.login'))

@bp.route('/create-product-review', methods=['GET', 'POST'])
def create_product_review():
    if request.method == 'POST':
        time_reviewed = datetime.now()
        comments = request.form.get('comments')
        num_stars = request.form.get('num_stars')
        product_id = request.form.get('product_id')
        user_id = current_user.id
        if Product_Reviews.prod_review_duplicates(user_id, product_id):
            flash('You already reviewed this product!')
            return redirect(url_for('products.product_page', id=product_id))
        if not current_user.is_authenticated:
            flash('You must be logged in to create a new review!')
            return redirect(url_for('users.login'))
        Product_Reviews.create_product_review(user_id, time_reviewed, comments, num_stars, product_id)
        flash('Successfully created a new review!')
        return redirect(url_for('products.product_page', id=product_id))

@bp.route('/create-seller-review', methods=['GET', 'POST'])
def create_seller_review():
    if request.method == 'POST':
        time_reviewed = datetime.now()
        comments = request.form.get('comments')
        num_stars = request.form.get('num_stars')
        seller_id = request.form.get('seller_id')
        user_id = current_user.id
        if Product_Reviews.checkUserBuySeller(current_user.id, seller_id):
            if Product_Reviews.seller_review_duplicates(user_id, seller_id):
                flash('You already reviewed this seller!')
                return redirect(url_for('myprofile.public_profile', id=seller_id))
            if not current_user.is_authenticated:
                flash('You must be logged in to create a new review!')
                return redirect(url_for('users.login'))
            Product_Reviews.create_seller_review(user_id, time_reviewed, comments, num_stars, seller_id)
            flash('Successfully created a new review!')
            return redirect(url_for('myprofile.public_profile', id=seller_id))
        else:
            flash('You have not bought from this seller')
            return redirect(url_for('myprofile.public_profile', id = seller_id))

@bp.route('/my_reviews', methods=['GET', 'POST'])
def my_reviews():
    form = AllForm()
    if current_user.is_authenticated:
        page = request.args.get(get_page_parameter(), type=int, default=1)
        filter = "RECENT"

        if request.method == 'POST' and form.validate():
            filter = form.filterType.data
        reviews = Product_Reviews.get_my_reviews(current_user.id, filter, 40, 40, page)

        if len(reviews) == 0:
                flash('You do not have any reviews!')
                return redirect(url_for('myprofile.profilepage'))

        total_reviews = int(Product_Reviews.num_reviews(current_user.id))
        per_page = 40
        pagination = Pagination(page=page, total=total_reviews, per_page=per_page)

        return render_template('my_reviews.html', user_reviews=reviews, form=form, pagination=pagination, humanize_time=humanize_time)
    else:
        flash('You must be logged in to view your reviews!')
        return redirect(url_for('users.login'))


@bp.route('/edit_review/<review_type>/<review_id>', methods=['GET', 'POST'])
def edit_review(review_type, review_id):
    if request.method == "POST":
        time_reviewed = datetime.now().strftime('%a %b %d %Y %H:%M:%S')
        comments = request.form.get('comments')
        num_stars = request.form.get('num_stars')
        if int(num_stars) < 1 or int(num_stars) > 5:
            flash('Please enter a number 1 through 5 for the number of stars')
            return redirect(url_for('reviews.edit_review', review_id=review_id, review_type=review_type))
        Product_Reviews.finalize_update(review_id, comments, num_stars, time_reviewed, review_type)
        flash('Your review was successfully updated!')
        return redirect(url_for('reviews.my_reviews'))
    return render_template('edit_review.html', review_id = review_id)


@bp.route('/delete_review/<review_type>/<review_id>', methods=['GET', 'POST'])
def delete_review(review_type, review_id):
    Product_Reviews.delete_op(review_id, review_type)
    return redirect(url_for('reviews.my_reviews'))