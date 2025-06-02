from flask import current_app as app

class BalanceItem:
    def __init__(self, user_id, amount):
        self.user_id = user_id
        self.amount = amount

    @staticmethod
    def get_balance(user_id):
        rows = app.db.execute('''
            SELECT amount
            FROM Balance
            WHERE Balance.user_id = :user_id 
            ''', user_id = user_id)
        return rows if rows is not None else None

    @staticmethod
    def update_balance(user_id, amount):
        rows = app.db.execute("""
            UPDATE Balance
            SET amount = :amount
            WHERE user_id = :user_id
            """,  user_id=user_id,
                    amount=amount)

    @staticmethod
    def withdraw(user_id, withdrawal_amount):
        result = app.db.execute('''
            SELECT amount
            FROM Balance
            WHERE user_id = :user_id
        ''', user_id=user_id)

        current_balance = result[0][0]

        if withdrawal_amount < 0:
            return False


        if withdrawal_amount > current_balance:
            return False


        app.db.execute('''
            UPDATE Balance
            SET amount = amount - :withdrawal_amount
            WHERE user_id = :user_id
        ''', user_id=user_id, withdrawal_amount=withdrawal_amount)

    @staticmethod
    def deposit(user_id, deposit_amount):

        if deposit_amount < 0:
            return False

        app.db.execute('''
            UPDATE Balance
            SET amount = amount + :deposit_amount
            WHERE user_id = :user_id
        ''', user_id=user_id, deposit_amount=deposit_amount)