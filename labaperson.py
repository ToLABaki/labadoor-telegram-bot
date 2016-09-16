from vars import *

class Labaperson:
    def __init__(self, id):
        self._id = id

    def get_id(self):
        return self._id

    def is_admin(self, db):
        found = False
        db.connect()
        for user in User.select().where(User.uid == self.get_id()):
            found = user.admin
        db.close() 
        return found

    def is_user(self, db):
        found = False
        db.connect()
        found = User.select().where(User.uid == self.get_id()).exists()
        db.close() 
        return found

    def add_user(self, db):
        st = False
        db.connect()
        if not is_user(db, uid):
            User(uid = self.get_id(), admin=False).save()
            st = True
        db.close()
        return st

    def del_user(self, db):
        found = False
        db.connect()
        if str(uid).isdigit():
            for user in User.select().where(User.uid == self.get_id()):
                user.delete_instance()
                found = True
                break
        db.close()
        return found


