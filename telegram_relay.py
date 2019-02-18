# coder :- Jacks Esmer

import time
import telepot
import RPi.GPIO as GPIO
import os
import re
import ast

class TelegramBot():

    def __init__(self):
        self.SleepTimeL = 2
        self.telegram_token = ''
        self.users_dict = {}

    def start(self):
        return 'Welcome to reset servers use /help to help!'

    def help(self, chat_id):
        text_help = open(os.path.join(os.getcwd(), 'help.txt'), 'r')
        text_lines = text_help.readlines()
        text_help.close()
        for line in text_lines:
            self.bot.sendMessage(chat_id, line.strip('\n'))
        return 'finish help'

    def reset(self, pin, command):
        GPIO.output(pin, GPIO.LOW)
        time.sleep(self.SleepTimeL)
        GPIO.output(pin, GPIO.HIGH)
        return 'server ' + command[1:] + ' reseted'

    def add_new_user(self, chat_id, name, type):
        read_users = open(os.path.join(os.getcwd(), 'telegram.cfg'), 'r')
        list_users = read_users.read()
        read_users.close()
        new_user_add = list_users.replace("}", ", {0}: ['{1}', '{2}']".format(chat_id, name, type) + '}')
        write_users = open(os.path.join(os.getcwd(), 'telegram.cfg'), 'w')
        write_users.write(new_user_add)
        write_users.close()
        return 'user {0} added'.format(name)

    def remove_user(self, user):
        for key, value in self.users_dict.items():
            if value[0] == user.lower():
                read_users = open(os.path.join(os.getcwd(), 'telegram.cfg'), 'r')
                list_users = read_users.read()
                read_users.close()
                user_removed = list_users.replace(", {0}: ['{1}', '{2}']".format(key, value[0], value[1]) + '}', "}")
                write_users = open(os.path.join(os.getcwd(), 'telegram.cfg'), 'w')
                write_users.write(user_removed)
                write_users.close()
                return 'user {0} removed'.format(value[0])
        return 'user not found\nuse /list to see active users'

    def rename_doors(self, names):
        list_names = names.split('_')
        old_name = list_names[0]
        new_name = list_names[1]
        read_doors = open(os.path.join(os.getcwd(), 'relays.cfg'), 'r')
        list_doors = read_doors.read()
        read_doors.close()
        if '/' not in new_name[0]:
            new_name = '/' + new_name
        new_name_write = list_doors.replace(old_name, new_name)
        write_doors = open(os.path.join(os.getcwd(), 'relays.cfg'), 'w')
        write_doors.write(new_name_write)
        write_doors.close()
        self.rename_help(old_name, new_name)
        self.send_message_all(old_name, new_name)

    def rename_help(self, old_name, new_name):
        read_help = open(os.path.join(os.getcwd(), 'help.txt'), 'r')
        list_help = read_help.read()
        read_help.close()
        new_help_write = list_help.replace(old_name, new_name)
        write_help = open(os.path.join(os.getcwd(), 'help.txt'), 'w')
        write_help.write(new_help_write)
        write_help.close()


    def allowed_users(self, chat_id):
        with open(os.path.join(os.getcwd(), 'telegram.cfg')) as file_id:
            users_txt = file_id.read()
        users = (re.findall(r'{*.*}', users_txt))
        self.users_dict = ast.literal_eval(users[0])
        if chat_id in self.users_dict.keys():
            return True
        return False

    def relays(self):
        with open(os.path.join(os.getcwd(), 'relays.cfg')) as doors:
            relays = doors.read()
        return ast.literal_eval(relays)

    def send_message_all(self, old_name, new_name):
        for key in self.users_dict:
            self.bot.sendMessage(key, 'command {0} now is {1}'.format(old_name, new_name))

    def handle(self, msg):
        chat_id = msg['chat']['id']
        user_name = msg['chat']['first_name']
        command = msg['text']
        doors_commands = self.relays()
        print('chat id: %s' % chat_id)

        try:
            if self.allowed_users(chat_id):
                if command in doors_commands.keys():
                    self.bot.sendMessage(chat_id, self.reset(doors_commands.get(command), command))
                elif command == '/start':
                    self.bot.sendMessage(chat_id, self.start())
                elif command == '/help':
                    self.bot.sendMessage(chat_id, self.help(chat_id))
                elif command == '/add':
                    status = self.users_dict.get(chat_id)[1]
                    if status == 'a':
                        self.bot.sendMessage(chat_id, 'to add user use "/add_id_name_type\n'
                                                      'The id is chat_id telegram\n'
                                                      'The name is the name of person\n'
                                                      'The type is a to admin or u to user\n'
                                                      'Example: /add_0000000_teste_u')
                    else:
                        self.bot.sendMessage(chat_id, "Acess Denied")
                elif command == '/add' + re.findall(r'/*.*', command[4:])[0]:
                    user_new = command.split('_')
                    status = self.users_dict.get(chat_id)[1]
                    if status == 'a':
                        if user_new[3].lower() != 'u' and user_new[3].lower() != 'a':
                            self.bot.sendMessage(chat_id, 'the type must be "a" for admin or "u" for user')
                        else:
                            self.bot.sendMessage(chat_id, self.add_new_user(user_new[1].lower(), user_new[2].lower(), user_new[3].lower()))
                elif command == '/rename':
                    status = self.users_dict.get(chat_id)[1]
                    if status == 'a':
                        self.bot.sendMessage(chat_id, 'to rename use "/rename_oldname_newname, name\n'
                                                      'Example: /rename_/1_/new')
                    else:
                        self.bot.sendMessage(chat_id, "Acess Denied")
                elif command == '/list':
                    status = self.users_dict.get(chat_id)[1]
                    if status == 'a':
                        users = ""
                        for user in self.users_dict.values():
                            users += 'name: {0} type: {1}\n'.format(user[0], user[1])
                        self.bot.sendMessage(chat_id, 'list of users:\n{0}'.format(users))
                    else:
                        self.bot.sendMessage(chat_id, "Acess Denied")
                elif command == '/remove_' + re.findall(r'_(.*)', command)[0]:
                    status = self.users_dict.get(chat_id)[1]
                    if status == 'a':
                        self.bot.sendMessage(chat_id, self.remove_user(re.findall(r'_(.*)', command)[0]))
                    else:
                        self.bot.sendMessage(chat_id, "Acess Denied")
                elif command == '/rename' + re.findall(r'_.*_', command)[0] + re.findall(r'_.*_(.*)', command)[0]:
                    status = self.users_dict.get(chat_id)[1]
                    if status == 'a':
                        old_name = re.findall(r'_(.*)_', command)[0]
                        if '/' not in old_name[0]:
                            old_name = '/' + old_name
                        if old_name in doors_commands:
                            self.rename_doors(re.findall(r'_(.*_.*)', command)[0])
                        else:
                            self.bot.sendMessage(chat_id, old_name + " doesn't exist")
                else:
                    self.bot.sendMessage(chat_id, 'unknow command\nuse /help for help')
            else:
                self.bot.sendMessage(chat_id, "I don't know you!!!")
                for key in self.users_dict:
                    status = self.users_dict.get(key)[1]
                    if status == 'a':
                        self.bot.sendMessage(key, 'new user trying connect\nsend /add_{0}_{1}_u to add like user\n'
                                                  'or /add_{0}_{1}_a to add like admin\n'
                                                  'example /add_{0}_{1}_u'.format(str(chat_id), str(user_name)))
        except IndexError:
            self.bot.sendMessage(chat_id, 'unknow command\nuse /help for help')

    def connect_telegram(self):
        self.bot = telepot.Bot(self.telegram_token)
        self.bot.message_loop(self.handle)

    def run(self):

        GPIO.setmode(GPIO.BCM)

        pinList = [4, 17, 18, 22, 23, 24, 25, 27]
        for pin in pinList:
            GPIO.setup(pin, GPIO.OUT)
            GPIO.output(pin, GPIO.HIGH)

        try:
            self.connect_telegram()
            print('System Started')
        except:
            print('server error trying again in 10 seconds...')
            time.sleep(10)
            print('restarting...')
            self.connect_telegram()

        while 1:
            try:
                time.sleep(10)

            except KeyboardInterrupt:
                print('\n Program interrupted')
                GPIO.cleanup()
                exit()

            except:
                print('Other error or exception occured!')
                GPIO.cleanup()


telegram_bot = TelegramBot()
telegram_bot.run()

