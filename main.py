#!/usr/bin/env python3

from ldap3 import Server, Connection, ALL
from ldap3.protocol.formatters.formatters import format_integer
import telepot
from telepot.delegate import pave_event_space, per_chat_id, create_open
from time import sleep

DB_PATH = 'stuff.db'

welcome_messages = [
    "Oh, hey there!",
    "This bot helps us open the door at τοLabάκι hackerspace.",
    "You need to have an LDAP account in order to open the door.",
    "For more info, you can visit http://wiki.tolabaki.gr/w/To_LABaki",
    "Enjoy your stay!"
]

registration_instructions = [
        "To open the door, you need to add your Telegram user id to your LDAP \
account.",
        "In order to do that, visit https://accounts.tolabaki.gr and add your \
Telegram User ID under the Fax field, in Generic settings."
]
db = peewee.SqliteDatabase(DB_PATH)

class Token(Model):
    token = CharField()

    class Meta:
        database = db


class User(Model):
    uid = IntegerField()
    admin = BooleanField()

    class Meta:
        database = db


class Logic(telepot.helper.ChatHandler):
    def __init__(self, *args, **kwargs):
        super(Logic, self).__init__(*args, **kwargs)

    # Message handler.
    # Don't change function name, it is recognized by default from telepot.
    def on_chat_message(self, msg):
        telegram_uid = msg['from']['id']

if __name__ == "__main__":

    # DelegatorBot creates a new instance of the Logic for each conversation.
    bot = telepot.DelegatorBot(API_KEY,[
        pave_event_space()(
            per_chat_id(), create_open, Logic, timeout=10)
        ])
    bot.message_loop()

    # This loop is necessary; we have to keep running because message_loop() is
    # waiting to accept messages.
    while True:
        sleep(1)
