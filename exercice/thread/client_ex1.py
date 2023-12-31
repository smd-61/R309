import socket
import threading

def send_message(client_socket):
    while True:
        message = input("Entrez un message : ")
        client_socket.send(message.encode())
        if message == "arret" or message == "bye":
            break

def receive_messages(client_socket):
    while True:
        data = client_socket.recv(1024).decode()
        print(f"\nMessage reçu du serveur : {data}")

def main():
    client_socket = socket.socket()
    client_socket.connect(('127.0.0.1', 5546))

    send_thread = threading.Thread(target=send_message, args=(client_socket,))
    receive_thread = threading.Thread(target=receive_messages, args=(client_socket,))

    send_thread.start()
    receive_thread.start()

    send_thread.join()
    receive_thread.join()

    client_socket.close()

if __name__ == "__main__":
    main()
