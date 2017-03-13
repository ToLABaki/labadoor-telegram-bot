#!/usr/bin/env python3

from ldap3 import Server, Connection, ALL
from ldap3.protocol.formatters.formatters import format_integer
import telepot
from telepot.delegate import pave_event_space, per_chat_id, create_open
from time import sleep
from subprocess import call
import os

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
Telegram User ID under the Pager field, in Generic settings."
]

API_KEY        = os.environ['TELEGRAM_BOT_API_KEY']
ldap_server    = "ldap.tolabaki.gr"
ldap_user      = "cn=agent,dc=tolabaki,dc=gr"
ldap_password  = os.environ['LDAP_PASSWORD']
search_base    = "dc=tolabaki,dc=gr"
allowed_users  = "objectClass=person"
telegram_uid_field = "pager"
doorlock_bin   = "/usr/local/bin/doorlock"

server = Server(ldap_server, use_ssl=True)
conn = Connection(server, ldap_user, ldap_password)
conn.bind()

class Logic(telepot.helper.ChatHandler):
    def __init__(self, *args, **kwargs):
        super(Logic, self).__init__(*args, **kwargs)

    # Message handler.
    # Don't change function name, it is recognized by default from telepot.
    def on_chat_message(self, msg):
        telegram_uid = msg['from']['id']
        if msg['text'] == "/start":
            for message in welcome_messages[0:4]:
                bot.sendMessage(telegram_uid, message)
                sleep(3)
            bot.sendMessage(telegram_uid, welcome_messages[4])
        elif msg['text'] == "/register":
            for message in registration_instructions[0:2]:
                bot.sendMessage(telegram_uid, message)
            bot.sendMessage(telegram_uid,"Your Telegram ID is: " + str(msg['from']['id']))
        elif msg['text'] == "/open":
            conn.search(search_base, "(&(" + allowed_users + ")(" +
                    telegram_uid_field + "=*))",
                    attributes=[telegram_uid_field])
            found = False
            for user in conn.entries:
                field_value = int(format_integer(user[telegram_uid_field])[0])
                if field_value == telegram_uid:
                    bot.sendMessage(telegram_uid, "Open Sesame!")
                    call([doorlock_bin])
                    found = True
            if found == False:
                bot.sendMessage(telegram_uid,
                        "You need to /register in order to open the door!")

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
