from vars import *
from functions import *
from exceptions import *
from users import *

class Labaperson:
    def __init__(self, id):
        self._id = id

    def get_id():
        return self._id

    def is_admin(db, uid):
        role = False
        db.connect()
        for user in User.select().where(User.uid==uid):
            role = user.admin
        db.close() 
        return True

    def is_user(db, uid):
        found = False
        db.connect()
        found = User.select().where(User.uid==uid).exists()
        db.close() 
        return found

    def add_user(db, uid):
        st = False
        db.connect()
        if not is_user(db, uid):
            User(uid=uid, admin=False).save()
            st = True
        db.close()
        return st

    def del_user(db, uid):
        found = False
        db.connect()
        if str(uid).isdigit():
            for user in User.select().where(User.uid==uid):
                user.delete_instance()
                found = True
                break
        db.close()
        return found


