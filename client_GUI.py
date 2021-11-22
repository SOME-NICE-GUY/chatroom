import socket
import threading

from future.moves import tkinter as tk

messages = ''
TARGET_IP = input('Enter the host\'s IP address (developer\'s IP is : 192.168.1.104): ')
TARGET_PORT = 5555
clients = {TARGET_IP: 'server admin'}
client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
name = input('Enter your name: ').lower()
client.sendto(name.encode('UTF-8'), (TARGET_IP, TARGET_PORT))


def receive_incoming_messages():
    global messages
    while True:
        name_of_sender, addr = client.recvfrom(4096)
        message, addr = client.recvfrom(4096)
        name_of_sender = name_of_sender.decode('UTF-8')
        message = message.decode('UTF-8')
        if message == 'PROGRAM TERMINATED':
            print('program ended')
            exit()

        if name_of_sender == name:
            name_of_sender = 'YOU'
        messages += f"{name_of_sender}:\n{message}____________________________________________________________\n"
        update_messages()


def main():
    global win, _label, v, messages, messages_label, _label_, new_message, send_button
    win = tk.Tk()
    win.title('client side chat application')
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

    _label_ = tk.Label(win, height=3, bg='gray', text=f'your name is: {name}')
    _label_.pack()

    new_message = tk.Text(win, width=75, height=3)
    new_message.pack()

    send_button = tk.Button(text='send', relief=tk.RAISED, borderwidth=12, font=0, width=34, bg='Gray', fg='green'
                            , command=post_message)
    send_button.pack()

    win.mainloop()
    client.sendto('PROGRAM TERMINATED'.encode('UTF-8'), (TARGET_IP, TARGET_PORT))
    exit()


def update_messages():
    global messages_label, messages
    messages_label.configure(state='normal')
    messages_label.delete('1.0', 'end')
    messages_label.insert(tk.END, messages)
    messages_label.configure(state='disabled')


def post_message():
    global messages
    message = new_message.get('1.0', 'end')
    if message == '\n':
        print('you can not send empty messages')
        return None
    client.sendto(message.encode('UTF-8'), (TARGET_IP, TARGET_PORT))
    new_message.delete('1.0', 'end')
    update_messages()


t1 = threading.Thread(target=main)
t1.start()
t2 = threading.Thread(target=receive_incoming_messages)
t2.start()
