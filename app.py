from flask import Flask, render_template, request, redirect, url_for # type: ignore
import Constants as CONSTANTS
import sqlite3
import os

ProgramDatabase = None #PDatbase: Database typing

app = Flask(__name__)

CURRENT_USER = None

@app.route('/')
def index():
    return render_template('startup.html')

@app.route('/login.html')
def login():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login_post():
    username = request.form.get('username')
    password = request.form.get('password')

    print("Username: ", username)
    print("Password: ", password)

    tylan = False

    if username == "tylan":
        username = "u cunt tylan"
        tylan = True

    return redirect(url_for('mb_test'))#render_template('main.html', Authenticated=True, Text="Hello " + username, t=tylan);

@app.route('/register.html')
def register():
    return render_template('register.html')

@app.route('/startup.html')
def startup():
    return render_template('startup.html')

@app.route('/main.html')
def mb_test():
    return render_template("main.html", Authenticated=False, Text=request.remote_addr)

@app.route('/pomodoro.html')
def pomodoro_endpoint():
    pass

@app.errorhandler(404)
def not_found_error(error):
    return render_template("error.html", status_code=404, error_message="Page not found.")

@app.errorhandler(405)
def not_found_error(error):
    return render_template("error.html", status_code=405, error_message="Method not allowed.")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)