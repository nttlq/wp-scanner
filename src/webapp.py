import sqlite3
import hashlib

from flask import Flask, request

app = Flask(__name__)


def connect():
    conn = sqlite3.connect(":memory:", check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE users (username TEXT, password TEXT, role TEXT)")
    cursor.execute(
        "INSERT INTO users VALUES ('admin', 'v1568c271e614e0fb1724da8fd515dc7', 'admin')"
    )
    cursor.execute(
        "INSERT INTO users VALUES ('user1', '827ccb0eea8a706c4c34a16891f84e7b', 'user')"
    )  # 12345 psw
    cursor.execute(
        "INSERT INTO users VALUES ('user2', 'm2575edf8s52ce06fbc5bb76z5dc1ca3', 'moderator')"
    )
    cursor.execute(
        "INSERT INTO users VALUES ('user3', 'j1v72ecj8s52ce06dbc5b376hvdc1cn2', 'moderator')"
    )
    cursor.execute(
        "INSERT INTO users VALUES ('user4', '827ccb0eea8a706c4c34a16891f84e7b', 'user')"
    )

    cursor.execute("CREATE TABLE CVV(user_id INTEGER, cvv TEXT)")
    cursor.execute("INSERT INTO CVV VALUES (1, '123')")
    cursor.execute("INSERT INTO CVV VALUES (2, '456')")
    cursor.execute("INSERT INTO CVV VALUES (3, '789')")
    cursor.execute("INSERT INTO CVV VALUES (4, '321')")
    cursor.execute("INSERT INTO CVV VALUES (5, '654')")
    conn.commit()
    return conn


@app.route("/")
def home():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title> injection testing server</title>
    </head>
    <body>
        <h1> injection testing server</h1>

        <h2>Login</h2>
        <form action="/login" method="get">
            <label for="username">Username:</label><br>
            <input type="text" id="username" name="username"><br>
            <label for="password">Password:</label><br>
            <input type="password" id="password" name="password"><br>
            <input type="submit" value="Login">
        </form>

        <h2>List Users</h2>
        <form action="/users" method="get">
            <label for="role">Role:</label><br>
            <input type="text" id="role" name="role"><br>
            <input type="submit" value="List Users">
        </form>
    </body>
    </html>
    """


@app.route("/login")
def login() -> str:
    username = request.args.get("username", "")
    password = request.args.get("password", "")
    md5 = hashlib.new("md5", password.encode("utf-8"))
    password = md5.hexdigest()
    print("md5 password:", password)
    c = CONNECTION.cursor()
    c.execute(
        "SELECT * FROM users WHERE username = ? and password = ?", (username, password)
    )
    data = c.fetchone()
    if data is None:
        return "Incorrect username and password."
    else:
        return "Welcome %s! Your role is %s." % (username, data[2])


@app.route("/users")
def list_users() -> str:
    role = request.args.get("role", "")
    if role == "admin":
        return "Can't list admins!"
    c = CONNECTION.cursor()
    c.execute("SELECT username, role FROM users WHERE role = '{0}'".format(role))
    data = c.fetchall()
    return str(data)


def start_server():
    global CONNECTION
    CONNECTION = connect()
    app.run(port=5000, debug=True)


if __name__ == "__main__":
    start_server()
