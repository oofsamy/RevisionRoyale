### Library Imports

from flask import Flask, render_template, request, redirect, session
from dotenv import dotenv_values
from modules import *

import arrow

### Global Variables

app = Flask(__name__)
app.secret_key = dotenv_values(".env")["SECRET_KEY"]

ProgramDatabase = Database(constants.DEFAULT_DATABASE_LOCATION)
AuthenticationModule = Authentication(ProgramDatabase)
SubjectManagementModule = SubjectManagement(ProgramDatabase, AuthenticationModule)
CurrentUser: Record = None

def AuthHandling(Session):
    global CurrentUser

    if "user" not in Session:
        return redirect("/login")

    if CurrentUser is None or CurrentUser.IsEmpty():
        CurrentUser = AuthenticationModule.GetUserRecord(session["user"])

    if CurrentUser is None or CurrentUser.IsEmpty():
        return redirect("/login")
    else:
        AuthenticationModule.UpdateStreak(CurrentUser)
        AuthenticationModule.UpdateLastActive(CurrentUser)

# endpoint for creating a flashcard
@app.route("/flashcard_creation", methods=["GET", "POST"])
def CreateFlashcardEndpoint():
    AuthHandling(session)

    if request.method == 'POST':
        FrontContent = request.form.get("FrontContent")
        BackContent = request.form.get("BackContent")
        DeckID = request.form.get("DeckID")
        SubjectManagementModule.CreateFlashcard(FrontContent, BackContent, session["user"], DeckID)
        return redirect("/flashcard_selection?DeckID="+str(DeckID))
    elif request.method == "GET":
        return render_template("authenticated/subjects/flashcard_creation.html", DeckID=request.args.get('DeckID'))

# endpoint for managing a flashcard
@app.route("/flashcard_management", methods=["GET", "POST"])
def FlashcardManagementPage():
    AuthHandling(session)
 
@app.route("/flashcard_review", methods=["GET", "POST"])
def FlashcardReviewPage():
    AuthHandling(session)
    if request.method == 'POST':
        FlashcardID = request.form["FlashcardID"]
        UserDifficulty = request.form["UserDifficulty"]

        SubjectManagementModule.HandleReview(FlashcardID, UserDifficulty)

        return True
    elif request.method == "GET":
        Mode = request.args.get('mode')
        Decks = request.args.get('DeckID').split(',')
        if Mode == "normal":
            FlashcardsData = []

            for Deck in Decks:
                NewFlashcards = ProgramDatabase.GetAllRecords("Flashcards", AttributeValue("DeckID", "INTEGER", Deck))

                for Flashcard in NewFlashcards:
                    FlashcardsData.append(Flashcard.ConvertToDictionary())

            print(FlashcardsData)

            return render_template("authenticated/subjects/flashcard_review.html", FlashcardsData=FlashcardsData)
        elif Mode == "FSRS":
            FlashcardsData = []

            for Deck in Decks:
                NewFlashcards = ProgramDatabase.GetAllRecords("Flashcards", AttributeValue("DeckID", "INTEGER", Deck))

                for Flashcard in NewFlashcards:
                    if Flashcard.GetAttribute('NextDue').Value <= int(time.time()):
                        FlashcardsData.append(Flashcard.ConvertToDictionary())

            print(FlashcardsData)
            return render_template("authenticated/subjects/flashcard_review.html", FlashcardsData=FlashcardsData)

@app.route("/flashcard_selection", methods=["GET"])
def FlashcardSelectionPage():
    AuthHandling(session)

    Deck = ProgramDatabase.GetRecord("Decks", AttributeValue("DeckID", "INTEGER", request.args.get('DeckID')))

    if Deck is None:
        return redirect("/deck_selection")

    Flashcards = ProgramDatabase.GetAllRecords("Flashcards", AttributeValue("DeckID", "INTEGER", request.args.get('DeckID')))
    FlashcardsData = []

    for Card in Flashcards:
        FlashcardsData.append(Card.ConvertToDictionary())

    return render_template("authenticated/subjects/flashcard_selection.html", ActivePage="dashboard", DeckData=Deck.ConvertToDictionary(), FlashcardsData = FlashcardsData)

