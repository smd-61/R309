from PyQt6.QtWidgets import QApplication, QMessageBox, QScrollArea, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QFormLayout, QHBoxLayout, QListWidget, QComboBox, QTextEdit, QDialog
from PyQt6.QtGui import QPixmap, QFont
from PyQt6 import QtCore
from PyQt6.QtCore import QThread, pyqtSignal
import sys, socket, threading, json, re, time
global b
server_host = "127.0.0.1"  # Adresse IP du serveur
server_port = 12345 # Port utiliser
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # Création d'un socket client avec IPv4 et TCP
client_socket.connect((server_host, server_port)) #Connection au sereur en utilisant la socket client.
b=0

class PageInscription(QWidget):
    global b
    global client_socket, server_host, server_port
    def __init__(self, client_socket):
        """Dans cette partie nous plaçons les différents éléments sur la page d'inscription"""
        super().__init__()
        self.setWindowTitle('Inscription') # Titre de la page
        self.setGeometry(475, 250, 350, 300)  # Positionner la fenetre à 475 250 avec comme dimension 350 * 300
        self.setWindowFlag(QtCore.Qt.WindowType.WindowMaximizeButtonHint, False) #Désactiver bouton pleine écran
        self.setStyleSheet("background-color: beige;") #mettre couleur de fond en beige
        self.setFont(QFont('Aldhabi', 8)) #mettre style du texte
        self.client_socket=client_socket

        self.t=None
        self.layout = QVBoxLayout()
        form_layout = QFormLayout()

        champ_image = QVBoxLayout()
        image_label = QLabel(self)
        pixmap = QPixmap("fond.jpg")  # image
        image_label.setPixmap(pixmap.scaledToHeight(300))  # Ajustez la hauteur de l'image
        champ_image.addWidget(image_label)


        self.label_nom_util = QLabel('Nom d\'utilisateur :', self)
        self.champ_nom_util = QLineEdit(self)
        self.champ_nom_util.setMaximumWidth(200)

        self.label_mdp = QLabel('Mot de passe :', self)
        self.champ_mdp = QLineEdit(self)
        self.champ_mdp.setEchoMode(QLineEdit.EchoMode.Password)
        self.champ_mdp.setMaximumWidth(200)

        self.label_mdp2 = QLabel('Confirmer mot de passe :', self)
        self.champ_mdp2 = QLineEdit(self)
        self.champ_mdp2.setEchoMode(QLineEdit.EchoMode.Password)
        self.champ_mdp2.setMaximumWidth(200)

        self.label_alias = QLabel('Alias :', self)
        self.champ_alias = QLineEdit(self)
        self.champ_alias.setMaximumWidth(200)

        self.label_email = QLabel('Email :', self)
        self.champ_email = QLineEdit(self)
        self.champ_email.setMaximumWidth(200)

        self.bouton_inscription = QPushButton('S\'inscrire', self)
        self.bouton_inscription.clicked.connect(self.validation)
        self.bouton_inscription.setMaximumWidth(200)

        self.bouton_retour = QPushButton('Retour', self)
        self.bouton_retour.setMaximumWidth(200)
        self.bouton_retour.clicked.connect(self.retour)
        self.bouton_retour.setStyleSheet("border: none;")

        form_layout.addRow(self.label_nom_util)
        form_layout.addRow(self.champ_nom_util)
        form_layout.addRow(self.label_mdp)
        form_layout.addRow(self.champ_mdp)
        form_layout.addRow(self.label_mdp2)
        form_layout.addRow(self.champ_mdp2)
        form_layout.addRow(self.label_alias)
        form_layout.addRow(self.champ_alias)
        form_layout.addRow(self.label_email)
        form_layout.addRow(self.champ_email)
        form_layout.addRow(self.bouton_inscription)
        form_layout.addRow(self.bouton_retour)

        # Ajouter des espaces élastiques pour centrer verticalement
        self.layout.addStretch(1)  # Ajouter un espace élastique en haut
        self.layout.addLayout(form_layout)
        self.layout.addStretch(1)  # Ajouter un espace élastique en bas

        # Créer une mise en page horizontale pour centrer les champs
        horizontal_layout = QHBoxLayout()
        horizontal_layout.addLayout(champ_image)  # Ajouter un espace élastique à gauche
        horizontal_layout.addLayout(self.layout)
        self.setLayout(horizontal_layout)

    def retour(self):
        """
        Cette méthode est utilisée pour revenir à la page d'authentification en fermant la fenêtre actuelle en donnant comme argument la socket du client pour continuer à utiliser la même socket.

        Elle est utilisé par le bouton retour.
        """
        self.close()  # Ferme la fenêtre actuelle
        self.pageauthentification = PageAuthentification(client_socket)
        self.pageauthentification.show()
    
    
    
    def validation(self):
        """
        Cette méthode est utilisée pour vérifier si les champs entrer dans les champs de l'inscription (mots de passe sont identiques, email correcte, ...). 

        Si les champs sont validés, ils sont envoyés au server sous forme de dictionnaire.

        Une fois envoyer, il attends une réponse du serveur qui lui indique si l'inscription est validé.

        Sortie:
            Inscription approuvé: L'inscription est bon

            Identifant existe: L'indentifant est déjà utiliser
        """
        if self.champ_mdp.text() != self.champ_mdp2.text():
            QMessageBox.warning(self, 'Erreur', 'Les mots de passe ne correspondent pas.')
            return

        # Vérification que l'email est valide
        email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
        if not re.fullmatch(email_pattern, self.champ_email.text()):
            QMessageBox.warning(self, 'Erreur', 'L\'adresse e-mail n\'est pas valide.')
            return

        # Vérification que les champs ne sont pas vides
        if any(field.text() == '' for field in [self.champ_nom_util, self.champ_mdp, self.champ_mdp2, self.champ_alias, self.champ_email]):
            QMessageBox.warning(self, 'Erreur', 'Veuillez remplir tous les champs.')
            return
        username = self.champ_nom_util.text()
        password = self.champ_mdp.text()
        alias=self.champ_alias.text()
        email=self.champ_email.text()
        data = {"commande": "inscription", "username": username, "password": password, "alias": alias, "email": email}
        json_data = json.dumps(data)
        self.client_socket.send(json_data.encode('utf-8'))
        self.t = self.client_socket.recv(1024).decode("utf-8")
        print(self.t)
        if self.t== "Inscription approuvé":
            self.close()
            self.page = PageAuthentification(client_socket)
            self.page.show()
        elif self.t==  "Identifant existe":
            QMessageBox.warning(self, 'Erreur', 'L\'indentifiant est déjà utilisé.')
        else:
            QMessageBox.warning(self, 'Erreur', 'Problème lors de l\'inscription')
        

