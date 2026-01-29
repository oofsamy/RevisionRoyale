### MAYBE MAKE TEST.PY INTO A MODULES.PY FILE AND I IMPORT INTO APP.PY WHICH CONTAINS ALL TO DO WITH FLASK OMG AMAZING

from flask import Flask, render_template, request, redirect, session
from dotenv import dotenv_values
import test as Modules
import Constants
from test import Authentication

app = Flask(__name__)
app.secret_key = dotenv_values(".env")["SECRET_KEY"]

ProgramDatabase = Modules.Database(Constants.DEFAULT_DATABASE_LOCATION)
AuthenticationModule = Modules.Authentication(ProgramDatabase)

@app.route("/login", methods=["GET", "POST"])
def LoginPage():
    if request.method == "POST":
        UsernameInput = request.form["username"]
        PasswordInput = request.form["password"]

        print(UsernameInput, PasswordInput)

        if AuthenticationModule.Login(UsernameInput, PasswordInput):
            session['user'] = UsernameInput
            print("Successful login")
            return redirect('/')
        else:
            return render_template('login.html', error="Invalid Login")


    return render_template("login.html")

@app.route("", methods=["GET"])
def Index():
    return render_template('startup.html')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)