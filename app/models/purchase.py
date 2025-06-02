from flask import current_app as app


class Purchase:
    def __init__(self, id, uid, pid, time_purchased):
        self.id = id
        self.uid = uid
        self.pid = pid
        self.time_purchased = time_purchased

    @staticmethod
    def get(id):
        rows = app.db.execute('''
SELECT id, uid, pid, time_purchased
FROM Purchases
WHERE id = :id
''',
                              id=id)
        return Purchase(*(rows[0])) if rows else None

    @staticmethod
    def get_all_by_uid_since(uid, since):
        rows = app.db.execute('''
SELECT id, uid, pid, time_purchased
FROM Purchases
WHERE uid = :uid
AND time_purchased >= :since
ORDER BY time_purchased DESC
''',
                              uid=uid,
                              since=since)
        return [Purchase(*row) for row in rows]

        

#THIS STUFF BELOW ISN"T USED ANY MORE, IT MOVED TO CART.PY

        # given a user id, find the items purchased for that user
    @staticmethod
    def get_purchase(user_id, sort_by):
        if sort_by == "price_ascending":
            rows = app.db.execute('''
            SELECT Purchases.id AS id, Products.name AS name, Products.price AS price, Purchases.time_purchased AS time
            FROM Purchases, Products
            WHERE Purchases.pid = Products.id AND Purchases.uid = :user_id
            ORDER BY price ASC
            ''', user_id = user_id)

        
        elif sort_by == "price_descending":
            rows = app.db.execute('''
            SELECT Purchases.id AS id, Products.name AS name, Products.price AS price, Purchases.time_purchased AS time
            FROM Purchases, Products
            WHERE Purchases.pid = Products.id AND Purchases.uid = :user_id
            ORDER BY price DESC
            ''', user_id = user_id)

        elif sort_by == "time_newest":
            rows = app.db.execute('''
            SELECT Purchases.id AS id, Products.name AS name, Products.price AS price, Purchases.time_purchased AS time
            FROM Purchases, Products
            WHERE Purchases.pid = Products.id AND Purchases.uid = :user_id
            ORDER BY time DESC
            ''', user_id = user_id)

        
        elif sort_by == "time_oldest":
            rows = app.db.execute('''
            SELECT Purchases.id AS id, Products.name AS name, Products.price AS price, Purchases.time_purchased AS time
            FROM Purchases, Products
            WHERE Purchases.pid = Products.id AND Purchases.uid = :user_id
            ORDER BY time ASC
            ''', user_id = user_id)

        elif sort_by == "name_a":
            rows = app.db.execute('''
            SELECT Purchases.id AS id, Products.name AS name, Products.price AS price, Purchases.time_purchased AS time
            FROM Purchases, Products
            WHERE Purchases.pid = Products.id AND Purchases.uid = :user_id
            ORDER BY name ASC
            ''', user_id = user_id)

        elif sort_by == "name_z":
            rows = app.db.execute('''
            SELECT Purchases.id AS id, Products.name AS name, Products.price AS price, Purchases.time_purchased AS time
            FROM Purchases, Products
            WHERE Purchases.pid = Products.id AND Purchases.uid = :user_id
            ORDER BY name DESC
            ''', user_id = user_id)

        else:
            rows = app.db.execute('''
            SELECT Purchases.id AS id, Products.name AS name, Products.price AS price, Purchases.time_purchased AS time
            FROM Purchases, Products
            WHERE Purchases.pid = Products.id AND Purchases.uid = :user_id
            ORDER BY time DESC
            ''', user_id = user_id)

        return rows if rows is not None else None

