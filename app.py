### Library Imports

from flask import Flask, render_template, request, redirect, session
from modules import *
from dotenv import dotenv_values

## maybe a tad comment, i haven't actually used a single validation constant in the login and register methods man 😭
#import modules

### Global Variables

app = Flask(__name__)
app.secret_key = dotenv_values(".env")["SECRET_KEY"]

ProgramDatabase = Database(constants.DEFAULT_DATABASE_LOCATION)
AuthenticationModule = Authentication(ProgramDatabase)

### Website Endpoint Routes

@app.route("/login", methods=["GET", "POST"])
def LoginPage():
    return "Login Page Accessed"

@app.route("/register", methods=["GET", "POST"])
def RegisterPage():
    return "Register Page Accessed"

@app.route("/", methods=["GET"])
def Index():
    return render_template("startup.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)