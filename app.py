### Library Imports

from flask import Flask, render_template, request, redirect, session
from modules import *
from dotenv import dotenv_values

### Global Variables

app = Flask(__name__)
app.secret_key = dotenv_values(".env")["SECRET_KEY"]

ProgramDatabase = Database(constants.DEFAULT_DATABASE_LOCATION)
AuthenticationModule = Authentication(ProgramDatabase)

### Website Endpoint Routes
@app.route("/dashboard", methods=["GET"])
def DashboardPage():
    if "user" not in session:
        return render_template("login.html")

    user_subjects = [
        {"SubjectName": "Computer Science", "ExamBoard": "OCR", "LastReviewed": "2 days ago"},
        {"SubjectName": "Mathematics", "ExamBoard": "Edexcel", "LastReviewed": "Today"},
        {"SubjectName": "Physics", "ExamBoard": "AQA", "LastReviewed": "Never"},
        {"SubjectName": "History", "ExamBoard": "WJEC", "LastReviewed": "1 week ago"},
        {"SubjectName": "English Lit", "ExamBoard": "Eduqas", "LastReviewed": "Yesterday"},
    ]

    return render_template("authenticated/dashboard.html", ActivePage="dashboard", Subjects=user_subjects)

@app.route("/timetable", methods=["GET"])
def TimetablePage():
    if "user" not in session:
        return render_template("login.html")

    return render_template("authenticated/timetable.html", ActivePage="timetable")

@app.route("/timer", methods=["GET"])
def TimerPage():
    if "user" not in session:
        return render_template("login.html")

    return render_template("authenticated/timer.html", ActivePage="timer")

@app.route("/statistics", methods=["GET"])
def StatisticsPage():
    if "user" not in session:
        return render_template("login.html")

    return render_template("authenticated/statistics.html", ActivePage="statistics")

@app.route("/leaderboard", methods=["GET"])
def LeaderboardPage():
    if "user" not in session:
        return render_template("login.html")

    return render_template("authenticated/leaderboard.html", ActivePage="leaderboard")

@app.route("/base_auth", methods=["GET"])
def BaseAuthPage():
    return render_template("authenticated/authenticated_base.html")

@app.route("/login", methods=["GET", "POST"])
def LoginPage():
    ErrorMessage = (False, "")

    if request.method == 'POST':
        UsernameInput = request.form["username"]
        PasswordInput = request.form["password"]

        ErrorMessage = AuthenticationModule.Login(UsernameInput, PasswordInput)

        if ErrorMessage[0]:
            session["user"] = UsernameInput

            User: Record = AuthenticationModule.GetUserRecord(session["user"])

            if GetAttributeValueFromList(User.GetAttributes(), "SetupComplete").Value == 0:
                return redirect("/setup-subjects")

            return redirect("/dashboard")

    return render_template("login.html", ErrorMessage=ErrorMessage[1])

@app.route("/register", methods=["GET", "POST"])
def RegisterPage():
    if "user" in session:
        return redirect("/dashboard")

    ErrorMessage = (False, "")

    if request.method == "POST":
        UsernameInput = request.form["username"]
        PasswordInput = request.form["password"]
        ConfirmedPasswordInput = request.form["confirmed-password"]

        ErrorMessage = AuthenticationModule.Register(UsernameInput, PasswordInput, ConfirmedPasswordInput)

        if ErrorMessage[0]:
            session["user"] = UsernameInput
            return redirect("/login")

    return render_template("register.html", ErrorMessage=ErrorMessage[1])

@app.route('/test', methods=["GET"])
def Test():
    #ProgramDatabase.DeleteRecord("Users", AttributeValue("Username", "", "oofsamy"))
    #session.pop("user", None)
    #print(session)

    #return "test"

    Records = ProgramDatabase.GetAllRecords("Subjects", AttributeValue("Username", "", "dihlan"))

    print(Records[0].GetAttributes())

    return " asda"


@app.route('/logout', methods=["GET"])
def Logout():
    session.pop("user", None)

    return "logged out"

@app.route("/setup-subjects", methods=["GET", "POST"])
def Setup():
    if "user" not in session:
        return redirect("/login")

    User: Record = AuthenticationModule.GetUserRecord(session["user"])
    
    if (GetAttributeValueFromList(User.GetAttributes(), "SetupComplete")).Value == 1:
        return redirect("/dashboard")

    if request.method == "POST":
        SelectedSubjects = request.form.getlist("subject[]")
        SelectedExamBoards = request.form.getlist("exam-board[]")

        SubjectBoardCombinations = []

        for Index in range(len(SelectedSubjects)):
            if f"{SelectedSubjects[Index]}-{SelectedExamBoards[Index]}" in SubjectBoardCombinations:
                return render_template("setup_subjects.html", Subjects = constants.PREDEFINED_SUBJECTS, ExamBoards = constants.PREDEFINED_BOARDS, ErrorMessage = "Subjects cannot be duplicated.")
                
            else:
                SubjectBoardCombinations.append(f"{SelectedSubjects[Index]}-{SelectedExamBoards[Index]}")

        for Index in range(len(SelectedSubjects)):
            ProgramDatabase.CreateRecord("Subjects", PrimaryKey=None, AutoIncrementPrimaryKey=True, Attributes=[
                AttributeValue("SubjectName", "TEXT", SelectedSubjects[Index]),
                AttributeValue("Username", "TEXT", session["user"]),
                AttributeValue("ExamBoard", "TEXT", SelectedExamBoards[Index]),
                AttributeValue("TimeSpent", "INTEGER", 0),
                AttributeValue("LastReviewed", "INTEGER", 0),
                AttributeValue("Priority", "REAL", 0)
            ])

        User.ChangeAttribute("SetupComplete", 1)
        ProgramDatabase.SaveRecord(User)

        return redirect("/dashboard")
    
    return render_template("setup_subjects.html", Subjects = constants.PREDEFINED_SUBJECTS, ExamBoards = constants.PREDEFINED_BOARDS)

@app.route("/", methods=["GET"])
def Index():
    if "user" in session:
        print(session)

        return redirect("/dashboard")

    return render_template("startup.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
