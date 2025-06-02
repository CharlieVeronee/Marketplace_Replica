import os
import uuid
from flask import current_app as app
from flask import Flask, render_template, flash, redirect, url_for, request
from flask_wtf import FlaskForm
from wtforms import SubmitField, SelectField, StringField, MultipleFileField, DecimalField, IntegerField
from wtforms.validators import DataRequired, Length, NumberRange
from werkzeug.utils import secure_filename
from flask_ckeditor import CKEditorField, CKEditor
from flask_paginate import Pagination, get_page_parameter
from flask_login import current_user
from humanize import naturaltime
import datetime

from .models.product import Product
from .models.inventory import Inventory
from .models.reviews import Product_Reviews

from flask import Blueprint

bp = Blueprint('products', __name__)

def humanize_time(dt):
    return naturaltime(datetime.datetime.now() - dt)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

class FilterForm(FlaskForm):
    filterType = SelectField(u'Filter by price:', id='filterType', choices=[('NONE', 'None'), ('DESC', 'Price - High to Low'), ('ASC', 'Price - Low to High')])

class CreateProductForm(FlaskForm):
    name = StringField(u'Product Name:', validators=[DataRequired(), Length(min = 3, max = 500)])
    description = CKEditorField('Description:')
    uploads = MultipleFileField(u'Featured Product Files (Images):')
    price = DecimalField(u'Price:', validators=[DataRequired(), NumberRange(min = 0, max = 1000000)])
    quantity = IntegerField(u'Quantity for Sale:', validators=[DataRequired(), NumberRange(min=1, max=1000000)])
    submit = SubmitField('Create Product', validators=[DataRequired()])

    

@bp.route('/products', methods=['GET', 'POST'])
def products():
    form = FilterForm()
    categories = []

    if request.method == 'POST':
        categories = request.form.getlist("category")
    
    search_query = request.args.get("search")
    if search_query is None:
        search_query = ""

    page = request.args.get(get_page_parameter(), type=int, default=1)
    products = Product.get_products(True, form.filterType.data, categories, search_query, 40, page, None)
    
    pagination = Pagination(page=page, total=Product.num_products(categories, search_query, True, None), record_name='products', per_page=40)


    # render the page by adding information to the product.html file
    return render_template('product.html', title='Product Display Page', form=form, products=products, pagination=pagination, categories = Product.get_all_categories())

@bp.route('/create-products', methods=['GET', 'POST'])
def create_product():
    form = CreateProductForm()

    if request.method == 'POST' and form.validate():
        valid = True
        if Product.check_name(form.name.data):
            flash('Product name already exists, choose a different name!')
            valid = False
        files = request.files.getlist("uploads") 

        if not current_user.is_authenticated:
            flash('You must be logged in to create a product!')
            valid = False
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        for file in files:
            if file.filename == '':
                flash('No selected file')
                valid = False
            else:
                if not allowed_file(file.filename):
                    flash('Invalid file type(s)')
                    valid = False
        
        if valid: # if use includes valid file type
            # we know at least one valid file is uploaded so we can create product
            product_id = Product.create_product(form.name.data, form.description.data, form.price.data, True)
            Product.set_owner(product_id, current_user.id)
            Inventory.set_inv(current_user.id, product_id, form.quantity.data)
            categories = request.form.getlist("categories")
            for category in categories:
                Product.add_category_link(product_id, category)
            
            
            for file in files: 
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    basedir = os.path.abspath(os.path.dirname(__file__))
                    hash_value = uuid.uuid4().hex + "." + filename.rsplit('.', 1)[1].lower() 
                    # create hash value to make sure image upload does not have same value as an image currently already stored
                    # add . + file format at the end to help with HTML later on
                    file_url = os.path.join(basedir, app.config['UPLOAD_FOLDER'], hash_value)
                    # max file size currently at 64MB, but not throwing error if > 5 GB
                    file.save(file_url, buffer_size = 64 * 1024 * 1024)
                    Product.add_product_file(product_id, hash_value, "IMG")
            flash('Successfully created a new product!')
            return redirect(url_for('products.create_product'))
    if current_user.is_authenticated:
        return render_template('create_product.html', title='Create Product Page', form = form, categories = Product.get_all_categories())
    else:
        flash('You must be logged in to create a new product listing!')
        return redirect(url_for('users.login'))

