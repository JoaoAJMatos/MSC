import threading 
import socket
import hashlib
import secrets
import prime
import random

import os.path
from os import path

loginWrite = False
if not path.exists('logins.txt'):
    loginWrite = True
else:
    with open('logins.txt', 'r') as f3:
        if f3.readlines() == '':
            loginWrite = True

if loginWrite:
    with open('logins.txt', 'a') as f2:
        f2.write('5af9af63c3d67ede16c88986dee08673112a36afecdd8b9f49d3b395fe8dd1eb')

open('banlist.txt', 'w')

# Dados para a conexao
host = '127.0.0.1' # Localhost
port = 55555

# Iniciar o servidor
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
server.bind((host, port)) 
server.listen()

# Array dos clientes, dos nicknames e das encryption keys
clients     = []
nicknames   = []
public_gens = []
prime_mods  = []

# Funcao de comparacao dos hashes
def comp(hash):

    with open('logins.txt', 'r') as f2:
        if str(f2.readline()) == str(hash):
            return True
        else:
            return False

# Enviar mensagens em broadcast para os clientes ligados ao chat
def broadcast(message):
    for client in clients:
        client.send(message)

# Gerir mensagens dos clientes
def handle(client):
    while True:
        try:
            # Broadcast da mensagem
            msg = message = client.recv(1024)

            if msg.decode('ascii').startswith('KICK'):
                if nicknames[clients.index(client)] == 'admin':
                    client_to_kick = msg.decode('ascii')[5:]
                    kick_user(client_to_kick)
                
                else:
                    client.send("You don't have the permits to run this command.".encode('ascii'))

            elif msg.decode('ascii').startswith('BAN'):
                if nicknames[clients.index(client)] == 'admin':
                    client_to_ban = msg.decode('ascii')[4:]
                    kick_user(client_to_ban)

                    with open('banlist.txt', 'a') as f:
                        f.write(f'{client_to_ban}\n')

                    print(f'{client_to_ban} banned from the server.')
                
                else:
                    client.send("You don't have the permits to run this command.".encode('ascii'))


            else:
                broadcast(message)
        except:
            if client in clients:
                # Remover e fechar clientes
                index = clients.index(client)
                clients.remove(client)
                client.close()
                nickname = nicknames[index]
                broadcast(f'{nickname} left the chat!'.encode('ascii'))
                nicknames.remove(nickname)
                break

# Receber dados
def receive():
    ctd = 0

    while True: 

        handshake = False
        # Autorizar a conexao
        client, address = server.accept()
        print(f"Connected with {str(address)}")

        # Key exchange
        public_gen = secrets.randbelow(100)
        prime_mod = prime.getRandomPrimeInteger([0, 1000])
        print(str(public_gen) + ' ' + str(prime_mod))
        public_gens.append(public_gen) 
        prime_mods.append(prime_mods) 

        msg2send  = 'DHELL_PG' + str(public_gens[ctd])
        msg2send_ = 'DHELL_PM' + str(prime_mods[ctd])

        client.send(msg2send.encode('ascii'))
        client.send(msg2send_.encode('ascii'))
        handshake = True


        if handshake:
            # Pedir e guardar o nick do utilizador
            client.send('NICK'.encode('ascii')) # Envia a Keyword ao cliente para fazer um request do Nickname

        nickname = client.recv(1024).decode('ascii')

        with open('banlist.txt', 'r') as f:
            bans = f.readlines()

        if nickname+'\n' in bans:
            client.send('BAN'.encode('ascii'))
            client.close()
            continue

        if nickname == 'admin':
            client.send('PASSWD'.encode('ascii'))
            recvd_pwd = client.recv(1024).decode('ascii')

            recvd_hash = hashlib.sha256(str(recvd_pwd).encode())

            if comp(str(recvd_hash.hexdigest())) == False:
                client.send('REFUSE'.encode('ascii'))
                client.close()
                continue

        nicknames.append(nickname)
        clients.append(client)

        # Informar que o cliente se ligou ao chat
        print(f'Nickname set: {nickname}')
        broadcast(f'[{nickname}] joined the chat!'.encode('ascii'))
        client.send('Connected to the server!'.encode('ascii'))

        # Iniciar a thread para o cliente do lado do servidor
        thread = threading.Thread(target=handle, args=(client,))
        thread.start()

        ctd += 1


def kick_user(client):
    if client in nicknames:
        name_index = nicknames.index(client)
        client_kick = clients[name_index]
        clients.remove(client_kick)
        client_kick.send('You have been kicked by an admin!'.encode('ascii'))
        client_kick.close()
        nicknames.remove(client)
        broadcast(f'[{client}] was kicked by an admin!'.encode('ascii'))


print("Server is listening...")
receive()
