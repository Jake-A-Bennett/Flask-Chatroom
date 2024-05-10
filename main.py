import mysql.connector
from flask import Flask, render_template, request, url_for, session
from flask_socketio import SocketIO, join_room, leave_room
from flask_session import Session
from Database import Database

database = Database("localhost", "root", "Ilikesushi12!@", "chatroom")

app = Flask(__name__) #might need a sercret key but tbh I don't know why
socketio = SocketIO(app)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)



@app.route("/")
def main():
    return "<p>Welcome to the main page</p>"

@app.route("/login/")
def login():
    return render_template("login.html")

@app.post("/login/")
def get_data():
    users_table = database.get_table("users")
    username = request.form["username"]
    password = request.form["password"]

    for row in users_table:
        if row[0] == username and row[1] == password:
            session["user"] = username
            return app.redirect("/homepage/")

    return app.redirect("/login/") #if I want to do this in real time I have to use sockets.io


@app.route("/createaccount/")
def create_account():
    return render_template("createaccount.html")

@app.post("/createaccount/")
def get_account_info():
    users_table = database.get_table("Users")

    username = request.form["username"]
    password = request.form["password"]

    for row in users_table:
        if row[0] == username:
            return app.redirect("/createaccount/")

    sql = "INSERT INTO users (username, password) VALUES (%s, %s)"
    values = (username, password)
    database.database_cursor.execute(sql, values)

    database.database.commit()

    return app.redirect("/login/")

@app.route("/homepage/")
def home_page():
    if not session.get("user"):
        return app.redirect("/login/")
    else:
        room_table = database.get_table("rooms")
        return render_template("homepage.html", room_table=room_table)

@app.route("/chatroom/<room_name>")
def chat_room(room_name):
    rooms_table = database.get_table("rooms")

    for room in rooms_table:
        if room[1] == room_name:

            return render_template("chatroom.html", room=room_name)
        else:
            app.redirect("/homepage/")

@app.route("/homepage/createroom/")
def create_room():
    return render_template("createroom.html")

@app.post("/homepage/createroom/") #be careful because people could really just spam rooms and that could be a problem
def get_room():
    username = session["user"]
    room_name = request.form["room_name"]

    rooms_table = database.get_table("rooms")

    for room in rooms_table:
        if room[1] == room_name:
            print("There is already a room with this name") #this should also be sent to the user
            return app.redirect("/homepage/createroom/")

    sql = "INSERT INTO rooms (username, room) VALUES (%s, %s)"
    values = (username, room_name)
    database.database_cursor.execute(sql, values)

    database.database.commit()
    print(f"The room {room_name} was successfully created")

    return render_template("createroom.html")

socketio.run(app, allow_unsafe_werkzeug=True, debug=True)
