import socket
import threading
a=1
def ecoute(conn):
    global a
    while a == 1:
        message = conn.recv(1024).decode()

        if message == "arret":
            reply = "Fin"
            conn.send(reply.encode())
            conn.close()
            a=2
        elif message == "bye":
            print("Client déconnecté.")
            reply = "Fin"
            conn.send(reply.encode())
            conn.close()
            break
        else:
            print(f"Message reçu du client : {message}")
def ecrire(conn):
    global a
    while a == 1:
        reply = input("Entrez une réponse : ")
        if reply == "arret":
            conn.send(reply.encode())
            a = 2
        else:
            conn.send(reply.encode())

server_socket = socket.socket()
server_socket.bind(('127.0.0.1', 5546))
server_socket.listen()


while a == 1:
    print("En attente de clients...")
    conn, address = server_socket.accept()
    print(f"Nouveau client connecté : {address}")
    t1 = threading.Thread(target=ecoute, args=(conn,))
    t2 = threading.Thread(target=ecrire, args=(conn,))
    
    t1.start()
    t2.start()
    t1.join()
server_socket.close()
