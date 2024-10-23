from flask import current_app as app


class User_Info:
    def __init__(self, id, email, password, First_Name, Last_Name):
        self.id = id
        self.email = email
        self.password = password
        self.First_Name = firstname
        self.Last_Name = lastname


    @staticmethod
    def get_info(user_id):
        rows = app.db.execute('''
        SELECT Users.email, Users.password, Users.firstname, Users.lastname
        FROM Users
        WHERE Users.id = :user_id
        ''', user_id = user_id)
        
        return rows if rows is not None else None