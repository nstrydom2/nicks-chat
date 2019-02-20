##
## Server class is to handle server side handling
##  for the chat.
##
##

import socket
import sys
import threading
import json
import time
import re

class Server():
    def __init__(self):
        # Constructor
        self.is_exit = False

        # Set interface config
        self.host = '0.0.0.0'
        self.port = 3333

        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        self.clients = []
        self.clients_nicks = {}

        try:
            self.server.bind((self.host, self.port))

            # if the bind is successful it will get to the code below
            # let me know if it went well, k? Thanks babe ;)
            print('[*] Socket setup successful!')

        except socket.error as msg:
            print('[*] Error -- Bind failed.')
            sys.exit(1)

        self.server.listen(100)
        print('[*] Socket is now listening...')

    def client_thread(self, conn, addr):
        is_closed = False
        self.welcome_mat(conn)

        while(is_closed is not True):
            try:
                # Recieve data
                data = conn.recv(4096).decode()

                if data.split(' ')[0] == '<!CLOSE>':
                    print('[*] Connection to <' + addr[0] + ':' + str(addr[1]) + '> was closed.')
                    #self.broadcast(conn, addr, 'disconnected.\n')
                    self.broadcast_client_left(conn, addr)
                    self.clients_nicks.pop(addr[0])
                    self.clients.remove(conn)

                    is_closed = True
                else:
                    # Log the data recieved
                    print('[*] Message recieved from <' + addr[0] + ':' + str(addr[1]) + '> -- {\"' + data + '\"}')

                    # Broadcast message to all clients
                    self.broadcast(conn, addr, data)

            except Exception as ex:
                print('[*] Error -- ' + str(ex))
                break

    def welcome_mat(self, conn):
        logo = None

        client_list = '<!CLIENTS> ' + self.get_client_nicks()
        print('[*] Clients list requested: ' + client_list)

        conn.send(client_list.encode()) # send client list

        with open('/home/ghost/PycharmProjects/nicks_chat/lib/logo.txt', 'rb') as f:
            logo = f.read()

        conn.send(logo)
        conn.send('Welcome to the chat!\n'.encode())
        conn.send('\n[You] joined the room.\n'.encode())

    def broadcast(self, conn, addr, msg):
        nick = self.clients_nicks.get(addr[0])

        if msg is not None:
            for client in self.clients:
                try:
                    if client is not conn:
                        print('[*] Broadcasting to clients.')
                        client.send(('[' + nick + '] ' + msg).encode())
                except:
                    pass
                    #client.close()
                    #self.clients.remove(client)

    def broadcast_client_join(self, conn, addr):
        nick = self.clients_nicks.get(addr[0])

        client_info = {}
        client_info[addr[0]] = nick

        for client in self.clients:
            try:
                if client is not conn:
                    print('[*] Broadcasting new client \'' + nick + '\' to clients.')
                    client.send(('<!CLIENT> ' + json.dumps(client_info)).encode())
            except:
                client.close()
                self.clients.remove(client)

    def broadcast_client_left(self, conn, addr):
        nick = self.clients_nicks.get(addr[0])

        client_info = {}
        client_info[addr[0]] = nick

        print('[*] Broadcasting client \'' + nick + '\' left the room to clients.')

        for client in self.clients:
            try:
                if client is not conn:
                    client.send(('<!REM_CLIENT> ' + json.dumps(client_info)).encode())
            except Exception as ex:
                #client.close()
                print('[*] Error -- ' + str(ex))

    def get_client_nicks(self):
        return json.dumps(self.clients_nicks)

    def run(self):
        try:
            # Continue talking to client
            while(self.is_exit is not True):
                # Waiting for connection from clients
                conn, addr = self.server.accept()

                if conn is not None or addr is not None:
                    print('[*] Connection established with <' + addr[0] + ':' + str(addr[1]) + '>')

                    welcome_data = conn.recv(2048).decode()

                    if welcome_data.find('<!NICK>') is not -1:
                        self.clients_nicks[addr[0]] = welcome_data.split(' ')[1]
                    else:
                        self.clients_nicks[addr[0]] = addr[0]

                    self.clients.append(conn)

                    #self.broadcast(conn, addr, 'joined the room.\n')
                    #time.sleep(1)

                    self.broadcast_client_join(conn, addr)

                    thread = threading.Thread(target=self.client_thread, args=(conn, addr))
                    thread.start()
        except Exception as ex:
            print('[*] Error -- ' + str(ex))
        finally:
            self.server.close()

if __name__ == '__main__':
    server = Server()

    server.run()