class PageAuthentification(QWidget):
    """
        Cette classe est la page d'authentification de l'application de messagerie.

        C'est ici où doit s'identifier afin d'accéder à l'interface du serveur.

    """
    global b
    b=0
    global client_socket, server_host, server_port
    def __init__(self, client_socket):
        super().__init__()
        self.client_socket=client_socket
        self.setWindowTitle('Authentification') # Titre de la page
        self.setGeometry(475, 250, 350, 300)  # Positionner la fenetre à 475 250 avec comme dimension 350 * 300
        self.setWindowFlag(QtCore.Qt.WindowType.WindowMaximizeButtonHint, False) #Désactiver pleine écran
        self.setStyleSheet("background-color: beige;") #mettre couleur de fond en beige
        self.setFont(QFont('Aldhabi', 8))
        self.t=None

        self.layout = QVBoxLayout()
        form_layout = QFormLayout()

        champ_image = QVBoxLayout()
        image_label = QLabel(self)
        pixmap = QPixmap("fond.jpg")  # image
        image_label.setPixmap(pixmap.scaledToHeight(300))  # Ajustez la hauteur de l'image
        champ_image.addWidget(image_label)


        self.label_nom_util = QLabel('Nom d\'utilisateur :', self)
        self.champ_nom_util = QLineEdit(self)
        self.champ_nom_util.setMaximumWidth(200)

        self.label_mdp = QLabel('Mot de passe :', self)
        self.champ_mdp = QLineEdit(self)
        self.champ_mdp.setEchoMode(QLineEdit.EchoMode.Password)
        self.champ_mdp.setMaximumWidth(200)

        self.bouton_login = QPushButton('Connexion', self)
        self.bouton_login.clicked.connect(self.login)
        self.bouton_login.setMaximumWidth(200)

        self.bouton_inscription = QPushButton('S\'inscrire', self)
        self.bouton_inscription.setMaximumWidth(200)
        self.bouton_inscription.clicked.connect(self.inscription)
        self.bouton_inscription.setStyleSheet("border: none;")

        form_layout.addRow(self.label_nom_util)
        form_layout.addRow(self.champ_nom_util)
        form_layout.addRow(self.label_mdp)
        form_layout.addRow(self.champ_mdp)
        form_layout.addRow(self.bouton_login)
        form_layout.addRow(self.bouton_inscription)

        # Ajouter des espaces élastiques pour centrer verticalement
        self.layout.addStretch(1)  # Ajouter un espace élastique en haut
        self.layout.addLayout(form_layout)
        self.layout.addStretch(1)  # Ajouter un espace élastique en bas

        # Créer une mise en page horizontale pour centrer les champs
        horizontal_layout = QHBoxLayout()
        horizontal_layout.addLayout(champ_image)  # Ajouter un espace élastique à gauche
        horizontal_layout.addLayout(self.layout)

        self.setLayout(horizontal_layout)

    def login(self):
        """
        Cette méthode est utilisé pour s'authentifier. Il envoie un dictionnaire avec les champs de la page d'inscription.
        
        Il attends ensuite une réponse du serveur, si les champs sont validés, il est redirigé vers la page principale de l'application avec le compte entrer par rapport au message.

        Sortie:
            Connection approuvé: L'authentification est bon

            Autre: L'authentification a échoué 
        """
        username = self.champ_nom_util.text()
        password = self.champ_mdp.text()
        data = {"commande": "connection_compte", "username": username, "password": password}
        self.send_messages(data)
        
        self.t = self.client_socket.recv(1024).decode("utf-8")
        
        if self.t== "Connection approuvé":
            self.close()
            self.page = PagePrincipale(client_socket, username)
            self.page.show()
        else:
            print(self.t)
            QMessageBox.warning(self, 'Erreur', 'Identifant ou mdp incorrecte')

    def send_messages(self, data):
        json_data = json.dumps(data)
        self.client_socket.send(json_data.encode('utf-8'))
        """
        Cette méthode prend un dictionnaire `data` et le convertit en format JSON.

        Args:
            data (dict): Dictionnaire contenant les données à envoyer.

        """

    def inscription(self):
        self.close()  # Ferme la fenêtre actuelle
        self.inscription_page = PageInscription(client_socket)
        self.inscription_page.show()
        """
        Cette méthode est utilisé pour nous rediriger vers la page d'inscrition.

        """
       
