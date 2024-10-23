from flask import current_app as app


class Cart:
    def __init__(self, id, user_id, product_id, seller_id, quantity, saved, order_id, time_ordered, fulfilled, time_fulfilled):
        self.id = id
        self.user_id = user_id
        self.product_id = product_id
        self.seller_id = seller_id
        self.quantity = quantity
        self.saved = saved
        self.order_id = order_id
        self.time_ordered = time_ordered
        self.fulfilled = fulfilled
        self.time_fulfilled = time_fulfilled


# given a user id, find the items in the cart for that user
    @staticmethod
    def get_cart(user_id):
        rows = app.db.execute('''
    SELECT Cart.id as id,
    Products.name AS name,
    CONCAT(Users.firstname, ' ', Users.lastname) AS seller,
    Cart.seller_id AS seller_id,
    Products.price AS price,
    Products.id AS product_id,                
    Cart.quantity AS quantity,
    (Products.price * Cart.quantity) AS total
    FROM Cart
    JOIN Products ON Cart.product_id = Products.id
    JOIN Users ON Users.id = Cart.seller_id
    WHERE Cart.user_id = :user_id AND saved = FALSE AND order_id IS NULL
    ORDER BY Products.name;
        ''', user_id = user_id)
        return rows if rows is not None else None




# given a new product quantity, update
    @staticmethod
    def adjust_quantity(user_id, product_id, seller_id, quantity):
        app.db.execute('''
        UPDATE Cart
        SET quantity = :quantity
        WHERE user_id = :user_id
        AND product_id = :product_id
        AND seller_id = :seller_id
        RETURNING quantity
        ''',
        user_id = user_id, product_id = product_id, seller_id = seller_id, quantity = quantity)
        return Cart.get_cart(user_id)
   
# remove products from cart
    @staticmethod
    def remove_product(user_id, product_id, seller_id):
        app.db.execute('''
        DELETE FROM Cart
        WHERE user_id = :user_id
        AND product_id = :product_id
        AND seller_id = :seller_id
        RETURNING user_id
        ''', user_id = user_id, product_id = product_id, seller_id = seller_id)
        return Cart.get_cart(user_id)




# add item to cart
    @staticmethod
    def add_item_to_cart(user_id, product_id, seller_id, quantity):
            try:
                # if item is in cart
                existing_item = app.db.execute("""
        SELECT quantity FROM Cart
        WHERE user_id = :user_id
        AND product_id = :product_id
        AND seller_id = :seller_id
        AND order_id IS NULL
        """,
                    user_id=user_id,
                    product_id=product_id,
                    seller_id = seller_id
                )


                if existing_item:
                    app.db.execute("""
        UPDATE Cart
        SET quantity = quantity + :quantity
        WHERE user_id = :user_id
        AND product_id = :product_id
        AND seller_id = :seller_id
        """,
                        quantity=quantity,
                        user_id=user_id,
                        product_id=product_id,
                        seller_id=seller_id
                    )
                else:
                    # if item is not in cart, add
                    app.db.execute("""
        INSERT INTO Cart (id, user_id, product_id, seller_id, quantity)
        VALUES (default, :user_id, :product_id, :seller_id, :quantity)
        """,
                        user_id=user_id,
                        product_id=product_id,
                        seller_id=seller_id,
                        quantity=quantity
                    )
                return True
            except Exception as e:
                print(str(e))
            return None


# save for later
    @staticmethod
    def check_saved(user_id, seller_id, product_id):
        app.db.execute('''
        UPDATE Cart
        SET saved = NOT saved
        WHERE user_id = :user_id
        AND seller_id = :seller_id
        AND product_id = :product_id
        RETURNING saved
        ''',
        user_id = user_id,seller_id = seller_id, product_id = product_id)


