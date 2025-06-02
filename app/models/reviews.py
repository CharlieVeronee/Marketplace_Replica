from flask import current_app as app
from bleach import clean
import re


class Seller_Reviews:
    def __init__(self, id, user_id, time_reviewed, comments, num_stars, seller_id):
        self.id = id
        self.user_id = user_id
        self.time_reviewed = time_reviewed
        self.comments = comments
        self.num_stars = num_stars
        self.seller_id = seller_id

class Product_Reviews:
    def __init__(self, id, user_id, time_reviewed, comments, num_stars, product_id):
        self.id = id
        self.user_id = user_id
        self.time_reviewed = time_reviewed
        self.comments = comments
        self.num_stars = num_stars
        self.product_id = product_id
    
    @staticmethod
    def check_identifier(user_id, reviewType, identifier):
        if reviewType == 'SELLER':
            rows = app.db.execute('''
            select *
            from 
            (select Seller_Reviews.user_id, Users.email
            from Seller_Reviews, Users
            where Seller_Reviews.seller_id = Users.id) as foo
            where foo.email = :identifier''', 
            user_id = user_id, identifier = identifier)
            return len(rows) >= 1
        if reviewType == 'PRODUCT':
            rows = app.db.execute('''
            select *
            from
            (select Product_Reviews.user_id, Products.name
            from Product_Reviews, Products
            where Product_Reviews.product_id = Products.id) as foo
            where foo.name = :identifier
            ''', 
            user_id = user_id, identifier = identifier)
            return len(rows) >= 1

    @staticmethod
    def prod_review_duplicates(user_id, product_id):
        rows = app.db.execute('''
        select *
        from product_reviews
        where product_reviews.product_id = :product_id
        and product_reviews.user_id = :user_id
        ''', user_id = user_id, product_id = product_id)
        return len(rows) >= 1

    @staticmethod
    def create_product_review(user_id, time_reviewed, comments, num_stars, product_id):
        rows = app.db.execute(
        '''
        INSERT INTO Product_Reviews (user_id, time_reviewed, comments, num_stars, product_id) 
        VALUES (:user_id, :time_reviewed, :comments, :num_stars, :product_id)
        ''',
        user_id = user_id, time_reviewed = time_reviewed, 
        comments = comments, num_stars = num_stars, product_id = product_id)

    @staticmethod
    def seller_review_duplicates(user_id, seller_id):
        rows = app.db.execute('''
        select *
        from seller_reviews
        where seller_reviews.user_id = :user_id
        and seller_reviews.seller_id = :seller_id
        ''', user_id = user_id, seller_id = seller_id)
        return len(rows) >= 1

    @staticmethod
    def create_seller_review(user_id, time_reviewed, comments, num_stars, seller_id):
        rows = app.db.execute(
        '''
        INSERT INTO seller_reviews (user_id, time_reviewed, comments, num_stars, seller_id) 
        VALUES (:user_id, :time_reviewed, :comments, :num_stars, :seller_id)
        ''',
        user_id = user_id, time_reviewed = time_reviewed, 
        comments = comments, num_stars = num_stars, seller_id = seller_id)

    @staticmethod 
    def create_review(reviewType, user_id, time_reviewed, identifier, comments, num_stars):
        comments = clean(comments, tags=[], strip=True)
        comments = re.sub(r'\s+', ' ', comments)
        comments = comments.replace('&nbsp;', ' ')
        if reviewType == "SELLER":
            seller_id = app.db.execute('''
                select id
                from Users
                where Users.email = :email;
                ''', email = identifier)
            rows = app.db.execute(
                '''
                INSERT INTO Seller_Reviews (user_id, time_reviewed, comments, num_stars, seller_id) 
                VALUES (:user_id, :time_reviewed, :comments, :num_stars, :seller_id)
                RETURNING id
                ''',
                user_id = user_id, time_reviewed = time_reviewed, identifier = identifier, 
                comments = comments, num_stars = num_stars, seller_id = seller_id[0][0])
        if reviewType == "PRODUCT":
            product_id = app.db.execute('''
                select id
                from Products
                where Products.name = :name;
                ''', name = identifier)
            rows = app.db.execute(
                '''
                INSERT INTO Product_Reviews (user_id, time_reviewed, comments, num_stars, product_id) 
                VALUES (:user_id, :time_reviewed, :comments, :num_stars, :product_id)
                RETURNING id
                ''',
                user_id = user_id, time_reviewed = time_reviewed, identifier = identifier, 
                comments = comments, num_stars = num_stars, product_id = product_id[0][0])
    
    @staticmethod
    def num_reviews(user_id):
        rows = app.db.execute('''
        select sum(total) as final_total
        from ((select count(*) as total
        from seller_reviews
        where seller_reviews.user_id = :user_id)
        union
        (select count(*) as total
        from product_reviews
        where product_reviews.user_id = :user_id)) 
        as foo;
        ''', user_id=user_id)
        print(rows[0][0])
        return rows[0][0]

    @staticmethod
    def get_reviews(user_id, filter, k):
        if filter == "RECENT":
            rows = app.db.execute('''
            (select email as id, time_reviewed, comments, num_stars
            from
            (select *
            from Seller_Reviews, Users
            where Seller_Reviews.seller_id = Users.id) as foo1
            where foo1.user_id = :user_id)
            union
            (select name as id, time_reviewed, comments, num_stars
            from 
            (select Product_Reviews.id, user_id, name, time_reviewed, comments, num_stars
            from Product_Reviews, Products
            where Product_Reviews.product_id = Products.id) as foo2
            where foo2.user_id = :user_id)
            order by time_reviewed desc
            limit :k;
            ''',
            user_id = user_id, k = k)
            return rows if rows is not None else None
        if filter == "OLDEST":
            rows = app.db.execute('''
            (select email as id, time_reviewed, comments, num_stars
            from
            (select *
            from Seller_Reviews, Users
            where Seller_Reviews.seller_id = Users.id) as foo1
            where foo1.user_id = :user_id)
            union
            (select name as id, time_reviewed, comments, num_stars
            from 
            (select Product_Reviews.id, user_id, name, time_reviewed, comments, num_stars
            from Product_Reviews, Products
            where Product_Reviews.product_id = Products.id) as foo2
            where foo2.user_id = :user_id)
            order by time_reviewed asc
            limit :k;
            ''',
            user_id = user_id, k = k)
            return rows if rows is not None else None
        if filter == "HIGHEST":
            rows = app.db.execute('''
            (select email as id, time_reviewed, comments, num_stars
            from
            (select *
            from Seller_Reviews, Users
            where Seller_Reviews.seller_id = Users.id) as foo1
            where foo1.user_id = :user_id)
            union
            (select name as id, time_reviewed, comments, num_stars
            from 
            (select Product_Reviews.id, user_id, name, time_reviewed, comments, num_stars
            from Product_Reviews, Products
            where Product_Reviews.product_id = Products.id) as foo2
            where foo2.user_id = :user_id)
            order by num_stars desc
            limit :k;
            ''',
            user_id = user_id, k = k)
            return rows if rows is not None else None
    
    @staticmethod
    def get_my_reviews(user_id, filter, amount, k=40, page=1):
        if page == None:
            page = 1
        if k == None:
            k = 40
        
        offset = k * (page - 1)

        query_template = '''
            SELECT 'Seller' AS review_type, Seller_Reviews.id AS review_id, CONCAT(firstname, ' ', lastname) AS name, time_reviewed, comments, num_stars
            FROM Seller_Reviews
            JOIN Users ON Seller_Reviews.seller_id = Users.id
            WHERE Seller_Reviews.user_id = :user_id

            UNION

            SELECT 'Product' AS review_type, Product_Reviews.id AS review_id, name, time_reviewed, comments, num_stars
            FROM Product_Reviews
            JOIN Products ON Product_Reviews.product_id = Products.id
            WHERE Product_Reviews.user_id = :user_id
            ORDER BY {order_by} LIMIT :amount OFFSET :offset;
        '''


        order_by = 'time_reviewed DESC' if filter == 'RECENT' else 'time_reviewed ASC' if filter == 'OLDEST' else 'num_stars DESC' if filter == 'HIGHEST' else None

        if order_by is None:
            return None

        rows = app.db.execute(query_template.format(order_by=order_by), user_id=user_id, k=k, offset=offset, amount=amount)
        return rows if rows is not None else None
    
    @staticmethod
    def delete_op(review_id, review_type):
        if review_type == "Seller":
            app.db.execute('''
            delete
            from Seller_Reviews
            where Seller_Reviews.id = :review_id
            ''', review_id = review_id)
        else:
            app.db.execute('''
            delete
            from Product_Reviews
            where Product_Reviews.id = :review_id
            ''', review_id = review_id)

    @staticmethod
    def finalize_update(review_id, new_comments, new_num_stars, new_time_reviewed, review_type):
        comments = clean(new_comments, tags=[], strip=True)
        comments = re.sub(r'\s+', ' ', comments)
        new_comments = comments.replace('&nbsp;', ' ')
        if review_type == "Seller":
            app.db.execute('''
            update seller_reviews
            set comments = :new_comments,
                num_stars = :new_num_stars,
                time_reviewed = :new_time_reviewed
            where Seller_Reviews.id = :review_id
            ''', review_id = review_id, new_comments = new_comments, 
            new_num_stars = new_num_stars, new_time_reviewed = new_time_reviewed)
        else:
            app.db.execute('''
            update product_reviews
            set comments = :new_comments,
                num_stars = :new_num_stars,
                time_reviewed = :new_time_reviewed
            where Product_Reviews.id= :review_id
            ''', review_id = review_id, new_comments = new_comments, 
            new_num_stars = new_num_stars, new_time_reviewed = new_time_reviewed)

    @staticmethod
    def get_average_product_review(id):
        rows = app.db.execute('''
        SELECT AVG(num_stars)
        FROM Product_Reviews
        WHERE product_id = :id
        ''', id=id)
        if rows[0][0] == None:
            return 0
        return rows[0][0]

    @staticmethod
    def get_average_seller_review(id):
        rows = app.db.execute('''
        SELECT AVG(num_stars)
        FROM Seller_Reviews
        WHERE seller_id = :id
        ''', id=id)
        if rows[0][0] == None:
            return 0
        return rows[0][0]
    
    @staticmethod
    def get_product_reviews(id):
        rows = app.db.execute('''
        SELECT *
        FROM Product_Reviews
        WHERE product_id = :id
        ORDER BY num_stars DESC, time_reviewed DESC
        ''', id = id)
        return [Product_Reviews(*row) for row in rows]
    
    @staticmethod
    def num_product_reviews(id):
        rows = app.db.execute('''
        SELECT COUNT(*)
        FROM Product_Reviews
        WHERE product_id = :id
        ''', id = id)
        return rows[0][0]

    @staticmethod
    def get_seller_reviews(id):
        rows = app.db.execute('''
        SELECT *
        FROM Seller_Reviews
        WHERE seller_id = :id
        ORDER BY num_stars DESC, time_reviewed DESC
        ''', id = id)
        return [Seller_Reviews(*row) for row in rows]

    @staticmethod
    def num_seller_reviews(id):
        rows = app.db.execute('''
        SELECT COUNT(*)
        FROM Seller_Reviews
        WHERE seller_id = :id
        ''', id = id)
        return rows[0][0]
    
    @staticmethod
    def verify_review(reviewType, identifier):
        if reviewType == "SELLER":
            rows = app.db.execute('''
            select * 
            from users
            where users.email = :email;
            ''', email = identifier)
            return len(rows) == 0
        if reviewType == "PRODUCT":
            rows = app.db.execute('''
            select * 
            from products
            where products.name = :name
            ''', name = identifier)
            return len(rows) == 0

    @staticmethod
    def validate_id(uid):
        rows = app.db.execute('''
        select *
        from users
        where users.id = :uid
        ''', uid = uid)
        return len(rows) == 0

    @staticmethod
    def get_reviews_of_me(user_id, type, amount):
        if filter == "RECENT":
            rows = app.db.execute('''
            select *
            from seller_reviews
            where seller_reviews.seller_id = :user_id
            order by time_reviewed desc
            limit :amount;
            ''',
            user_id = user_id, type = type, amount = amount)
            return rows if rows is not None else None
        if filter == "OLDEST":
            rows = app.db.execute('''
            select *
            from seller_reviews
            where seller_reviews.seller_id = :user_id
            order by time_reviewed asc
            limit :amount;
            ''',
            user_id = user_id, type = type, amount = amount)
            return rows if rows is not None else None
        if filter == "HIGHEST":
            rows = app.db.execute('''
            select *
            from seller_reviews
            where seller_reviews.seller_id = :user_id
            order by num_stars desc
            limit :amount;
            ''',
            user_id = user_id, type = type, amount = amount)
            return rows if rows is not None else None
        
    @staticmethod
    def checkUserBuySeller(uid, sid):
        rows = app.db.execute('''
        SELECT EXISTS (
            SELECT 1
            FROM Cart
            WHERE user_id = :uid 
            AND seller_id = :sid
            AND order_id IS NOT NULL
        ) AS result;
        ''', uid = uid, sid=sid)
        return rows[0][0]