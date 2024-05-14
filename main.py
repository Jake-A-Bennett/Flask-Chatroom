import mysql.connector
from flask import Flask, render_template, request, url_for, session
from flask_socketio import SocketIO, join_room, leave_room, emit
from flask_session import Session
from Database import Database

database = Database("localhost", "root", "Ilikesushi12!@", "chatroom")

app = Flask(__name__) #might need a sercret key but tbh I don't know why
socketio = SocketIO(app)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

room = None
admin = {"Jake"}

@app.route("/")
def main():
    return render_template("mainpage.html")

@app.route("/login/")
def login():
    try:
        if session["user"]:
            return app.redirect("/homepage/")
    except:
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
        room_table = database.get_table_sorted("rooms", "room")
        return render_template("homepage.html", room_table=room_table)

@app.route("/chatroom/<room_name>")
def chat_room(room_name):
    rooms_table = database.get_table("rooms")

    for room in rooms_table:
        if room[1] == room_name:
            return render_template("chatroom.html", room=room_name)

    return app.redirect("/homepage/")

@app.route("/homepage/createroom/")
def create_room():
    return render_template("createroom.html")

@app.post("/homepage/createroom/")
def get_room():
    global admin
    username = session["user"]
    room_name = request.form["room_name"]
    rooms_table = database.get_table("rooms")

    allowed_active_rooms = 5

    active_rooms = 0
    for room in rooms_table:
        if room[0] == username:
            active_rooms += 1
        if room[1] == room_name or (active_rooms > allowed_active_rooms and username not in admin):
            print("There is already a room with this name or your over the limit of active rooms") #sent to user
            return app.redirect("/homepage/createroom/")

    sql = "INSERT INTO rooms (username, room) VALUES (%s, %s)"
    values = (username, room_name)
    database.database_cursor.execute(sql, values)

    database.database.commit()
    print(f"The room {room_name} was successfully created")

    return render_template("createroom.html")

@app.route("/homepage/activerooms")
def active_rooms():
    user = session["user"]
    rooms_table = database.get_table("rooms")
    users_rooms = []

    for rooms in rooms_table:
        if rooms[0] == user:
            users_rooms.append(rooms[1])

    return render_template("activerooms.html", rooms=users_rooms)


@socketio.on("send")
def handle_messages(message):
    global room #I tried using session for this so then I wouldn't have to use a global but it was giving me a key error
    emit("distribute message", message, to=room)

@socketio.on("my event")
def connect(new_room):
    global room
    username = session["user"]
    room = new_room
    message = f"{username} has joined the room"
    join_room(room)
    emit("distribute message", message, to=room)

@socketio.on("disconnect")
def disconnect():
    global room
    leave_room(room)
    room = None


@socketio.on("delete_room")
def delete_room(room):
    database.delete_row("rooms", room)




socketio.run(app, allow_unsafe_werkzeug=True, host="0.0.0.0", port=5000)