# get saved items
    @staticmethod
    def get_saved(user_id):
        rows = app.db.execute('''
        SELECT Products.name AS name,
        CONCAT(Users.firstname, ' ', Users.lastname) AS seller,
        Cart.seller_id AS seller_id,
        Products.price AS price,
        Products.id AS product_id,                
        Cart.quantity AS quantity,
        (Products.price * Cart.quantity) AS total
        FROM Cart
        JOIN Products ON Cart.product_id = Products.id
        JOIN Users ON Users.id = Cart.seller_id
        WHERE Cart.user_id = :user_id AND saved = TRUE AND order_id IS NULL
        ORDER BY Products.name;
''',
    user_id = user_id)
        return rows if rows is not None else None

    @staticmethod
    def new_order(user_id):
        newid = app.db.execute('''
        INSERT INTO Orders (id, user_id, fulfilled, time_ordered)
        VALUES (default, :user_id, default, default);
        ''', 
        user_id = user_id)

    @staticmethod
    def get_orders(user_id):
        rows = app.db.execute('''
        Select id, user_id, fulfilled, time_ordered, delivery_addy
        FROM Orders
        WHERE user_id = :user_id
        ''',
        user_id = user_id
        )
        return rows if rows is not None else None
    
    @staticmethod
    def get_max_id():
        next_max_id = app.db.execute('''
        SELECT MAX(id)
        FROM Orders
         ''')
        return next_max_id


    @staticmethod
    def set_order(id, order_id):
        app.db.execute('''
        UPDATE Cart
        SET order_id = :order_id
        WHERE id = :id
        ''',
        id=id, order_id = order_id)

    @staticmethod
    def set_fulfilled(order_id):
        app.db.execute('''
        UPDATE Orders
        SET fulfilled = true
        WHERE id = :order_id
        ''',
        id=id, order_id = order_id)

    @staticmethod
    def get_from_order_id(order_id):
        rows = app.db.execute('''
        SELECT
        Products.name AS name,
        Cart.seller_id AS seller_id,
        CONCAT(Users.firstname, ' ', Users.lastname) AS seller,    
        Products.price AS price,
        Products.id AS product_id,
        Cart.order_id AS order_id,                
        Cart.quantity AS quantity,
        (Products.price * Cart.quantity) AS total,
        Cart.fulfilled AS fulfilled,
        Cart.time_fulfilled AS time_fulfilled
        FROM Cart
        JOIN Products ON Cart.product_id = Products.id
        JOIN Users ON Users.id = Cart.seller_id                      
        WHERE Cart.order_id = :order_id
        ''',
        order_id = order_id
        )
        return rows if rows is not None else None

    @staticmethod
    def set_delivery_addy(order_id, delivery_addy):
        app.db.execute('''
        UPDATE Orders
        SET delivery_addy = :delivery_addy
        WHERE id = :order_id
        ''',
        order_id = order_id, delivery_addy = delivery_addy)
    
    @staticmethod
    def get_purchase(user_id, sort_by):
        if sort_by == "price_ascending":
            rows = app.db.execute('''
            SELECT Products.name as name, Products.price as price, Users.firstname as firstname, Users.lastname as lastname, Cart.quantity as quantity, Cart.time_fulfilled as time, Cart.order_id as order_id
            FROM Cart, Products, Users
            WHERE Products.id = Cart.product_id AND Cart.user_id = :user_id AND Cart.seller_id = Users.id
            ORDER BY price ASC
            ''', user_id = user_id)
        
        elif sort_by == "price_descending":
            rows = app.db.execute('''
            SELECT Products.name as name, Products.price as price, Users.firstname as firstname, Users.lastname as lastname, Cart.quantity as quantity, Cart.time_fulfilled as time, Cart.order_id as order_id
            FROM Cart, Products, Users
            WHERE Products.id = Cart.product_id AND Cart.user_id = :user_id AND Cart.seller_id = Users.id
            ORDER BY price DESC
            ''', user_id = user_id)

        elif sort_by == "time_newest":
            rows = app.db.execute('''
            SELECT Products.name as name, Products.price as price, Users.firstname as firstname, Users.lastname as lastname, Cart.quantity as quantity, Cart.time_fulfilled as time, Cart.order_id as order_id
            FROM Cart, Products, Users
            WHERE Products.id = Cart.product_id AND Cart.user_id = :user_id AND Cart.seller_id = Users.id AND Cart.fulfilled = true
            ORDER BY time DESC
            ''', user_id = user_id)

        elif sort_by == "time_oldest":
            rows = app.db.execute('''
            SELECT Products.name as name, Products.price as price, Users.firstname as firstname, Users.lastname as lastname, Cart.quantity as quantity, Cart.time_fulfilled as time, Cart.order_id as order_id
            FROM Cart, Products, Users
            WHERE Products.id = Cart.product_id AND Cart.user_id = :user_id AND Cart.seller_id = Users.id AND Cart.fulfilled = true
            ORDER BY time ASC
            ''', user_id = user_id)

        elif sort_by == "name_a":
            rows = app.db.execute('''
            SELECT Products.name as name, Products.price as price, Users.firstname as firstname, Users.lastname as lastname, Cart.quantity as quantity, Cart.time_fulfilled as time, Cart.order_id as order_id
            FROM Cart, Products, Users
            WHERE Products.id = Cart.product_id AND Cart.user_id = :user_id AND Cart.seller_id = Users.id AND Cart.fulfilled = true
            ORDER BY name ASC
            ''', user_id = user_id)

        elif sort_by == "name_z":
            rows = app.db.execute('''
            SELECT Products.name as name, Products.price as price, Users.firstname as firstname, Users.lastname as lastname, Cart.quantity as quantity, Cart.time_fulfilled as time, Cart.order_id as order_id
            FROM Cart, Products, Users
            WHERE Products.id = Cart.product_id AND Cart.user_id = :user_id AND Cart.seller_id = Users.id AND Cart.fulfilled = true
            ORDER BY name DESC
            ''', user_id = user_id)

        else:
            rows = app.db.execute('''
            SELECT Products.name as name, Products.price as price, Users.firstname as firstname, Users.lastname as lastname, Cart.quantity as quantity, Cart.time_fulfilled as time, Cart.order_id as order_id
            FROM Cart, Products, Users
            WHERE Products.id = Cart.product_id AND Cart.user_id = :user_id AND Cart.seller_id = Users.id AND Cart.fulfilled = true
            ORDER BY time DESC
            ''', user_id = user_id)


        return rows if rows is not None else None

    @staticmethod
    def get_all_orders(user_id):
        rows = app.db.execute('''
        SELECT
        Products.name AS name,
        Cart.seller_id AS seller_id,
        CONCAT(Users.firstname, ' ', Users.lastname) AS seller,    
        Products.price AS price,
        Products.id AS product_id,
        Cart.order_id AS order_id,                
        Cart.quantity AS quantity,
        (Products.price * Cart.quantity) AS total,
        Cart.fulfilled AS fulfilled,
        Cart.time_fulfilled AS time_fulfilled
        FROM Cart
        JOIN Products ON Cart.product_id = Products.id
        JOIN Users ON Users.id = Cart.seller_id                      
        WHERE Cart.user_id = user_id AND Cart.order_id IS NOT NULL
        ORDER BY fulfilled, order_id DESC
        ''',
        user_id = user_id
        )
        return rows if rows is not None else None
