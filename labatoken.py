import telepot
import uuid
from users import *

class Labatoken:
    # Generate a new token.
    def gettoken(db, bot, chat_id):
        if is_user(db, chat_id):
            token = str(uuid.uuid4())
            # Prevent saving the same token twice.
            while auth_token(db, token):
                token = str(uuid.uuid4())
            bot.sendMessage(chat_id, token, reply_markup=markup)
            db.connect()
            Token(token=token, valid=True).save()
            db.close()
        else:
            raise EditTokensException

    # Delete a given token.
    def delete_token(db, token):
        found = False
        db.connect()
        for token in Token.select().where(Token.token==str(token)):
            token.delete_instance()
            found = True
            break
        db.close() 
        return found

    # Authenticate a user by the provided token.
    def auth_token(db, token):
        authenticated = False
        db.connect()
        if Token.select().where(Token.token==str(token), Token.valid == True).exists():
            authenticated = True
            Token.update(valid=False).where(Token.token==str(token)).execute()
        db.close()
        return authenticated


