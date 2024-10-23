from flask import current_app as app


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
    def get_summary_rating(identifier, requested_type):
        if requested_type == "SELLER":
            rows = app.db.execute('''
            select foo.count, foo.average_rating
            from (select Users.email, count(*), round(avg(num_stars), 2) as average_rating
            from Seller_Reviews, Users
            where Seller_Reviews.seller_id = Users.id
            group by Users.email) as foo
            where foo.email = :email;
            ''', email = identifier)
            return rows if rows is not None else None
        if requested_type == "PRODUCT":
            rows = app.db.execute('''
            select foo.count, foo.average_rating
            from (select Products.name, count(*), round(avg(num_stars), 2) as average_rating
            from Product_Reviews, Products
            where Products.id = Product_Reviews.product_id 
            group by Products.name) as foo
            where foo.name = :product_name;
            ''', product_name = identifier)
            return rows if rows is not None else None