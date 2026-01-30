### Library Imports

from flask import Flask, render_template, request, redirect, session, jsonify
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

@app.route("/dashboard", methods=["GET"]) ## mention how this was built as a placeholder for login module
def DashboardPage():
    return "Dashboard Page Accessed"

## maybe push out a remedial development where u improve the ui?

## add script.js linking to the html file which will handle the error codes being presented

@app.route("/login", methods=["GET", "POST"])
def LoginPage():
    if request.method == 'POST':
        print(request.form)
        UsernameInput = request.form["username"]
        PasswordInput = request.form["password"]

        if AuthenticationModule.Login(UsernameInput, PasswordInput):
            session["user"] = AuthenticationModule.GetUserRecord(UsernameInput)
            print(session["user"])
            return redirect("/dashboard")
        else:
            return render_template("login.html", success_message = "Login Failed")
        
    return render_template("login.html")

## error = "Invalid Login"

@app.route("/register", methods=["GET", "POST"])
def RegisterPage():
    return "Register Page Accessed"

@app.route("/", methods=["GET"])
def Index():
    return render_template("startup.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)