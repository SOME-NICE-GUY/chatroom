import socket
import threading

from future.moves import tkinter as tk

TARGET_IP, TARGET_PORT = '192.168.1.104', 5555
server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
name_self = 'SERVER ADMIN'
messages = ''

server.bind((TARGET_IP, TARGET_PORT))
clients = {}
print('waiting for a client...')
name, address = server.recvfrom(4096)
temp_full_address = address
name = name.decode('utf-8')
address = address[0]
clients[address] = name
full_addr = {address: temp_full_address}
print(f'new client:\n\tname: {name} \t address: {address}\n____________________________')


def receive_incoming_messages():
    global messages, clients, full_addr
    while True:
        message, addr = server.recvfrom(4096)
        full_addr[addr[0]] = addr
        addr = addr[0]
        message = message.decode('utf-8')
        if addr in clients:
            username_ = clients[addr]
        else:
            username_ = addr
        if message == 'PROGRAM TERMINATED':
            print('program ended by the client')
            print(f'user {username_} disconnected')
            server.sendto('PROGRAM TERMINATED'.encode('UTF-8'), full_addr[addr])
            server.sendto('PROGRAM TERMINATED'.encode('UTF-8'), full_addr[addr])
            del clients[addr]
            del full_addr[addr]
            continue
        if addr in clients:
            username_ = clients[addr]
        else:
            clients[addr] = message
            print(f'new client:\n\tname: {message} \t address: {addr}\n____________________________')
            continue
        messages += f'{username_}:\n{message}____________________________________________________________\n'
        for c in full_addr:
            server.sendto(username_.encode('UTF-8'), full_addr[c])
            server.sendto(message.encode('UTF-8'), full_addr[c])
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


def update_messages():
    global messages_label, messages
    messages_label.configure(state='normal')
    messages_label.delete('1.0', 'end')
    messages_label.insert(tk.END, messages)
    messages_label.configure(state='disabled')


def post_message():
    global messages, new_message
    message = new_message.get('1.0', 'end')
    if message == '\n':
        print('you can not send empty messages')
        return None
    messages += f'YOU:\n{message}____________________________________________________________'
    new_message.delete('1.0', tk.END)
    for i in full_addr:
        server.sendto(name_self.encode('UTF-8'), full_addr[i])
        server.sendto(message.encode('UTF-8'), full_addr[i])
    update_messages()


t1 = threading.Thread(target=main)
t1.start()
t2 = threading.Thread(target=receive_incoming_messages)
t2.start()
