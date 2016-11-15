#!/usr/bin/env python3

import telepot
from telepot.delegate import pave_event_space, per_chat_id, create_open
from telepot.namedtuple import ReplyKeyboardMarkup, ReplyKeyboardHide
from time import sleep
import peewee
from peewee import Model, IntegerField, BooleanField, CharField
from api_key import API_KEY
from exceptions import *
from labatoken import Labatoken
from labaperson import Labaperson

DB_PATH = 'stuff.db'

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


class FSM(telepot.helper.ChatHandler):
    def __init__(self, *args, **kwargs):
        super(FSM, self).__init__(*args, **kwargs)

    def set_person(self, person):
        self._person = person

    def get_person(self):
        return self._person

    # Message handler. 
    # Don't change function name, it is recognized by default from telepot.
    def on_chat_message(self, msg):
        cmd = msg['text']
        self.set_person(Labaperson(msg['chat']['id']))

        # Set keyboard depending on the role of the user.
        if self.get_person().is_admin(db):
            markup = keyboard_admin
        elif self.get_person().is_user(db):
            markup = keyboard_user
        else:
            markup = keyboard_guest


        try:
            if cmd == '/start':
                self.welcome(bot)

            elif cmd == '/open':
                self.OpenDoor(db, bot, None)

            elif cmd == '/gettoken':
                token = Labatoken.gen_token(db)
                bot.sendMessage(self.get_person().get_id(), token, reply_markup=markup)
                Labatoken.add_token(db, token)

            elif cmd == '/deltoken':
                self.deltoken(db, bot, self.get_person().get_id())

            elif cmd == '/tokens':
                self.ShowTokens(db, bot)

            elif cmd == '/adduser':
                self.adduser(db, bot)

            elif cmd == '/deluser':
                self.deluser(db, bot)

            elif cmd == '/users':
                self.ShowUsers(db, bot)

            elif cmd == '/lock':
                if self.get_person().is_admin(db):
                    self.set_state(state.lockdown)
                else:
                    bot.sendMessage(self.get_person().get_id(), 
                            'Only admins can lock the bot.',
                            reply_markup=markup)
            elif cmd == '/unlock':
                if self.get_person().is_admin(db):
                    self.set_state(state.normal)
                else:
                    bot.sendMessage(self.get_person().get_id(), 
                            'Only admins can unlock the bot.',
                            reply_markup=markup)
            else:
                print(cmd,st)
        except LabadoorBotException as e:
            bot.sendMessage(self.get_person().get_id(), e.get_string(), reply_markup=markup)

        if self.get_state() == state.lockdown:
            bot.sendMessage(self.get_person().get_id(), str_botdisabled,
                    reply_markup=markup)


        elif self.get_state() == state.guestopen:
            self.guest_open(db, bot, cmd)


        elif self.get_state() == state.deltoken:
            if Labatoken.del_token(db, cmd):
                bot.sendMessage(self.get_person().get_id(), 'Token ' + cmd + 
                        ' deleted.', reply_markup=markup)
            else:
                bot.sendMessage(self.get_person().get_id(), cmd + 
                        ': token isn\'t registered', reply_markup=markup)


        elif self.get_state() == state.adduser:
            if self.get_person().add_user(db):
                bot.sendMessage(self.get_person().get_id(), 'User ' + cmd + 
                        ' added.', reply_markup=markup)
            else:
                bot.sendMessage(self.get_person().get_id(), 'User ' + cmd + 
                        ' is already registered.', reply_markup=markup)


        elif self.get_state() == state.deluser:
            if self.get_person().del_user(db):
                bot.sendMessage(self.get_person().get_id(), 'User ' + cmd + 
                        ' deleted.', reply_markup=markup)
            else:
                bot.sendMessage(self.get_person().get_id(), cmd + 
                        ': user isn\'t registered', reply_markup=markup)


    # Welcome messages, sent when user start a chat with the bot (/start).
    def welcome(self, bot):
        for msg in welcome_messages[0:5]:
            bot.sendMessage(self.get_person().get_id(), msg, 
                    reply_markup=keyboard_hide)
            sleep(3)
        bot.sendMessage(self.get_person().get_id(), welcome_messages[5],
                    reply_markup=markup)

    def adduser(self, db, bot):
        if self.get_person().is_admin(db):
            bot.sendMessage(self.get_person().get_id(), str_adduser, reply_markup=markup)
        else:
            raise EditUsersException

    def deluser(self, db, bot):
        if self.get_person().is_admin(db):
            bot.sendMessage(self.get_person().get_id(), str_deluser, reply_markup=markup)
        else:
            raise EditUsersException

    # Ask the user for the token they want to delete.
    def deltoken(self, db, bot, chat_id):
        if self.get_person().is_user(db):
            bot.sendMessage(self.get_person().get_id(), str_deltoken, reply_markup=markup)
        else:
            raise EditTokensException

    # Print a list of all the users.
    def ShowUsers(self, db, bot):
        if self.get_person().is_admin(db):
            db.connect()
            users = User.select()
            if users.count()==0:
                bot.sendMessage(self.get_person().get_id(), "No users.", reply_markup=markup)
            else:
                for user in users:
                    bot.sendMessage(self.get_person().get_id(), str(user.uid), reply_markup=markup)
            db.close() 
        else:
            raise ShowUsersException

    # Print all valid tokens
    def ShowTokens(self, db, bot):
        if self.get_person().is_admin(db):
            db.connect()
            tokens = Token.select()
            if tokens.count()==0:
                bot.sendMessage(self.get_person().get_id(), "No tokens", reply_markup=markup)
            else:
                for token in tokens:
                    bot.sendMessage(self.get_person().get_id(), str(token.token),
                            reply_markup=markup)
            db.close() 
        else:
            raise ShowTokensException


    # If a user tries to open the door, open it.
    # However, if a non-user wants to open the door, change the state in order
    # to ask for an access token.
    def OpenDoor(self, db, bot, token):
        if self.get_person().is_user(db):
            bot.sendMessage(self.get_person().get_id(),'Open', reply_markup=markup)
            # Replace this comment with the command that actually opens the door
        else:
            bot.sendMessage(self.get_person().get_id(), str_guestoops, reply_markup=markup)

    # Open the door if the provided access token is correct.
    def guest_open(self, db, bot, token):
        if auth_token(db, token):
            bot.sendMessage(self.get_person().get_id(),'Open', reply_markup=markup)
        else:
            bot.sendMessage(self.get_person().get_id(),'Invalid token', reply_markup=markup)

    db.connect()
    db.create_tables([Token, User], safe=True)
    db.close()

if __name__ == "__main__":

    # DelegatorBot creates a new instance of the FSM for each conversation.
    bot = telepot.DelegatorBot(API_KEY,[
        pave_event_space()(
            per_chat_id(), create_open, FSM, timeout=10)
        ])
    bot.message_loop()

    # This loop is necessary; we have to keep running because message_loop() is
    # waiting to accept messages.
    while True:
        sleep(1)