@bp.route('/product/<id>', methods=['GET', 'POST'])
def product_page(id):
    return render_template('product_page.html', title='Product Page', product=Product.get(id), reviews = Product_Reviews.get_product_reviews(id), num_reviews = Product_Reviews.num_product_reviews(id), sellers = Inventory.get_sellers(id), humanize_time = humanize_time)

@bp.route('/my_products/', methods=['GET', 'POST'])
def get_my_products():
    if not current_user.is_authenticated:
        flash('You must be logged in to view your products!')
        return redirect(url_for('users.login'))
    form = FilterForm()
    categories = []

    if request.method == 'POST':
        categories = request.form.getlist("category")
    
    search_query = request.args.get("search")
    if search_query is None:
        search_query = ""

    page = request.args.get(get_page_parameter(), type=int, default=1)
    products = Product.get_products(True, form.filterType.data, categories, search_query, 40, page, current_user.id)
    
    pagination = Pagination(page=page, total=Product.num_products(categories, search_query, True, current_user.id), record_name='products', per_page=40)

    return render_template('my_products.html', title='Product Display Page', form=form, products=products, pagination=pagination, categories = Product.get_all_categories())

@bp.route('/edit_product/<id>', methods=['GET', 'POST'])
def edit_product(id):
    if not current_user.is_authenticated:
        flash('You must be logged in to edit a product!')
        return redirect(url_for('users.login'))
    if not Product.check_owner(id, current_user.id):
        return redirect(url_for('products.get_my_products'))
    
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('hiddenDescription')
        price = request.form.get('price')
        categories = request.form.getlist("categories")
        Product.delete_category_links(id)
        for category in categories:
            Product.add_category_link(id, category)
        if Product.check_name(name) and Product.get(id).name != name:
            flash('Product name already exists, choose a different name!')
            return render_template('edit_product.html', title = 'Product Edit Page', product = Product.get(id), categories = Product.get_all_categories())
            # return redirect(url_for('products.edit_product', id=id))
            
        else:
            Product.edit_product(id, name, description, price)
            flash('Product edited succesfully!')
            return redirect(url_for('products.get_my_products'))

    
    return render_template('edit_product.html', title = 'Product Edit Page', product = Product.get(id), categories = Product.get_all_categories())

@bp.route('/add_images/<id>', methods=['POST'])
def add_images(id):
    if not current_user.is_authenticated or not Product.check_owner(id, current_user.id):
        flash('You do not have permission to add images to this product!')
        return redirect(url_for('products.get_my_products'))

    if 'uploads' not in request.files:
        flash('No file part')
        return redirect(url_for('products.edit_product', id=id))

    files = request.files.getlist('uploads')

    for file in files:
            if file.filename == '':
                flash('No selected file')
                return redirect(url_for('products.edit_product', id=id))
            else:
                if not allowed_file(file.filename):
                    flash('Invalid file type(s)')
                    return redirect(url_for('products.edit_product', id=id))


    for file in files: 
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    basedir = os.path.abspath(os.path.dirname(__file__))
                    hash_value = uuid.uuid4().hex + "." + filename.rsplit('.', 1)[1].lower() 
                    # create hash value to make sure image upload does not have same value as an image currently already stored
                    # add . + file format at the end to help with HTML later on
                    file_url = os.path.join(basedir, app.config['UPLOAD_FOLDER'], hash_value)
                    # max file size currently at 64MB, but not throwing error if > 5 GB
                    file.save(file_url, buffer_size = 64 * 1024 * 1024)
                    Product.add_product_file(id, hash_value, "IMG")

    flash('Images added successfully.')
    return redirect(url_for('products.edit_product', id=id))

@bp.route('/delete_image/<pid>/<url>', methods=['POST'])
def delete_image(pid, url):
    print(pid)
    Product.delete_product_file(pid, url)
    return redirect(url_for('products.edit_product', id=pid))
