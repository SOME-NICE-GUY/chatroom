import socket
import threading
import sys
from future.moves import tkinter as tk

TARGET_IP, TARGET_PORT = '127.0.0.1', 5555
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
name_self = 'SERVER ADMIN'
messages = '----------------------------------conversation started----------------------------------'

server.bind((TARGET_IP, TARGET_PORT))
clients = {}
banned_ip_addresses = {}
print('waiting for a client...')
server.listen()


def receive_incoming_messages(the_client: socket.socket, the_address):
    global messages, clients
    name = the_client.recv(4096).decode('UTF-8')
    print(f'name: {name}\n____________________________________________________________')
    clients[name] = [the_client, the_address[0]]
    while True:
        try:
            message = the_client.recv(4096).decode('UTF-8')
        except ConnectionAbortedError or ConnectionResetError:
            break

        if message == 'PROGRAM TERMINATED':
            print(f'user {name} disconnected')
            print("____________________________________________________________")
            del clients[name]
            break
        messages += f'{name}:\n{message}____________________________________________________________\n'
        for c in clients.values():
            c = c[0]
            c.send(name.encode('UTF-8'))
            c.send(message.encode('UTF-8'))
        update_messages()


def main():
    global win, _label, v, messages, messages_label, _label_, new_message, send_button
    win = tk.Tk()
    win.title('server side chat application')
    win.geometry('750x700')
    win.configure(background='gray')

    _label = tk.Label(win, height=1, bg='gray')
    _label.pack()

    v = tk.Scrollbar(win, orient='vertical')
    v.pack(side='right', fill='y')
    messages_label = tk.Text(win, width=60, height=20, yscrollcommand=v.set, bg='black', fg='green', font=0)
    update_messages()
    messages_label.pack()
    v.config(command=messages_label.yview)

    _label_ = tk.Label(win, height=3, bg='gray', text=f'your name is: {name_self}')
    _label_.pack()

    new_message = tk.Text(win, width=75, height=3)
    new_message.pack()

    send_button = tk.Button(text='send', relief=tk.RAISED, borderwidth=12, font=0, width=34, bg='Gray', fg='green'
                            , command=post_message)
    send_button.pack()

    win.mainloop()
    server.close()
    sys.exit()


def update_messages():
    global messages_label, messages
    messages_label.configure(state='normal')
    messages_label.delete('1.0', 'end')
    messages_label.insert(tk.END, messages)
    messages_label.configure(state='disabled')


def post_message():
    global messages, new_message, server, banned_ip_addresses
    message = new_message.get('1.0', 'end')
    if message == '\n':
        return None
    if message[0] == '$':
        message = message[1:]
        if message == 'TERMINATE\n':
            for c in clients.values():
                c = c[0]
                c.close()
            server.close()
            exit()
        elif message[:3] == 'BAN':
            message = message[4:-1]
            if message in clients:
                print(f'banned user {message} with ip address {clients[message][1]}')
                banned_ip_addresses[message] = clients[message][1]
                clients[message][0].close()
                del clients[message]
            else:
                if message in banned_ip_addresses:
                    print(f'the user {message} is already banned use "$UNBAN {message}" to unban the user')
                else:
                    print(f'the user {message} doesnt exist')
        elif message[:5] == 'UNBAN':
            message = message[6:-1]
            user_exists = False
            if message in banned_ip_addresses:
                print(f'unbanned user {message} with ip address {banned_ip_addresses[message]}')
                del banned_ip_addresses[message]
            else:
                if message in clients:
                    print(f'the user {message} is not banned')
                else:
                    print(f'the user {message} does not exist')

        else:
            print('invalid command')
        new_message.delete('1.0', tk.END)
        return None
    messages += f'YOU:\n{message}____________________________________________________________'
    for c in clients.values():
        c = c[0]
        c.send(name_self.encode('UTF-8'))
        c.send(message.encode('UTF-8'))
    new_message.delete('1.0', tk.END)
    update_messages()


t1 = threading.Thread(target=main)
t1.daemon = True
t1.start()

while True:
    try:
        client, address = server.accept()
    except OSError:
        break
    if address[0] in banned_ip_addresses.values():
        reversed_banned_ip_addresses = {value: key for key, value in banned_ip_addresses.items()}
        print(f'banned user {reversed_banned_ip_addresses[address[0]]} with ip address {address[0]} '
              f'tried to connect but was rejected')
        client.send('NO'.encode('UTF-8'))
        continue
    client.send('YES'.encode('UTF-8'))
    print(f'new client from {address}')

    t2 = threading.Thread(target=receive_incoming_messages, args=(client, address))
    t2.daemon = True
    t2.start()
