import socket
import threading
import time
z=1
def envoie(client_socket):
    global z
    while z==1:
        message = input("Entrez un message : ")
        client_socket.send(message.encode())
        if message == "arret" or message == "bye":
            z=2
        

def ecoute(client_socket):
    global z
    while z==1:
        e = client_socket.recv(1024).decode()
        print(f"\nMessage reçu du serveur : {e}")
        if e== "arret":
            z=2
            

def main():
    global z
    client_socket = socket.socket()
    client_socket.connect(('127.0.0.1', 5546))
    
    t1 = threading.Thread(target=envoie, args=(client_socket,))
    t2 = threading.Thread(target=ecoute, args=(client_socket,))
    t1.start()
    t2.start()
    t1.join()
    t2.join()
    
    client_socket.close()

if __name__ == "__main__":
    main()
