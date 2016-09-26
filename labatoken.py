import telepot
import uuid
from labaperson import *

class Labatoken:
    # Generate a new token.
    def gen_token(db):
        token = str(uuid.uuid4())
        # Prevent saving the same token twice.
        while Labatoken.auth_token(db, token):
            token = str(uuid.uuid4())
        return token

    # Add token to database.
    def add_token(db, token):
        db.connect()
        Token(token=token).save()
        db.close()

    # Delete token from database.
    def del_token(db, token):
        found = False
        db.connect()
        for token in Token.select().where(Token.token==str(token)):
            token.delete_instance()
            found = True
            break
        db.close() 
        return found

    # Check if the token exists on the database.
    def auth_token(db, token):
        authenticated = False
        db.connect()
        if Token.select().where(Token.token==str(token)).exists():
            authenticated = True
        db.close()
        return authenticated


