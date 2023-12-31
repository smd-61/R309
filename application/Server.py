import socket
import threading
import queue, mysql.connector, json, re, time # Importez la bibliothèque queue pour une communication sûre entre les threads
global z
# Paramètres de connexion à MySQL
config = {
    'user': 'toto',
    'password': 'toto',
    'host': '127.0.0.1',
    'database': 'server',
    'raise_on_warnings': True
}

class ServeurMessagerie:
    global z
    def __init__(self, host, port):
        self.host = host # ip 
        self.port = port # Port
        self.conn = mysql.connector.connect(**config) # Connection à la base de donnée
        self.cursor = self.conn.cursor()
        
        a=0
        while a==0:
            # demande authentification
            x=input("Entrer votre identifiant: ") 
            y=input("Entrer votre mot de passe: ")
            # vérifier si le compte admin existe
            query = f"SELECT * FROM admin WHERE id = '{x}' AND mdp = '{y}';" 
            self.cursor.execute(query)
            result = self.cursor.fetchone()
            if result:
                print("Connexion réussie.")
                a=1
            else:
                print("Identifiants ou mdp incorrects. Connexion échouée.")

        self.clients = [] # liste des clients connectés
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))#Lie le socket à une adresse et un port.
        self.server_socket.listen(5) # definition de nombre de connection maximum
        
        

    def accept_clients(self):
        """
        Methode qui accepte une connection quand un client essaye de se connecter à celui-ci. 
        
        Il lance alors une thread d'écoute pour chaque client. 
        """
        while z:
            try:
                client_socket, client_address = self.server_socket.accept()
            except OSError:
                pass
            print(f"Connexion acceptée de {client_address}")
            client_thread = threading.Thread(target=self.handle_client, args=(client_socket, client_address))
            client_thread.start()
            client_thread2 = threading.Thread(target=self.cmd, args=(client_socket, client_address))
            client_thread2.start()
            self.clients.append((client_socket, client_address)) # ajout de la connection dans la liste

    def handle_client(self, client_socket, client_address):
        '''
        Cette méthode permet de récuperer le message envoyer par le client pour ensuite le traiter.

        Il vérifie ensuite le champs commande pour voir ce qui est demander.

        Ensuite il regarde les autres champs pour avoir des informations sur les données souhaiter.

        Puis les actions sur la base de données sont effectués.

        Et enfin ils sont envoyés aux clients.
        '''
        try:
            while z:
                
                message = client_socket.recv(1024).decode('utf-8') # reçoit message
                
                decode= self.receive_messages(message)
                if not decode:
                    print(f"Déconnexion de {client_address}")
                    self.clients.remove((client_socket, client_address))
                    client_socket.close()
                    break
                elif decode["commande"] == "connection_compte":
                    username = decode["username"]
                    password = decode["password"]
                    
                    query = f"SELECT mot_de_passe FROM Utilisateurs WHERE identifiant = '{username}';"
                    
                    self.cursor.execute(query)
                    result = self.cursor.fetchone()

                    if result and result[0] == password:
                        message = "Connection approuvé"
        
                        client_socket.send(message.encode('utf-8'))
                        # Procédez avec d'autres actions nécessaires après la connexion approuvée
                        # ...
                    else:
                        # Les identifiants sont incorrects
                        message = "Identifiant ou mot de passe incorrect"
                        client_socket.send(message.encode('utf-8'))
                elif decode["commande"] == "inscription":
                    username = decode["username"]
                    password = decode["password"]
                    alias = decode["alias"]
                    email = decode["email"]
                    status = 0

                    # Vérifier si l'utilisateur existe déjà
                    query = f"SELECT * FROM Utilisateurs WHERE identifiant = '{username}';"
                    self.cursor.execute(query)
                    existing_user = self.cursor.fetchone()

                    if existing_user:
                        # L'utilisateur existe déjà
                        message = "Identifant existe"
                        client_socket.send(message.encode('utf-8'))
                    else:
                        # Ajouter l'utilisateur à la base de données
                        insert_query = f"INSERT INTO Utilisateurs (identifiant, alias, mot_de_passe, email, status) VALUES ('{username}', '{alias}', '{password}', '{email}', {status});"
                        self.cursor.execute(insert_query)
                        self.conn.commit()
                        insert_user_channel_query = f"INSERT INTO Utilisateur_Salons (utilisateur_id, salon_nom) VALUES ('{username}', 'General');" # ajout dans le canal général par défaut
                        self.cursor.execute(insert_user_channel_query)
                        self.conn.commit()
                        message = "Inscription approuvé"
                        client_socket.send(message.encode('utf-8'))
                elif decode["commande"] == "recuperation_canaux":
                    query = f"SELECT Salons.nom FROM Utilisateur_Salons JOIN Salons ON Utilisateur_Salons.salon_nom = Salons.nom WHERE Utilisateur_Salons.utilisateur_id = '{decode["username"]}';"
                    self.cursor.execute(query)
                    channels = [row[0] for row in self.cursor.fetchall()]
                    data = {"commande": "recuperation_canaux", "username": decode["username"], "data": channels}
                    json_data = json.dumps(data)
                    try:
                        client_socket.send(json_data.encode('utf-8'))
                    except OSError:
                        print("Connection fermer")
                    
                elif decode["commande"] == "recuperation_util":
                    query = f"SELECT identifiant FROM Utilisateurs WHERE identifiant != '{decode["username"]}';"
                    self.cursor.execute(query)
                    users = [row[0] for row in self.cursor.fetchall()]
                    data = {"commande": "recuperation_util", "username": decode["username"], "data": users}
                    json_data = json.dumps(data)
                    client_socket.send(json_data.encode('utf-8'))
                elif decode["commande"] == "demande_canal":
                    query = f"SELECT * FROM Utilisateur_Salons WHERE salon_nom  = '{decode["canal"]}' AND utilisateur_id  = '{decode["username"]}';"
                    self.cursor.execute(query)
                    result = self.cursor.fetchone()
                    if result:
                        # Le nom du salon et le nom de l'utilisateur existent déjà dans la table Utilisateurs_Salon
                        message = "Deja membre"
                        data = {"commande": "demande_canal", "username": decode["username"], "data": message}
                        json_data = json.dumps(data)
                        client_socket.send(json_data.encode('utf-8'))
                    else:
                        query = f"SELECT nom FROM Salons WHERE nom = '{decode["canal"]}';"
                        self.cursor.execute(query)
                        result = self.cursor.fetchone()
                        if result:
                            query = f"SELECT nom FROM Salons WHERE nom = '{decode['canal']}' AND validation = 1;"
                            self.cursor.execute(query)
                            result = self.cursor.fetchone()
                            if result:
                                query = f"SELECT salon_nom  FROM demande_salon WHERE salon_nom  = '{decode["canal"]}' AND utilisateur_id = '{decode["username"]}';"
                                self.cursor.execute(query)
                                result = self.cursor.fetchone()
                                if result:
                                    message = "Deja demander"
                                    data = {"commande": "demande_canal", "username": decode["username"], "data": message}
                                    json_data = json.dumps(data)
                                    client_socket.send(json_data.encode('utf-8'))
                                else:
                                    message = "En attente de validation"
                                    data = {"commande": "demande_canal", "username": decode["username"], "data": message}
                                    json_data = json.dumps(data)
                                    client_socket.send(json_data.encode('utf-8'))
                                    query_insert = f"INSERT INTO demande_salon (utilisateur_id, salon_nom ) VALUES ('{decode["username"]}', '{decode["canal"]}');"
                                    self.cursor.execute(query_insert)
                                    self.conn.commit()
                            else:
                                message = "Demande validé"
                                data = {"commande": "demande_canal", "username": decode["username"], "data": message}
                                json_data = json.dumps(data)
                                client_socket.send(json_data.encode('utf-8'))
                                query_insert = f"INSERT INTO Utilisateur_Salons (utilisateur_id, salon_nom ) VALUES ('{decode["username"]}', '{decode["canal"]}');"
                                self.cursor.execute(query_insert)
                                self.conn.commit()
                        else:
                            # Le canal n'existe pas ou n'est pas validé
                            message = "Canal inexistant"
                            data = {"commande": "demande_canal", "username": decode["username"], "data": message}
                            json_data = json.dumps(data)
                            client_socket.send(json_data.encode('utf-8'))
                elif decode["commande"] == "supprimer_canal":
                    print(decode)
                    query = f"SELECT * FROM Utilisateur_Salons WHERE salon_nom  = '{decode["canal"]}' AND utilisateur_id  = '{decode["username"]}';"
                    self.cursor.execute(query)
                    result = self.cursor.fetchone()
                    if result:
                        message = "Supprimer"
                        data = {"commande": "supprimer_canal", "username": decode["username"], "data": message}
                        json_data = json.dumps(data)
                        client_socket.send(json_data.encode('utf-8'))
                        query_delete = f"DELETE FROM Utilisateur_Salons WHERE utilisateur_id = '{decode['username']}' AND salon_nom = '{decode['canal']}';"
                        self.cursor.execute(query_delete)
                        self.conn.commit()
                    else:
                        query = f"SELECT nom FROM Salons WHERE nom = '{decode["canal"]}';"
                        self.cursor.execute(query)
                        result = self.cursor.fetchone()
                        if result:
                            query = f"SELECT salon_nom FROM demande_salon WHERE salon_nom = '{decode["canal"]}' AND utilisateur_id = '{decode["username"]}';"
                            self.cursor.execute(query)
                            result = self.cursor.fetchone()
                            if result:
                                message = "Demande annuler"
                                data = {"commande": "supprimer_canal", "username": decode["username"], "data": message}
                                json_data = json.dumps(data)
                                client_socket.send(json_data.encode('utf-8'))
                                query_delete = f"DELETE FROM demande_salon WHERE utilisateur_id = '{decode['username']}' AND salon_nom = '{decode['canal']}';"
                                self.cursor.execute(query_delete)
                                self.conn.commit()
                            else:
                                message = "Pas dedans"
                                data = {"commande": "supprimer_canal", "username": decode["username"], "data": message}
                                json_data = json.dumps(data)
                                client_socket.send(json_data.encode('utf-8'))
                        else:
                            # Le canal n'existe pas ou n'est pas validé
                            message = "Canal inexistant"
                            data = {"commande": "supprimer_canal", "username": decode["username"], "data": message}
                            json_data = json.dumps(data)
                            client_socket.send(json_data.encode('utf-8'))
                elif decode["commande"] == "recuperation_demande1":
                    query = f"SELECT Salons.nom FROM demande_salon JOIN Salons ON demande_salon.salon_nom = Salons.nom WHERE demande_salon.utilisateur_id = '{decode["username"]}';"
                    self.cursor.execute(query)
                    channels1 = [row[0] for row in self.cursor.fetchall()]
                    
                    query = f"SELECT Salons.nom FROM Utilisateur_Salons JOIN Salons ON Utilisateur_Salons.salon_nom = Salons.nom WHERE Utilisateur_Salons.utilisateur_id = '{decode["username"]}';"
                    self.cursor.execute(query)
                    channels2 = [row[0] for row in self.cursor.fetchall()]
                    channels3=channels1+channels2
                    data = {"commande": "recuperation_demande1", "username": decode["username"], "data": channels3}
                    json_data = json.dumps(data)
                    client_socket.send(json_data.encode('utf-8'))
                elif decode["commande"] == "recuperation_demande2":
                    query = f"SELECT Salons.nom FROM demande_salon JOIN Salons ON demande_salon.salon_nom = Salons.nom WHERE demande_salon.utilisateur_id = '{decode["username"]}';"
                    self.cursor.execute(query)
                    channels = [row[0] for row in self.cursor.fetchall()]
                    
                    data = {"commande": "recuperation_demande2", "username": decode["username"], "data": channels}
                    json_data = json.dumps(data)
                    client_socket.send(json_data.encode('utf-8'))



                elif decode["commande"] == "envoi_message_canal":
                    query_insert = f"INSERT INTO messages  (user_identifiant , nom_salon, message_content ) VALUES ('{decode["username"]}', '{decode["destinataire"]}', '{decode["message"]}');"
                    self.cursor.execute(query_insert)
                    self.conn.commit()


                    for client_tuple in self.clients:
                        other_socket, _ = client_tuple
                        if other_socket != client_socket:  # Évitez de renvoyer le message à l'expéditeur
                            data = {"commande": "envoi_message_canal", "username": decode['username'], "destinataire": decode["destinataire"], "message": decode["message"]}
                            json_data = json.dumps(data)
                            other_socket.send(json_data.encode('utf-8'))

                elif decode["commande"] == "envoi_message_prv":

                    query_insert = f"INSERT INTO message_privés  (id_emmeteur , id_receveur, message_content ) VALUES ('{decode["username"]}', '{decode["destinataire"]}', '{decode["message"]}');"
                    self.cursor.execute(query_insert)
                    self.conn.commit()
                        
                        # Lire les résultats de la requête
                        

                    for client_tuple in self.clients:
                        other_socket, _ = client_tuple
                        if other_socket != client_socket:  # Évitez de renvoyer le message à l'expéditeur
                            data = {"commande": "envoi_message_prv", "username": decode['username'], "destinataire": decode["destinataire"], "message": decode["message"]}
                            json_data = json.dumps(data)
                            other_socket.send(json_data.encode('utf-8'))

                elif decode["commande"] == "charger_msg_canal": 
                    
                    query = f"SELECT messages.message_content, messages.user_identifiant FROM messages JOIN Salons ON messages.nom_salon = Salons.nom WHERE Salons.nom = '{decode["destinataire"]}';"
                    self.cursor.execute(query)
                    message = [{"user_identifiant": row[1], "message_content": row[0]} for row in self.cursor.fetchall()]
                    print (message)
                    data = {"commande": "charger_msg_canal", "username": decode["username"], "destinataire": decode["destinataire"], "data": message}
                    json_data = json.dumps(data)
                    client_socket.send(json_data.encode('utf-8'))
                
                elif decode["commande"] == "charger_msg_prv": 
                    query = f"SELECT message_content, id_emmeteur FROM message_privés WHERE (id_emmeteur = '{decode['username']}' AND id_receveur = '{decode['destinataire']}') OR (id_emmeteur = '{decode['destinataire']}' AND id_receveur = '{decode['username']}');"
                    self.cursor.execute(query)
                    messages = [{"user_identifiant": row[1], "message_content": row[0]} for row in self.cursor.fetchall()]
                    data = {"commande": "charger_msg_prv", "username": decode["username"], "destinataire": decode["destinataire"], "data": messages}
                    json_data = json.dumps(data)
                    client_socket.send(json_data.encode('utf-8'))
        except ConnectionResetError:
            print(f"Erreur de connexion avec {client_address}")
            self.clients.remove((client_socket, client_address))
            client_socket.close()            
        

    def cmd(self, client_socket, client_address):
        """
        Méthode qui permet de rentrer des commandes. 

        Entrer "demande" pour voir les demande en attente.

        Entrer "accepte demande "n° demande" " pour accepter

        Entrer "reufse demande "n° demande" " pour refuser

        Entrer "kill" pour arreter le serveur et notifier les clients
        """
        global z
        while True:
            message = input("Entrez votre commande: ")
            match = re.match(r'^ban\s+(\w+)$', message)
            match2 = re.match(r'^kick\s+(\w+)$', message)
            match3 = re.match(r'^kill$', message)
            match4 = re.match(r'accepte demande (\d+)', message)
            match5 = re.match(r'refuse demande (\d+)', message)
            if match:
                # Si le message correspond au motif, extraire le nom d'utilisateur
                query = f"UPDATE Utilisateurs SET ban = CURRENT_TIMESTAMP WHERE identifiant = '{match.group(1)}';"
                self.cursor.execute(query)
                self.conn.commit()
            elif match2:
                query = f"UPDATE Utilisateurs SET ban = CURRENT_TIMESTAMP WHERE identifiant = '{match.group(1)}';"
                self.cursor.execute(query)
                self.conn.commit()
            
            elif message == "demande":
                query = f"SELECT id, utilisateur_id, salon_nom FROM demande_salon;"
                self.cursor.execute(query)
                result = [{"id": row[0], "utilisateur_id": row[1], "salon_nom": row[2]} for row in self.cursor.fetchall()]
                for row in result:
                    print(f"Demande n°{row['id']} : l'utilisateur {row['utilisateur_id']} demande à rejoindre le salon {row['salon_nom']}.")
                    
            if match4:
                # Si le message correspond au motif, extraire le numéro de la demande
                demande_numero = int(match4.group(1))
                query = f"SELECT id, utilisateur_id, salon_nom FROM demande_salon WHERE id = {demande_numero};"
                self.cursor.execute(query)
                result = [{"id": row[0], "utilisateur_id": row[1], "salon_nom": row[2]} for row in self.cursor.fetchall()]
                print(result)
                for row in result:
                    id = row['id']
                    nom = row['utilisateur_id']
                    salon = row['salon_nom']

                query_delete = f"DELETE FROM demande_salon WHERE id = {id};"
                self.cursor.execute(query_delete)
                self.conn.commit()
                query_insert_user_salon = f"INSERT INTO utilisateur_salons (utilisateur_id, salon_nom) VALUES ('{nom}', '{salon}');"
                self.cursor.execute(query_insert_user_salon)
                self.conn.commit()
            elif match3:
                data = {"commande": "sys", "message": "FIN"}
                json_data = json.dumps(data)
                client_socket.send(json_data.encode('utf-8'))
                time.sleep(5)
                for client_tuple in self.clients:
                    client_socket, _ = client_tuple
                    try:
                        client_socket.shutdown(socket.SHUT_RDWR)
                        client_socket.close()
                        self.server_socket.close()
                        z=False
                    except:
                        pass  # Gérer les erreurs éventuelles, par exemple si le client a déjà fermé sa connexion
                    break
                
                return
            if match5:
                # Si le message correspond au motif, extraire le numéro de la demande
                demande_numero = int(match5.group(1))

                query_delete = f"DELETE FROM demande_salon WHERE id = {demande_numero};"
                self.cursor.execute(query_delete)
                self.conn.commit()
                
                        

    def receive_messages(self, data):
        """
        Méthode qui permet de décoder le message reçu en format json.
        """
        decoded_data = json.loads(data)
        return decoded_data
    
if __name__ == "__main__":
    z=True
    host = "127.0.0.1"  # Adresse IP du serveur
    port = 12345  # Port du serveur
    server = ServeurMessagerie(host, port)
    server.accept_clients()
