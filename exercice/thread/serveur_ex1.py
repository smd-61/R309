import socket
import threading


def main():
    server_socket= socket.socket()
    server_socket.bind(('127.0.0.1', 5546))

    t1 = threading.Thread(target=lecture, args=(server_socket,))
    t2 = threading.Thread(target=envoie, args=(server_socket,))
    server_socket.listen()
    a = 1
    while a == 1:
        print("En attente de clients...")
        conn, address = server_socket.accept()
        print(f"Nouveau client connecté : {address}")
        t = threading.Thread(target=ecoute, args=(conn,))
        t.start()
        t.join()