@app.route("/deck_selection", methods=["GET"])
def DeckSelectionPage():
    AuthHandling(session)
    
    Subject = ProgramDatabase.GetRecord("Subjects", AttributeValue("SubjectID", "INTEGER", request.args.get('SubjectID')))

    Subject.ChangeAttribute("LastReviewed", int(time.time()))
    ProgramDatabase.SaveRecord(Subject)

    Decks = ProgramDatabase.GetAllRecords("Decks", AttributeValue("SubjectID", "INTEGER", Subject.GetPrimaryKey().Value))
    DecksData = []

    for Deck in Decks:
        DecksData.append(Deck.ConvertToDictionary())

    return render_template("authenticated/subjects/deck_selection.html", ActivePage="dashboard", SubjectName=Subject.GetAttribute('SubjectName').Value, DecksData=DecksData)

@app.route("/dashboard", methods=["GET"])
def DashboardPage():
    AuthHandling(session)

    if CurrentUser is None:
        return redirect("/login")

    if CurrentUser.GetAttribute("SetupComplete").Value == 0:
        return redirect("/setup-subjects")

    SubjectRecords: list[Record] = ProgramDatabase.GetAllRecords("Subjects", AttributeValue("Username", "TEXT", session["user"]))

    if SubjectRecords is None or SubjectRecords == []:
        return redirect('/setup-subjects')

    Subjects = []

    for Subject in SubjectRecords:
        LastReviewed = Subject.GetAttribute("LastReviewed").Value

        if LastReviewed == 0:
            LastReviewed = "Never Reviewed"
        else:
            LastReviewed = arrow.get(LastReviewed).humanize()

        Subjects.append({"SubjectID" : Subject.GetPrimaryKey().Value,
                         "SubjectName": Subject.GetAttribute("SubjectName").Value,
                         "ExamBoard": Subject.GetAttribute("ExamBoard").Value,
                         "LastReviewed": LastReviewed})

    return render_template("authenticated/dashboard.html", ActivePage="dashboard", Subjects=Subjects)

@app.route("/timetable", methods=["GET"])
def TimetablePage():
    AuthHandling(session)

    return render_template("authenticated/timetable.html", ActivePage="timetable")

@app.route("/timer", methods=["GET"])
def TimerPage():
    AuthHandling(session)

    return render_template("authenticated/timer.html", ActivePage="timer")

@app.route("/statistics", methods=["GET"])
def StatisticsPage():
    AuthHandling(session)

    return render_template("authenticated/statistics.html", ActivePage="statistics")

@app.route("/leaderboard", methods=["GET"])
def LeaderboardPage():
    AuthHandling(session)

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

            if User.GetAttribute("SetupComplete").Value == 0:
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
    #b = SubjectManagementModule.CreateFlashcard("What are the factors affecting CPU performance?", "Clock speed, Core count, Cache size", "oofsamy", 14)
    SubjectManagementModule.CreateFlashcard("What is Self-Concept?", "", "oofsamy", 1)
    SubjectManagementModule.CreateFlashcard("What are gross motor skills?", "", "oofsamy", 1)
    SubjectManagementModule.CreateFlashcard("What are fine motor skills?", "", "oofsamy", 1)

    return "sup bro"
    #return "hello bro \n" + b

@app.route('/logout', methods=["GET"])
def Logout():
    session.pop("user", None)

    return redirect("/login")

@app.route("/setup-subjects", methods=["GET", "POST"])
def Setup():
    if "user" not in session:
        return redirect('/login')

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

            SubjectManagementModule.SetupDecksForSubject(ProgramDatabase.GetRecord("Subjects", AttributeValue("SubjectName", "TEXT", SelectedSubjects[Index])))

        User.ChangeAttribute("SetupComplete", 1)
        ProgramDatabase.SaveRecord(User)

        return redirect("/dashboard")
    
    return render_template("setup_subjects.html", Subjects = constants.PREDEFINED_SUBJECTS, ExamBoards = constants.PREDEFINED_BOARDS)

@app.route("/", methods=["GET"])
def Index():
    if "user" in session:
        return redirect("/dashboard")

    return render_template("startup.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
