from flask_login import UserMixin
from flask import current_app as app
from werkzeug.security import generate_password_hash, check_password_hash

from .. import login


class User(UserMixin):
    def __init__(self, id, email, firstname, lastname, address, isSeller):
        self.id = id
        self.email = email
        self.firstname = firstname
        self.lastname = lastname
        self.address = address
        self.isSeller = isSeller

    @staticmethod
    def get_by_auth(email, password):
        rows = app.db.execute("""
SELECT password, id, email, firstname, lastname, address, isSeller
FROM Users
WHERE email = :email
""",
                              email=email)
        if not rows:  # email not found
            return None
        elif not check_password_hash(rows[0][0], password):
            # incorrect password
            return None
        else:
            return User(*(rows[0][1:]))

    @staticmethod
    def email_exists(email):
        rows = app.db.execute("""
SELECT email
FROM Users
WHERE email = :email
""",
                              email=email)
        return len(rows) > 0

    @staticmethod
    def register(email, password, firstname, lastname, address, isSeller):
        try:
            rows = app.db.execute("""
INSERT INTO Users(email, password, firstname, lastname, address, isSeller)
VALUES(:email, :password, :firstname, :lastname, :address, :isSeller)
RETURNING id
""",
                                  email=email,
                                  password=generate_password_hash(password),
                                  firstname=firstname, lastname=lastname, address=address, isSeller=isSeller)
            id = rows[0][0]
            balance = app.db.execute('''
            INSERT INTO Balance
            VALUES
            (:user_id, 0)
            ''', user_id = id)
            return User.get(id)
        except Exception as e:
            # likely email already in use; better error checking and reporting needed;
            # the following simply prints the error to the console:
            print(str(e))
            return None

    @staticmethod
    @login.user_loader
    def get(id):
        rows = app.db.execute("""
SELECT id, email, firstname, lastname, address, isSeller
FROM Users
WHERE id = :id
""",
                              id=id)
        return User(*(rows[0])) if rows else None




    @staticmethod
    def edit_email(user_id, new_email):
        app.db.execute('''
            UPDATE Users
            SET email = :new_email
            WHERE id = :user_id
        ''', user_id=user_id, new_email=new_email)

    
    @staticmethod
    def edit_password(user_id, new_password):
        app.db.execute('''
            UPDATE Users
            SET password = :new_password
            WHERE id = :user_id
        ''', user_id=user_id, new_password=generate_password_hash(new_password))

    
    @staticmethod
    def edit_firstname(user_id, new_firstname):
        app.db.execute('''
            UPDATE Users
            SET firstname = :new_firstname
            WHERE id = :user_id
        ''', user_id=user_id, new_firstname=new_firstname)

    @staticmethod
    def edit_lastname(user_id, new_lastname):
        app.db.execute('''
            UPDATE Users
            SET lastname = :new_lastname
            WHERE id = :user_id
        ''', user_id=user_id, new_lastname=new_lastname)

    @staticmethod
    def edit_address(user_id, new_address):
        app.db.execute('''
            UPDATE Users
            SET address = :new_address
            WHERE id = :user_id
        ''', user_id=user_id, new_address=new_address)

    @staticmethod
    def edit_isSeller(user_id, new_isSeller):
        app.db.execute('''
            UPDATE Users
            SET isSeller = :new_isSeller
            WHERE id = :user_id
        ''', user_id=user_id, new_isSeller=new_isSeller)


    @staticmethod
    def return_profile(user_id):
        
        result = app.db.execute('''
            SELECT Users.id, Users.email, Users.firstname, Users.lastname, Users.address, Users.isSeller
            FROM Users
            WHERE id = :user_id
        ''', user_id=user_id)

        user_data = None

        for row in result:
            user_data = {
                'id': row[0],
                'email': row[1],
                'firstname': row[2],
                'lastname': row[3],
                'address': row[4],
                'isSeller': row[5]
            }
            break 

        if not user_data:
            return None

        return User(**user_data)


    # @staticmethod
    # def database_return(firstname_input, lastname_input):
    #     firstname_input = '%' + firstname_input + '%' # change format of search string to %search_term% before using with SQL LIKE
    #     lastname_input = '%' + lastname_input + '%'
    #     rows = app.db.execute("""
    #     SELECT *
    #     FROM Users
    #     WHERE LOWER(firstname) LIKE LOWER(:firstname_input) OR LOWER(lastname) LIKE LOWER(:lastname_input)
    #     """, firstname_input = firstname_input, lastname_input = lastname_input)

    #     user_data = None

    #     for row in rows:
    #         user_data = {
    #             'id': row[0],
    #             'firstname': row[2],
    #             'lastname': row[3],
    #         }
    #         break 

    #     if not user_data:
    #         return None

    #     return _____