class ClientThread(QThread):
    """
        Cette classe est utilisé pour faire tourner en arrière plan (thread) la socket en écoute pour que quand un message est reçu il puisse traité les informations sans pour autant bloqué les autres taches efféctués.

    """
    message_received = pyqtSignal(str) #Signal émis lorsqu'un message est reçu.
    

    def __init__(self, client_socket, parent=None):
        super().__init__(parent)
        self.client_socket = client_socket # Attribue le socket client pour la communication avec le serveur. Cela permet d'accéder au socket client à l'intérieur de la classe.

    def run(self):
        """
        Cette fonction est la fonction qui est utilisé par la thread, quand un message est reçu il va vérifier si b== 1 (véifier si on est dans la page principale), si oui, il va utiliser la fonction message_received avec comme argument le message
        """
        global b
        while b == 1:  # Utilisez la condition appropriée pour votre logique
            try:
                message = self.client_socket.recv(1024).decode('utf-8')
                if message and b == 1:
                    print(message)
                    self.message_received.emit(message)
                if message and b == 0:
                    # Utilisez self.parent() comme parent pour le QMessageBox
                    QMessageBox.warning(self.parent(), 'Erreur', 'La déconnection de la session précédente a posé quelques soucis lors de l\'authentification. Veuillez réessayer.')

            except Exception as erreur:
                print(f"Erreur dans ClientThread: {erreur}")
                break
        
