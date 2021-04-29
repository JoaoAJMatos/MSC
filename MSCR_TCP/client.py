import socket
import threading
import secrets

# Escolher um nickname
nickname = input("Type in your nickname: ")
if nickname == 'admin':
    password = input("Password: ")

# Efetuar conexao com o servidor
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(('127.0.0.1', 55555))

stop_thread = False

# "Ouvir" o servidor e enviar o Nick
def receive():
    while True:
        global stop_thread
        if stop_thread:
            break

        try:
            # Receber mensagem do servidor
            message_ = str(client.recv(1024).decode('ascii'))
            if message_[:9] == 'DHELL_PG':
                publicGenerator = message_[9:]
                print(publicGenerator + '\n')

                next_message_ = str(client.recv(1024).decode('ascii'))
                if next_message_[:9] == 'DHELL_PM':
                    primeMod = next_message_[9:]
                    print(primeMod + '\n')

            # Se a mensagem for um request do Nickname: enviar nick
            if message == 'NICK':
                client.send(nickname.encode('ascii'))
                next_message = client.recv(1024).decode('ascii')

                if next_message == 'PASSWD':
                    client.send(password.encode('ascii'))
                    
                    if client.recv(1024).decode('ascii') == 'REFUSE':
                        print("Connection refused by the server.")
                        stop_thread = True

                elif next_message == 'BAN':
                    print('Connection refused: [BAN]')
                    client.close()
                    stop_thread = True



            else: # Se nao for: Mostrar a mensagem
                print(message)
        except:
            # Cortar comunicacao em caso de erro
            print("An error has occurred!")
            client.close()
            break

# Enviar mensagens ao servidor
def write():
    while True:
        if stop_thread:
            break

        message = f'{nickname}: {input("")}'
        if message[len(nickname)+2:].startswith('/'):
            if nickname == 'admin':
                if message[len(nickname)+2:].startswith('/kick'):
                    client.send(f'KICK {message[len(nickname)+8:]}'.encode('ascii'))
                elif message[len(nickname)+2:].startswith('/ban'):
                    client.send(f'BAN {message[len(nickname)+7:]}'.encode('ascii'))

            else:
                print("You don't have the permits to run this command.\n")
        else:
            client.send(message.encode('ascii'))

# Iniciar as threads para ler e escrever
receive_thread = threading.Thread(target=receive)
receive_thread.start()

write_thread = threading.Thread(target=write)
write_thread.start()