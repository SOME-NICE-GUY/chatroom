import socket
import threading
import sys
from future.moves import tkinter as tk

TARGET_IP = input('Enter the host\'s IP address (localhost\'s IP is : 127.0.0.1): ')
TARGET_PORT = 5555
messages = '----------------------------------conversation started----------------------------------'

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    client.connect((TARGET_IP, TARGET_PORT))
except Exception as e:
    print('the server doesnt exist or isn\'t running at the moment')
    print(f"the error was: {e}")
    exit()
response = client.recv(4096).decode('UTF-8')
if response == 'NO':
    print('you are banned from this server ask the server admin to unban you')
    exit()

name = input('Enter your name: ').lower()
client.sendto(name.encode('UTF-8'), (TARGET_IP, TARGET_PORT))


def receive_incoming_messages():
    global messages, win
    while True:
        try:
            name_of_sender = client.recv(4096).decode('UTF-8')
        except ConnectionResetError:
            print('the admin either closed the server or banned you from the server')
            win.quit()
            return None
        message = client.recv(4096).decode('UTF-8')
        message = message

        if name_of_sender == name:
            name_of_sender = 'YOU'
        messages += f"{name_of_sender}:\n{message}____________________________________________________________\n"
        update_messages()


def main():
    global win, _label, v, messages, messages_label, _label_, new_message, send_button, t2
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
    try:
        client.send("PROGRAM TERMINATED".encode('UTF-8'))
    except ConnectionResetError:
        pass
    sys.exit()


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
        return None
    client.sendto(message.encode('UTF-8'), (TARGET_IP, TARGET_PORT))
    new_message.delete('1.0', 'end')
    update_messages()


t1 = threading.Thread(target=main)
t1.start()
t2 = threading.Thread(target=receive_incoming_messages)
t2.daemon = True
t2.start()
