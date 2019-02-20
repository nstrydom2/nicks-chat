##
##
##  Client side for chat
##
##
import socket
import select
import threading
import sys
import json
import re

from tkinter import *
from tkinter import scrolledtext, Entry, Button
from itertools import chain

class Client():
    def __init__(self, interface):
        # Constructor
        self.is_exit = False
        self.interface = interface

        self.host = '192.168.1.141'
        self.post = 3333

        self.clients_nicks = None

        if self.interface is 'gui':
            self.window = Tk()

            self.window.title('NicksChat')
            self.window.geometry('575x385')
            self.window.protocol('WM_DELETE_WINDOW', self.close_all)
            #self.window.maxsize(width=575, height=385)
            #self.window.bind('<Destroy>', self.close_all)

            self.top_frame = Frame(self.window)
            self.bottom_frame = Frame(self.window)

            self.top_frame.pack(side=TOP)
            self.bottom_frame.pack(side=TOP)

            self.chattxt = scrolledtext.ScrolledText(self.top_frame, width=60, height=20)
            self.chattxt.config(state=DISABLED)
            self.chattxt.pack(side=LEFT)

            self.usertxt = scrolledtext.ScrolledText(self.top_frame, width=15, height=20)
            self.usertxt.config(state=DISABLED)
            self.usertxt.pack(side=LEFT)


            self.input_txt = scrolledtext.ScrolledText(self.bottom_frame, width=60, height=4)
            self.input_txt.pack(side=LEFT)
            self.window.bind('<Return>', self.enter)

            self.button = Button(self.bottom_frame, command=self.take_input, text='Send', width=12, height=3)
            self.button.pack(side=LEFT)

            self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server.connect((self.host, self.post))
            self.server.send(('<!NICK> ' + 'Nick').encode())

            thread = threading.Thread(target=self.get_from_server)
            thread.setDaemon(True)
            thread.start()

            # thread = threading.Thread(target=self.friends_list_thread)
            # thread.setDaemon(True)
            # thread.start()

            self.window.mainloop()

        else:
            self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server.connect((self.host, self.post))

            self.run()

    def get_from_server(self):
        while (self.is_exit is not True):
            message = self.server.recv(4096).decode()

            print('[*] Received data from server -- ' + message)

            if message[0] == '<':
                data = message.split(' ')

                command = data[0]

                print('[*] Command -- ' + message)

                if command == '<!CLIENTS>':
                    message = message.replace('<!CLIENTS> ', '')

                    print('[*] Clients list recieved -- ' + message)
                    self.clients_nicks = json.loads(message)
                    self.populate_friends_list()

                elif command == '<!CLIENT>':
                    message = message.replace('<!CLIENT> ', '')
                    self.add_friend(json.loads(message))

                elif command == '<!REM_CLIENT>':
                    message = message.replace('<!REM_CLIENT> ', '')
                    self.remove_friend(json.loads(message))

            else:
                self.add_message_chat(message)

    def add_message_chat(self, message):
        self.chattxt.config(state=NORMAL)
        self.chattxt.insert(END, message)
        self.chattxt.config(state=DISABLED)
        self.chattxt.yview(END)

    def send_to_server(self, message):
        self.server.send(message.encode())

    def populate_friends_list(self):
        self.usertxt.config(state=NORMAL)
        self.usertxt.delete('1.0', END)
        self.usertxt.config(state=DISABLED)

        for nick in self.clients_nicks.values():
            print('[*] Inserting \'' + nick + '\' into client list.')
            self.usertxt.config(state=NORMAL)
            self.usertxt.insert(END, nick + '\n')
            self.usertxt.config(state=DISABLED)

    def add_friend(self, client_info):
        self.clients_nicks = dict(chain(self.clients_nicks.items(), client_info.items()))

        for key, nick in client_info.items():
            print('[*] Adding client \'' + nick + '\' from list.')

            self.add_message_chat('[' + nick + '] has joined the room.\n')

        self.populate_friends_list()


    def remove_friend(self, client_info):
        for key, nick in client_info.items():
            print('[*] Removing client \'' + nick + '\' from list.')

            self.add_message_chat('[' + nick + '] has disconnected.\n')

            del self.clients_nicks[key]

        self.populate_friends_list()

    def take_input(self):
        self.message = self.input_txt.get('1.0', END).replace('\n\n', '\n')
        self.input_txt.delete('1.0', END)
        self.chattxt.config(state=NORMAL)
        self.chattxt.insert(END, '[You] ' + self.message)
        self.chattxt.config(state=DISABLED)
        self.chattxt.yview(END)

        self.send_to_server(self.message)

    def enter(self, event=None):
        self.take_input()

    def close_all(self, event=None):
        print("[*] Sending close connection report to server.")
        self.server.send('<!CLOSE>'.encode())

        self.is_exit = True

        print('[*] Exiting')
        self.server.close()
        self.window.destroy()
        sys.exit(1)

    def run(self):
        try:
            while(self.is_exit is not True):

                sockets_list = [sys.stdin, self.server]
                read_sockets, write_socket, error_socket = select.select(sockets_list, [], [])

                for socks in read_sockets:
                    if socks == self.server:
                        message = socks.recv(2048).decode()
                        print(message)
                    else:
                        if self.interface is 'gui':
                            if self.message is not None:
                                self.server.send(self.message.encode())
                                self.usertxt.send('[You] ' + self.message)
                        else:
                            message = sys.stdin.readline()
                            self.server.send(message.encode())
                            sys.stdout.write('[You] ')
                            sys.stdout.write(message)
                            sys.stdout.flush()
        except KeyboardInterrupt as ex:
            print('[*] Exiting')

            self.close_all()


if __name__ == '__main__':
    client = Client('gui')