class PagePrincipale(QWidget):
    """
    Cette classe est la page principale de l'application où l'utilisateurs peut faire différente action.
    """
    global b
    
    b=1
    def __init__(self, client_socket, username):
        super().__init__()
        self.client_socket=client_socket
        self.client_thread = ClientThread(self.client_socket)
        self.client_thread.message_received.connect(self.message_recu)
        self.client_thread.start()
        
        
        self.username=username
        self.setWindowTitle(f'Chat App {self.username}')
        self.setGeometry(475, 250, 600, 400)
        self.setWindowFlag(QtCore.Qt.WindowType.WindowMaximizeButtonHint, False)
        self.setFont(QFont('Aldhabi', 8))
        self.t=None

        
        

        # Layout principal
        self.layoutgeneral = QHBoxLayout()
        self.layoutgauche = QVBoxLayout()
        self.layoutdroite = QVBoxLayout()

        # Zone de recherche des canaux et utilisateurs
        self.layout_titre1=QHBoxLayout()
        self.titre_1 = QLabel("MESSAGE", self)
        self.layout_titre1.addStretch(1)  # Ajouter un espace élastique en haut
        self.layout_titre1.addWidget(self.titre_1)
        self.layout_titre1.addStretch(1)

        self.choix = QComboBox(self)
        self.choix.addItems(['Canaux','Msg privés'])
        self.choix.currentIndexChanged.connect(self.update_channel_list)
        
        self.channel_list = QListWidget(self)
        self.channel_list.clear()
        
        #Récupération des canaux 
        data = {"commande": "recuperation_canaux", "username": self.username}
        self.send_messages(data)

        
        add_channel_button = QPushButton('Ajouter Canal', self)
        add_channel_button.clicked.connect(self.add_channel)
        list = QPushButton('Canaux en attente de validation', self)
        list.clicked.connect(self.show_list)
        suppr = QPushButton('Supprimer un canal', self)
        suppr.clicked.connect(self.supprimer_channel)

        

        # Ajout des éléments au layout gauche
        self.layoutgauche.addLayout(self.layout_titre1)
        self.layoutgauche.addWidget(self.choix)
        self.layoutgauche.addWidget(self.channel_list)
        self.layoutgauche.addWidget(add_channel_button)
        self.layoutgauche.addWidget(list)
        self.layoutgauche.addWidget(suppr)
        self.layoutgauche.addStretch(1)

        # Zone d'affichage des messages
        self.layout_titre2=QHBoxLayout()
        
        #Zone de message avec possibilité de scroll
        self.messages_display_widget = QWidget(self)
        self.messages_display_layout = QVBoxLayout(self.messages_display_widget)
        self.messages_display = QScrollArea(self)
        self.messages_display.setWidgetResizable(True)
        self.messages_display.setWidget(self.messages_display_widget)
        
        self.channel_list.setCurrentItem(self.channel_list.item(0))
        self.titre_2 = QLabel("Conversation", self)
        self.layout_titre2.addStretch(1)  # Ajouter un espace élastique en haut
        self.layout_titre2.addWidget(self.titre_2)
        self.layout_titre2.addStretch(1)
        self.all_messages_widgets = []

        # Zone de saisie des messages
        self.message_input_layout = QHBoxLayout()
        message_input = QLineEdit(self)
        send_button = QPushButton('Envoyer', self)
        send_button.clicked.connect(self.send_message)

        self.message_input_layout.addWidget(message_input)
        self.message_input_layout.addWidget(send_button)

        # Bouton "Ajouter"
        self.layoutdroite.addLayout(self.layout_titre2)
        self.layoutdroite.addWidget(self.messages_display)
        self.layoutdroite.addLayout(self.message_input_layout)

        self.deco = QPushButton('Déconnection', self)
        self.deco.clicked.connect(self.deconnection)
        # Appliquer le layout principal
        self.layoutgeneral.addLayout(self.layoutgauche)
        self.layoutgeneral.addLayout(self.layoutdroite)
        self.layoutfinal=QVBoxLayout(self)
        self.layoutfinal.addLayout(self.layoutgeneral)
        self.layoutfinal.addWidget(self.deco)
        
        self.setLayout(self.layoutfinal)
        self.channel_list.currentItemChanged.connect(self.reset_txt)
    
    def reset_txt(self):
        """
        Cette fonction permet de reset la zone de message pour y mettre les messages de la nouvelle conversation choisi.

        Pour faire cela, il supprimer tout les messages un par un ensuite il fait une requête au serveur pour qu'il lui envoie les messages de la conversation choisi.
        
        """
        current_item = self.channel_list.currentItem()
        if current_item is not None:
            canal = current_item.text()
            
            
            for widget in self.all_messages_widgets:
                self.messages_display_layout.removeWidget(widget)
            self.all_messages_widgets = []

            selected_mode = self.choix.currentText()
            if selected_mode == 'Canaux':
                
                data = {"commande": "charger_msg_canal", "username": self.username, "destinataire": canal}
                self.send_messages(data)
            elif selected_mode == 'Msg privés':
                data = {"commande": "charger_msg_prv", "username": self.username, "destinataire": canal}
                self.send_messages(data)
    
    def send_message(self):
        """
        Cette méthode vérifie si il y a un message, dans la zone d'envoie de texte, si c'est le cas, il vérifie si une conversation est séléctionné.

        Si ces 2 conditions sont réunis, il envoie au serveur un dictionnaire le message en spécifiant sur quel canal ou à quel utilisateur il l'a envoyé puis, il l'affiche dans la zone de texte.

        Et enfin il supprime ce qu'il y a dans la zone d'entrer de texte.
        """
        message = self.message_input_layout.itemAt(0).widget().text()
        current_item = self.channel_list.currentItem()
        if message:
            if current_item is not None:
                canal = current_item.text()
                selected_mode = self.choix.currentText()
                if selected_mode == 'Canaux':
                    data = {"commande": "envoi_message_canal", "username": self.username, "destinataire": canal, "message": message}
                    self.send_messages(data)
                    x = QLabel(f"Moi : {message}", self)
                    self.messages_display_layout.addWidget(x)
                    self.all_messages_widgets.append(x)
                elif selected_mode == 'Msg privés':
                    data = {"commande": "envoi_message_prv", "username": self.username, "destinataire": canal, "message": message}
                    self.send_messages(data)
                    x = QLabel(f"Moi : {message}", self)
                    self.messages_display_layout.addWidget(x)
                    self.all_messages_widgets.append(x)
                self.message_input_layout.itemAt(0).widget().clear()

    def message_recu(self, message):
        """
        Cette méthode est celle utilisé par la thread pour gérer les actions nécessaire quand un messsage est reçu.

        D'abord, le message est convertie pour récuperer le dictionnaire.

        Ensuite, il regarde la commande dans le champs "commande" et ensuite il rentre plus en détail afin d'executer les actions souhaités.

        Args:
            message: message reçu par la thread et renvoyer pour être traiter 
        """
        decode = json.loads(message)
        if decode["commande"] == "envoi_message_canal":
            if decode["username"] != self.username and decode["destinataire"] ==  self.channel_list.currentItem().text():
                x = QLabel(f"{decode['username']}: {decode['message']}", self)
                self.messages_display_layout.addWidget(x) #ajout des messages dans la zone de texte
                self.all_messages_widgets.append(x) #liste des messages qui est utilisé pour la suppressions de celles-ci
                
        elif decode["commande"] == "envoi_message_prv":
            if decode["destinataire"] ==  self.username and decode["username"]==self.channel_list.currentItem().text():
                x = QLabel(f"{decode['username']}: {decode['message']}", self)
                self.messages_display_layout.addWidget(x) #ajout des messages dans la zone de texte
                self.all_messages_widgets.append(x) #liste des messages qui est utilisé pour la suppressions de celles-ci
        
        elif decode["commande"] == "charger_msg_canal":
            print(decode)
            if decode["username"] ==  self.username and decode["destinataire"]==self.channel_list.currentItem().text():
                
                for data in decode["data"]:
                    message_content = data['message_content']
                    user_identifiant = data['user_identifiant']
                    if user_identifiant == self.username:
                        x = QLabel(f"Moi: {message_content}", self)
                        self.messages_display_layout.addWidget(x)#ajout des messages dans la zone de texte
                        self.all_messages_widgets.append(x) #liste des messages qui est utilisé pour la suppressions de celles-ci
                    if user_identifiant != self.username:
                        x = QLabel(f"{user_identifiant}: {message_content}", self)
                        self.messages_display_layout.addWidget(x)#ajout des messages dans la zone de texte
                        self.all_messages_widgets.append(x) #liste des messages qui est utilisé pour la suppressions de celles-ci
        
        elif decode["commande"] == "charger_msg_prv":
            if decode["username"] ==  self.username and decode["destinataire"]==self.channel_list.currentItem().text():
                for data in decode["data"]:
                    message_content = data['message_content']
                    user_identifiant = data['user_identifiant']
                    if user_identifiant == self.username:
                        x = QLabel(f"Moi: {message_content}", self)
                        self.messages_display_layout.addWidget(x)#ajout des messages dans la zone de texte
                        self.all_messages_widgets.append(x)#liste des messages qui est utilisé pour la suppressions de celles-ci
                    if user_identifiant != self.username:
                        x = QLabel(f"{user_identifiant}: {message_content}", self)
                        self.messages_display_layout.addWidget(x)#ajout des messages dans la zone de texte
                        self.all_messages_widgets.append(x)#liste des messages qui est utilisé pour la suppressions de celles-ci
        
        elif decode["commande"] == "recuperation_canaux":
            self.channel_list.clear()
            self.channel_list.addItems(decode["data"])
        elif decode["commande"] == "recuperation_util":
            self.channel_list.clear()
            self.channel_list.addItems(decode["data"])
        elif decode["commande"] == "demande_canal":
            if decode["data"] == "Deja membre":
                QMessageBox.information(self, 'Info', 'Vous êtes déjà membre de ce canal.')
            elif decode["data"] == "En attente de validation":
                QMessageBox.information(self, 'Info', 'Votre demande a été pris en compte. La validation d\'un administrateur est nécessaire.')
            elif decode["data"] == "Demande validé":
                QMessageBox.information(self, 'Info', 'Vous avez été ajouter au canal.')
            elif decode["data"] == "Canal inexistant":
                QMessageBox.warning(self, 'Erreur', 'Ce canal est inexistant.')
            elif decode["data"] == "Deja demander":
                QMessageBox.information(self, 'Info', 'Vous avez déjà fait une demande pour ce canal')
            else:
                QMessageBox.warning(self, 'Erreur', 'Une erreur imprévu est survenue.')
        elif decode["commande"] == "recuperation_demande1":
            dialog = ListSuppr(decode["data"], self.client_socket, self.username) # Ouverture d'une fenetre pour selectionner et supprimer un canal si besoin
            dialog.exec()
            self.channel_list.clear()
            data = {"commande": "recuperation_canaux", "username": self.username}
            self.send_messages(data)
        elif decode["commande"] == "supprimer_canal":
            if decode["data"] == "Supprimer":
                QMessageBox.information(self, 'Info', 'Vous avez été retirer du canal.')
            elif decode["data"]  == "Canal inexistant":
                QMessageBox.warning(self, 'Erreur', 'Ce canal est inexistant.')
            elif decode["data"]  == "Demande annuler":
                QMessageBox.information(self, 'Info', 'Votre demande pour ce canal a été annuler.')
            elif decode["data"]  == "Pas dedans":
                QMessageBox.warning(self, 'Erreur', 'Vous n\'êtes pas dans ce canal.')
            else:
                QMessageBox.warning(self, 'Erreur', 'Une erreur imprévu est survenue.')
        elif decode["commande"] == "recuperation_demande2":
            dialog = ListDemande1(decode["data"])
            dialog.exec()
        elif decode["commande"] == "sys":
            if decode["message"]=="FIN":
                QMessageBox.warning(self, 'Info', 'Le serveur va s\'arreter')
                time.sleep(5)
                self.close()    

    def update_channel_list(self):
        """
        Cette méthode est utilisé pour mettre à jour la liste des canaux ou des utilisateurs selon celui qui a été sélectionner.

        Une requêtes est envoyé au serveur puis traité par la thread.
        """
        selected_mode = self.choix.currentText()

        if selected_mode == 'Canaux':
            data = {"commande": "recuperation_canaux", "username": self.username}
            self.send_messages(data)
            
        elif selected_mode =='Msg privés':
            data = {"commande": "recuperation_util", "username": self.username}
            self.send_messages(data)

    def add_channel(self):
        """
        Cette méthode est utilisé pour ouvrir la fenêtre "Canal" qui va nous permettre de rajouter un canal.

        Une fois la fenêtre ouverte, on rentre un texte qui est récupéreé par cette méthode.
        
        Il va ensuite envoyé une demande au serveur qui va prendre en compte ou non notre demande.
        """
        dialog = Canal()
        result = dialog.exec()
        # Récupérer le nom du canal à partir de la boîte de dialogue
        if result == QDialog.DialogCode.Accepted:
            channel_name = dialog.get_channel_name()
            data = {"commande": "demande_canal", "username": self.username, "canal": channel_name}
            self.send_messages(data)
            self.channel_list.clear()
            data = {"commande": "recuperation_canaux", "username": self.username}
            self.send_messages(data)
            
    def supprimer_channel(self):
        """
        Cette méthode permet d'envoyer une requête au serveur pour récuper la liste des canaux où l'on est membre et ceux auquel on a fait une demande. 

        Il ouvre ensuite une fenêtre après que la thread reçoit la réponse pour pouvoir supprimer un si besoin.
        """
        data = {"commande": "recuperation_demande1", "username": self.username}
        self.send_messages(data)
        
    def show_list(self):
        """
        Cette méthode permet d'envoyer une requête au serveur pour récuper la liste des canaux où l'on est en attente de confirmation. 

        Il ouvre ensuite une fenêtre après que la thread reçoit la réponse pour pouvoir voir celles-ci.
        """
        data = {"commande": "recuperation_demande2", "username": self.username}
        self.send_messages(data)
        

    def deconnection(self):
        """
        Cette méthode permet de nous déconnecter et de nous diriger vers la page d'authentification.
        """
        global b
        b=0
        self.close()  # Ferme la fenêtre actuelle
        self.main = PageAuthentification(client_socket)
        self.main.show()

    def send_messages(self, data):
        """
        Cette méthode prend un dictionnaire `data` et le convertit en format JSON.

        Args:
            data (dict): Dictionnaire contenant les données à envoyer.

        """
        json_data = json.dumps(data)
        self.client_socket.send(json_data.encode('utf-8'))
    
