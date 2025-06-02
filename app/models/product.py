from flask import current_app as app
from html_sanitizer import Sanitizer

from .reviews import Product_Reviews


class Product:
    def __init__(self, id, name, price, description, available, images, stars, categories):
        self.id = id
        self.name = name
        self.price = price
        self.description = description
        self.available = available
        self.images = images
        self.stars = stars
        self.categories = categories

    @staticmethod
    # returns true if name already exists, false otherwise
    def check_name(name):
        rows = app.db.execute("SELECT * FROM Products WHERE name = :name", name = name)
        return len(rows) >= 1

    @staticmethod 
    def create_product(name, description, price, available=True):
        sanitizer = Sanitizer()
        rows = app.db.execute(
            '''
            INSERT INTO Products (name, price, description, available) 
            VALUES (:name, :price, :description, :available)
            RETURNING id
            ''', # note RETURNING selects and returns the id of the product we just created
            name=name, price= float(price), description=sanitizer.sanitize(description), available=available
        )
        return rows[0][0] # returns the id of the inserted product from call to create_product
    
    @staticmethod
    def edit_product(product_id, name, description, price):
        sanitizer = Sanitizer()
        app.db.execute(
            '''
            UPDATE Products
            SET name = :name, price = :price, description = :description
            WHERE id = :product_id
            ''',
            name=name, price=float(price), description=sanitizer.sanitize(description),
            product_id=product_id
        )

    
    @staticmethod
    def set_owner(pid, uid):
        app.db.execute(
            '''
            INSERT INTO ProductOwner VALUES
            (:pid, :uid)
            ''', pid = int(pid), uid = int(uid)
        )
        return
    
    @staticmethod
    def check_owner(pid, uid):
        rows = app.db.execute(
            '''
            SELECT * 
            FROM ProductOwner
            WHERE ProductOwner.pid = :pid AND
            ProductOwner.uid = :uid
            ''',
            pid = pid, uid = uid
        )
        return len(rows) >= 1


    @staticmethod
    def add_product_file(pid, url, type): # add an upload file to the ProductFiles table
        index = app.db.execute('''
            SELECT COALESCE(MAX(index), 0) AS max_index
            FROM ProductFiles
            WHERE pid = :pid
            ''', pid = pid
        )
        app.db.execute(
            '''
            INSERT INTO ProductFiles (pid, url, index, type)
            VALUES (:pid, :url, :index, :type)
            ''',
            pid=pid, url=url, index = index[0][0] + 1, type=type
        )
        return 
    
    @staticmethod
    def get_product_image_urls(pid):
        rows = app.db.execute(
            '''
            SELECT url
            FROM ProductFiles
            WHERE pid = :pid and type = 'IMG'
            ORDER BY index
            ''', pid=pid
        )
        return [row[0] for row in rows]

    @staticmethod
    def get(id):
        rows = app.db.execute('''
SELECT id, name, price, description, available
FROM Products
WHERE id = :id
''',
                              id=id)
        if len(rows) == 0:
            return None
        return Product(*(rows[0]), Product.get_product_image_urls(id), Product_Reviews.get_average_product_review(id),  Product.get_categories(id))

    @staticmethod
    def num_products(categories, search_query, available = True, uid = None):
        search_query = '%' + search_query + '%' # change format of search string to %search_term% before using with SQL LIKE
        if uid == None:
            if len(categories) < 1:
                rows = app.db.execute('''
                SELECT COUNT(*) FROM
                    (SELECT DISTINCT Products.id, Products.name, Products.price, Products.description, Products.available
                    FROM Products
                    WHERE available = :available AND LOWER(Products.name) LIKE LOWER(:search_query)) AS A''',
                available=available, search_query = search_query)
            else:
                rows = app.db.execute('''
                SELECT COUNT(*) FROM
                    (SELECT DISTINCT Products.id, Products.name, Products.price, Products.description, Products.available
                    FROM Products, ProductCategoriesLink, ProductCategories
                    WHERE available = :available AND 
                        Products.id = ProductCategoriesLink.pid AND
                        ProductCategories.cid = ProductCategoriesLink.cid AND
                        ProductCategories.cid IN :categories AND
                        LOWER(Products.name) LIKE LOWER(:search_query)) AS A''',
                available=available, categories = tuple(categories), search_query = search_query)
        else:
            if len(categories) < 1:
                rows = app.db.execute('''
                SELECT COUNT(*) FROM
                    (SELECT DISTINCT Products.id, Products.name, Products.price, Products.description, Products.available
                    FROM Products, ProductOwner
                    WHERE available = :available AND 
                    LOWER(Products.name) LIKE LOWER(:search_query)
                    AND Products.id = ProductOwner.pid 
                    AND ProductOwner.uid = :uid
                    ) AS A''',
                available=available, search_query = search_query, uid = uid)
            else:
                rows = app.db.execute('''
                SELECT COUNT(*) FROM
                    (SELECT DISTINCT Products.id, Products.name, Products.price, Products.description, Products.available
                    FROM Products, ProductCategoriesLink, ProductCategories, ProductOwner
                    WHERE available = :available AND 
                        Products.id = ProductCategoriesLink.pid AND
                        ProductCategories.cid = ProductCategoriesLink.cid AND
                        ProductCategories.cid IN :categories AND
                        LOWER(Products.name) LIKE LOWER(:search_query)
                        AND Products.id = ProductOwner.pid 
                        AND ProductOwner.uid = :uid) AS A''',
                available=available, categories = tuple(categories), search_query = search_query, uid = uid)
        return rows[0][0]

    @staticmethod
    def order_products(available=True, order="", categories = [], search_query = "", k = 20, page = 1, uid = None):

        if (order == "DESC"): 
            order = "ORDER BY price DESC"
        elif (order == "ASC"): 
            order = "ORDER BY price ASC"
        else:
            order = ""
        
        search_query = '%' + search_query + '%' # change format of search string to %search_term% before using with SQL LIKE

        offset = k*(page-1)
        if uid == None:
            if len(categories) < 1:
                rows = app.db.execute('''
                SELECT DISTINCT Products.id, Products.name, Products.price, Products.description, Products.available
                FROM Products
                WHERE available = :available AND LOWER(Products.name) LIKE LOWER(:search_query)
                {}
                LIMIT :k OFFSET :offset'''.format(order), available=available, search_query = search_query, k=k, offset=offset)
            else:
                rows = app.db.execute('''
                SELECT DISTINCT Products.id, Products.name, Products.price, Products.description, Products.available
                FROM Products, ProductCategoriesLink, ProductCategories
                WHERE available = :available AND 
                    Products.id = ProductCategoriesLink.pid AND
                    ProductCategories.cid = ProductCategoriesLink.cid AND
                    ProductCategories.cid IN :categories AND
                    LOWER(Products.name) LIKE LOWER(:search_query)
                                    
                {}
                LIMIT :k OFFSET :offset'''.format(order), available=available, categories = tuple(categories), search_query = search_query, k=k, offset=offset)
            return rows
        else:
            if len(categories) < 1:
                rows = app.db.execute('''
                SELECT DISTINCT Products.id, Products.name, Products.price, Products.description, Products.available
                FROM Products, ProductOwner
                WHERE available = :available AND 
                LOWER(Products.name) LIKE LOWER(:search_query) 
                AND Products.id = ProductOwner.pid 
                AND ProductOwner.uid = :uid
                {}
                LIMIT :k OFFSET :offset'''.format(order), available=available, search_query = search_query, k=k, offset=offset, uid = uid)
            else:
                rows = app.db.execute('''
                SELECT DISTINCT Products.id, Products.name, Products.price, Products.description, Products.available
                FROM Products, ProductCategoriesLink, ProductCategories, ProductOwner
                WHERE available = :available AND 
                    Products.id = ProductCategoriesLink.pid AND
                    ProductCategories.cid = ProductCategoriesLink.cid AND
                    ProductCategories.cid IN :categories AND
                    LOWER(Products.name) LIKE LOWER(:search_query) AND
                    Products.id = ProductOwner.pid AND
                    ProductOwner.uid = :uid
                                    
                {}
                LIMIT :k OFFSET :offset'''.format(order), available=available, categories = tuple(categories), search_query = search_query, k=k, offset=offset, uid = uid)
            return rows

    @staticmethod
    def get_k_products(available=True, order="DESC", categories = [], search_query = "", k = 20, page = 1, uid = None): # default display 10
        # k >= 1
        rows = Product.order_products(available, order, categories, search_query, k, page, uid)
        if (len(rows) < 1):
            return None
        return [Product(*rows[i], Product.get_product_image_urls(rows[i][0]), Product_Reviews.get_average_product_review(rows[i][0]), Product.get_categories(rows[i][0])) for i in range(len(rows))]
    
    @staticmethod
    def get_products(avaiable=True, order="NONE", categories = [], search_query = "", k = 20, page = 1, uid = None):
        if order is None: order = "NONE"
        if k is None: k = 20
        return Product.get_k_products(avaiable, order, categories, search_query, k, page, uid)  

    @staticmethod
    # get all categories
    def get_all_categories():
        rows = app.db.execute('''
            SELECT cid, name
            FROM ProductCategories
            ''')
        return [rows[i] for i in range(len(rows))]

    @staticmethod
    # get categories for product pid
    def get_categories(pid):
        rows = app.db.execute(
            '''
            SELECT name
            FROM ProductCategories, ProductCategoriesLink
            WHERE ProductCategoriesLink.pid = :pid AND ProductCategories.cid = ProductCategoriesLink.cid
            ''', pid = pid)
        return [rows[i][0] for i in range(len(rows))]


    @staticmethod
    def add_category_link(pid, cid):
        app.db.execute(
            '''
            INSERT INTO ProductCategoriesLink (pid, cid) 
            VALUES (:pid, :cid)
            ''',
            pid = pid, cid = cid
        )
        return
    
    @staticmethod
    def delete_category_links(pid):
        app.db.execute(
            '''
            DELETE FROM ProductCategoriesLink 
            WHERE pid = :pid
            ''',
            pid=pid
        )
        return
    
    @staticmethod
    def delete_product_file(pid, url):
        print(pid)
        app.db.execute(
            '''
            DELETE FROM ProductFiles
            WHERE pid = :pid AND url = :url
            ''',
            pid=int(pid), url=url
        )
        return
    
    