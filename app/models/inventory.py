from flask import current_app as app

class Inventory:
    def __init__(self, user_id, product_id, quantity):
        self.user_id = user_id
        self.product_id = product_id
        self.quantity = quantity

    @staticmethod
    def get_inv(user_id, k = 40, page = 1):
        if page == None:
            page = 1
        if k == None:
            k = 40
        offset = k*(page-1)
        rows = app.db.execute('''
SELECT name, product_id, price, quantity
FROM (SELECT * FROM Inventory WHERE user_id = :user_id) as foo
LEFT JOIN Products
ON products.id = foo.product_id
LIMIT :k OFFSET :offset
''',
                                user_id = user_id, k=k, offset = offset)
        return rows if rows is not None else None

    @staticmethod
    def set_inv(uid, pid, quantity):
        app.db.execute('''
                        INSERT INTO Inventory (user_id, product_id, quantity)
                        VALUES
                        (:uid, :pid, :quantity)
                       ''', uid=uid, pid=pid, quantity=quantity)
        
    @staticmethod
    def num_products(user_id):
        rows = app.db.execute('''
                        SELECT COUNT(*)
                        FROM (SELECT * FROM Inventory WHERE user_id = :user_id) as foo
                        LEFT JOIN Products
                        ON products.id = foo.product_id
                       ''', user_id=user_id)
        return rows[0][0]
        
    @staticmethod
    def del_inv(uid, pid):
        app.db.execute('''
                        DELETE FROM Inventory WHERE product_id = :pid
                        AND user_id = :uid
                       ''', pid=pid, uid=uid)
    
    @staticmethod
    def upd_prodav(pid):
        app.db.execute('''
                        UPDATE Products
                        SET available = FALSE
                        WHERE id = :pid
                       ''', pid=pid)
    @staticmethod
    def upd_prodavtr(pid):
        app.db.execute('''
                        UPDATE Products
                        SET available = TRUE
                        WHERE id = :pid
                       ''', pid=pid)    
    
    @staticmethod
    def upd_qty(pid, n_qty, uid):
        app.db.execute('''
                        UPDATE Inventory
                        SET quantity = :n_qty
                        WHERE product_id = :pid AND user_id = :uid
                       ''', pid=pid, n_qty=n_qty, uid=uid)

    @staticmethod    
    def get_quantity(seller_id, product_id):
        rows = app.db.execute('''
        SELECT COALESCE(quantity, 0) AS quantity
        FROM Inventory
        WHERE user_id = :seller_id
        AND product_id = :product_id
        ''',
        seller_id=seller_id, product_id=product_id)
        return rows[0][0] if rows else 0

    @staticmethod
    def inv_prod(uid, pid):
        rows = app.db.execute('''
                        SELECT *
                        FROM Inventory
                        WHERE product_id = :pid
                        AND user_id = :uid
                       ''', pid=pid, uid=uid)
        return len(rows) >= 1
    
    @staticmethod
    def inv_prod_check(pid):
        rows = app.db.execute('''
                        SELECT COALESCE(SUM(quantity), 0)
                        FROM Inventory
                        WHERE product_id = :pid
                       ''', pid=pid)
        return rows[0][0]
    
    @staticmethod
    def get_sellers(pid):
        rows = app.db.execute('''
        SELECT *
        FROM Inventory, Users
        WHERE product_id = :pid
        AND Inventory.user_id = Users.id
        AND Inventory.quantity != 0
        ''', pid = pid)
        return [row for row in rows]

    @staticmethod
    def get_orders(seller_id, k = 40, page = 1):
        if page == None:
            page = 1
        if k == None:
            k = 40
        offset = k*(page-1)
        rows = app.db.execute('''
                              SELECT DISTINCT order_id, time_ordered, Cart.fulfilled
                              FROM Cart, Orders, Users, Inventory
                              WHERE Orders.id = Cart.order_id AND Cart.user_id = Users.id AND cart.seller_id = :seller_id
                              ORDER BY time_ordered DESC
                              LIMIT :k OFFSET :offset
                              ''', seller_id=seller_id, k=k, offset=offset)
        return rows

    @staticmethod
    def fulfill(oid, sid):
        app.db.execute('''
                        UPDATE Cart
                        SET fulfilled = TRUE
                        WHERE order_id = :oid
                        AND seller_id = :sid
                       ''', sid=sid, oid=oid)
        
    @staticmethod
    def time_fulfill(oid, sid):
        app.db.execute('''
                        UPDATE Cart
                        SET time_fulfilled = current_timestamp AT TIME ZONE 'America/New_York'
                        WHERE order_id = :oid
                        AND seller_id = :sid
                       ''', sid=sid, oid=oid)
   
    @staticmethod
    def get_order_details(oid, sid):
        rows = app.db.execute('''
        SELECT foo.firstname, foo.lastname, foo.address, foo.email, foo.fulfilled, foo.time_ordered
        FROM
        (SELECT DISTINCT firstname, lastname, address, email, Cart.fulfilled, time_ordered FROM
        Orders, Users, Cart
        WHERE Orders.user_id = Users.id
        AND Orders.id = :oid
        AND Cart.order_id = Orders.id AND
        Cart.seller_id = :sid) as foo
        ''', oid=oid, sid=sid)

        # SELECT DISTINCT firstname, lastname, address, email, foo.fulfilled, foo.time_ordered, isSeller
        # FROM Users
        # LEFT JOIN (SELECT Cart.fulfilled as fulfilled, time_ordered, Cart.user_id
        #         FROM Cart, Orders 
        #         WHERE seller_id = :sid
        #         AND Cart.order_id = Orders.id 
        #         AND Orders.id = :oid
        #         ) as foo
        # ON foo.user_id = Users.id
        # WHERE isSeller = False

        total_items = app.db.execute('''
        SELECT SUM(foo.quantity)
        FROM
        (SELECT * FROM
        Orders, Users, Cart
        WHERE Orders.user_id = Users.id
        AND Orders.id = :oid
        AND Cart.order_id = Orders.id AND
        Cart.seller_id = :sid) as foo
''', oid=oid, sid=sid)

        return rows, total_items[0][0]
    
    @staticmethod
    def num_orders(seller_id):
        rows = app.db.execute('''
                        SELECT COUNT(*)
                        FROM (SELECT DISTINCT Orders.id FROM Orders
                        LEFT JOIN Cart
                        ON Orders.id = Cart.order_id
                        WHERE Cart.seller_id = :seller_id) as foo
                       ''', seller_id=seller_id)
        return rows[0][0]

    @staticmethod
    def topTenProducts(seller_id):
        rows = app.db.execute('''
                        SELECT Products.name, foo.total as total
                        FROM Products
                        LEFT JOIN
                        (SELECT DISTINCT SUM(quantity) as total, product_id
                        FROM Cart, Orders 
                        WHERE Orders.id = Cart.order_id 
                        AND Cart.seller_id = :seller_id                        
                        GROUP BY product_id
                        ORDER BY total DESC
                        LIMIT 10) as foo
                        ON foo.product_id = Products.id
                        WHERE total is NOT NULL
                        ORDER BY total DESC
                        LIMIT 10 
                       ''', seller_id=seller_id)
        return rows
    
    @staticmethod
    def botTenProducts(seller_id):
        rows = app.db.execute('''
                        SELECT name, COALESCE(SUM(quantity), 0) as total
                        FROM   
                        (SELECT Cart.product_id, quantity
                        FROM Cart
                        LEFT JOIN Orders ON Cart.order_id = Orders.id
                        WHERE Cart.seller_id = :seller_id) AS foo2
                        FULL OUTER JOIN
                        (SELECT Products.name, Products.id
                        FROM Inventory 
                        LEFT JOIN Products ON Inventory.product_id = Products.id 
                        WHERE Inventory.user_id = :seller_id) AS foo
                        ON foo2.product_id = foo.id
                        WHERE NOT EXISTS (
                        SELECT 1
                        FROM Products
                        LEFT JOIN (
                            SELECT DISTINCT SUM(quantity) AS total, product_id
                            FROM Cart, Orders 
                            WHERE Orders.id = Cart.order_id 
                            AND Cart.seller_id = :seller_id                       
                            GROUP BY product_id
                            ORDER BY total DESC
                            LIMIT 10
                        ) AS foo_existing
                        ON foo_existing.product_id = foo.id
                        WHERE foo_existing.total IS NOT NULL
                        )
                        GROUP BY name
                        ORDER BY total ASC
                        LIMIT 10
                       ''', seller_id=seller_id)
        return rows

    @staticmethod
    def topFiveBuyers(seller_id):
        rows = app.db.execute('''
                        SELECT foo.total as total, firstname, lastname
                        FROM Users
                        LEFT JOIN
                        (SELECT SUM(quantity) as total, Cart.user_id  
                        FROM Cart, Orders 
                        WHERE Orders.id = Cart.order_id AND Cart.seller_id = :seller_id
                        GROUP BY Cart.user_id
                        ORDER BY total DESC
                        LIMIT 5) as foo
                        ON foo.user_id = Users.id
                        WHERE total is NOT NULL
                        ORDER BY total DESC
                        LIMIT 5;
                       ''', seller_id=seller_id)
        return rows
    
    @staticmethod
    def totalProf(seller_id):
        rows = app.db.execute('''
                        SELECT SUM(foo2.profit) 
                        FROM                      
                        (SELECT foo.total as total, Products.price as price, total*price as profit
                        FROM Products
                        LEFT JOIN
                        (SELECT DISTINCT SUM(quantity) as total, product_id
                        FROM Cart, Orders 
                        WHERE Orders.id = Cart.order_id 
                        AND Cart.seller_id = :seller_id                        
                        GROUP BY product_id
                        ORDER BY total DESC
                        LIMIT 10) as foo
                        ON foo.product_id = Products.id
                        WHERE total is NOT NULL) as foo2
                       ''', seller_id=seller_id)
        return rows[0][0]