class ListDemande1(QDialog):
    """
    C'est une classe qui ouvre une fenêtre avec une liste des canaux demander afin de les visualiser.

    Sortie: nom du canal
    """
    def __init__(self, items):
        super().__init__()
        self.setWindowTitle("Liste des canaux en attente")
        self.list_widget = QListWidget(self)
        self.list_widget.addItems(items)
        
        

        layout = QVBoxLayout(self)
        layout.addWidget(self.list_widget)
        
class ListSuppr(QDialog):
    """
    C'est une classe qui ouvre une fenêtre avec une liste des canaux dans lequel on est et les canaux demander afin de pouvoir les supprimer.

    Sortie: nom du canal
    """
    def __init__(self, items, client_socket, username):
        super().__init__()
        self.setWindowTitle("Suppression canaux")
        self.username=username
        self.client_socket=client_socket
        self.list_widget = QListWidget(self)
        self.list_widget.addItems(items)
        self.list_widget.setCurrentItem(self.list_widget.item(0))
        self.suppression = QPushButton('Supprimer le canal', self)
        self.suppression.clicked.connect(self.supprimer_channel)

        layout = QVBoxLayout(self)
        layout.addWidget(self.list_widget)
        layout.addWidget(self.suppression)
        

    def supprimer_channel(self):
        """
        C'est une méthode qui envoie l'élement choisi dans la liste au serveur pour que celui qui soit supprimer de la liste des canaux de l'utilisateur.

        """
        selected_item = self.list_widget.currentItem()
        if selected_item:
            data = {"commande": "supprimer_canal", "username": self.username, "canal": selected_item.text()}
            self.send_messages(data)
            
        self.close()
        
            
    def send_messages(self, data):
        json_data = json.dumps(data)
        self.client_socket.send(json_data.encode('utf-8'))

class Canal(QDialog):
    """
    C'est une classe qui ouvre une fenêtre avec une zone de texte pour mettre le nom du canal auquel on veut accéder.

    Sortie: nom du canal
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Ajout canaux")
        
        # Création des widgets
        self.channel_name_input = QLineEdit(self)
        self.validate_button = QPushButton("Valider", self)
        self.validate_button.clicked.connect(self.accept)

        # Mise en page de la boîte de dialogue
        layout = QVBoxLayout(self)
        layout.addWidget(self.channel_name_input)
        layout.addWidget(self.validate_button)

    def get_channel_name(self):
        return self.channel_name_input.text()

if __name__ == '__main__':
    b=1
    app = QApplication(sys.argv)
    authentification = PageAuthentification(client_socket)
    authentification.show()
    
    sys.exit(app.exec())
