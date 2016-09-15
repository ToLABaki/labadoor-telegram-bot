#!/usr/bin/env python3

import telepot
from api_key import *
from exceptions import *
from labatoken import *
from users import *
from vars import *


class FSM:
    def __init__(self):
        self._state = state.start
        
    def set_state(self, state):
        self._state = state

    def get_state(self, state):
        return self._state

    def set_person(self, person):
        self._person = person

    def get_person(self):
        return self._person

    # Message handler. 
    # Don't change function name, it is recognized by default from telepot.
    def on_chat_message(self, msg):
        cmd = msg['text']
        self.set_person(Labaperson(msg['chat']['id']))
        global db
        global markup

        # Set keyboard depending on the role of the user.
        if self.get_person().is_admin(db):
            markup = keyboard_admin
        if self.get_person().is_user(db):
            markup = keyboard_user
        else:
            markup = keyboard_guest


        if self.get_state() == state.lockdown:
            bot.sendMessage(self.get_person().get_id(), str_botdisabled,
                    reply_markup=markup)


        elif self.get_state() == state.guestopen:
            self.guest_open(db, bot, cmd)
            self.set_state(state.start)


        elif self.get_state() == state.deltoken:
            if delete_token(db, cmd):
                bot.sendMessage(self.get_person().get_id(), 'Token ' + cmd + 
                        ' deleted.', reply_markup=markup)
            else:
                bot.sendMessage(self.get_person().get_id(), cmd + 
                        ': token isn\'t registered', reply_markup=markup)
            self.set_state(state.start)


        elif self.get_state() == state.adduser:
            if add_user(db, cmd):
                bot.sendMessage(self.get_person().get_id(), 'User ' + cmd + 
                        ' added.', reply_markup=markup)
            else:
                bot.sendMessage(self.get_person().get_id(), 'User ' + cmd + 
                        ' is already registered.', reply_markup=markup)
            self.set_state(state.start)


        elif self.get_state() == state.deluser:
            if del_user(db, cmd):
                bot.sendMessage(self.get_person().get_id(), 'User ' + cmd + 
                        ' deleted.', reply_markup=markup)
            else:
                bot.sendMessage(self.get_person().get_id(), cmd + 
                        ': user isn\'t registered', reply_markup=markup)
            self.set_state(state.start)

        elif self.get_state() == state.start:
            self.start()

    # Welcome messages, sent when user start a chat with the bot (/start).
    def welcome(bot):
        global welcome_messages
        for msg in welcome_messages:
            bot.sendMessage(self.get_person().get_id, msg, reply_markup=keyboard_hide)
            sleep(3)


    def start():
            try:
                if cmd == '/start':
                    self.welcome(bot)

                elif cmd == '/open':
                    self.set_state(open(db, bot, None))

                elif cmd == '/gettoken':
                    gettoken(db, bot, self.get_person().get_id())
                    self.set_state(state.start)

                elif cmd == '/deltoken':
                    self.set_state(deltoken(db, bot, self.get_person().get_id()))

                elif cmd == '/tokens':
                    self.ShowTokens(db, bot)

                elif cmd == '/adduser':
                    self.set_state(adduser(db, bot))

                elif cmd == '/deluser':
                    self.set_state(deluser(db, bot))

                elif cmd == '/users':
                    self.ShowUsers(db, bot)
                    self.set_state(state.start)

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
                bot.sendMessage(self.get_person().get_id(), e.string, reply_markup=markup)
                
    def adduser(db, bot):
        self.set_state(state.start)
        if self.get_person().is_admin(db):
            self.set_state(state.adduser)
            bot.sendMessage(self.get_person().get_id(), str_adduser, reply_markup=markup)
        else:
            raise EditUsersException
        return st

    def deluser(db, bot, chat_id):
        global st
        self.set_state(state.start)
        if self.get_person().is_admin(db):
            self.set_state(state.deluser)
            bot.sendMessage(self.get_person().get_id(), str_deluser, reply_markup=markup)
        else:
            raise EditUsersException
        return st

    # Ask the user for the token they want to delete.
    def deltoken(db, bot, chat_id):
        self.set_state(state.start)
        if self.get_person().is_user(db):
            bot.sendMessage(self.get_person().get_id(), str_deltoken, reply_markup=markup)
            self.set_state(state.deltoken)
        else:
            raise EditTokensException
        return st

    # Print a list of all the users.
    def ShowUsers(db, bot):
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
    def ShowTokens(db, bot):
        if self.get_person().is_admin(db):
            db.connect()
            tokens = Token.select().where(Token.valid==True)
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
    def open(db, bot, token):
        global markup
        if self.get_person().is_user(db):
            bot.sendMessage(self.get_person().get_id(),'Open', reply_markup=markup)
            # Replace this comment with the command that actually opens the door
            self.set_state(state.start)
        else:
            bot.sendMessage(self.get_person().get_id(), str_guestoops, reply_markup=markup)
            self.set_state(state.guestopen)
        return st

    # Open the door if the provided access token is correct.
    def guest_open(db, bot, token):
        if auth_token(db, token):
            bot.sendMessage(self.get_person().get_id(),'Open', reply_markup=markup)
        else:
            bot.sendMessage(self.get_person().get_id(),'Invalid token', reply_markup=markup)


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
        pass
