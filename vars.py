from telepot.namedtuple import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardHide, ForceReply
from enum import Enum
from peewee import *

str_guestoops = 'Oops, you\'re a guest so you must send me a password now'
str_heresatoken = 'This code will allow a friend to open the door one time:'
str_botdisabled = 'The bot is disabled for security reasons.'
str_deltoken = 'Send me the token you need cancelled.'
str_adduser = 'Send me the user id you need to register.'
str_deluser = 'Send me the user id you need to remove.'

welcome_messages = [
"Oh, hey there!",
"This bot helps us open the door at τοLabάκι hackerspace.",
"You need to be registered by an admin in order to use the bot.",
"Alternatively, you can also get a one-time access password from a registered \
        member.",
"For more info, you can visit http://wiki.tolabaki.gr/w/To_LABaki",
"Enjoy your stay!"
]

keyboard_user = ReplyKeyboardMarkup(keyboard=[
    ['/open'],
    ['/gettoken', '/deltoken']
    ])

keyboard_admin = ReplyKeyboardMarkup(keyboard=[
    ['/open', '/users', '/tokens'],
    ['/gettoken', '/deltoken'],
    ['/adduser', '/deluser'],
    ['/lock', '/unlock']
    ])

keyboard_guest = ReplyKeyboardMarkup(keyboard=[
    ['/open']
    ])

keyboard_hide = ReplyKeyboardHide(hide_keyboard=True)


markup = keyboard_admin

class state(Enum):
    start, deltoken, guestopen, lockdown, wrongpassword, adduser, 
    deluser = range(7)

st = state.start

DB_PATH="stuff.db"
db = SqliteDatabase(DB_PATH)

class Token(Model):
    token = CharField()
    valid = BooleanField()

    class Meta:
        database=db

class User(Model):
    uid = IntegerField()
    admin = BooleanField()

    class Meta:
        database=db


db.connect()
db.create_tables([Token, User], safe=True)
db.close()
