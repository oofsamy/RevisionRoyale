### Library Imports

from werkzeug.security import generate_password_hash, check_password_hash
from fsrs import Scheduler, Card, Rating, State
from datetime import datetime, timezone
from dataclasses import dataclass

import constants
import sqlite3
import time
import os

### Dataclass Definitions

@dataclass
class AttributeValue:
    Name: str
    Type: str
    Value: any

@dataclass
class ForeignKeyAttributeValue(AttributeValue):
    ForeignTable: str
    ForeignName: str

### Utility Functions

def ContainsDigits(Text: str):
    for Character in Text:
        if Character.isdigit():
            return True
    return False

def GetAttributeValueFromList(Attributes: list[AttributeValue], Name: str) -> AttributeValue:
    for Attribute in Attributes:
        if Attribute.Name == Name:
            return Attribute

    return None


## Class Definitions

class Record:
    def __init__(self, TableName: str = None, PrimaryKey: AttributeValue = None, Attributes: list[AttributeValue] = None):
        self.TableName = TableName
        self.PrimaryKey = PrimaryKey
        self.Attributes = Attributes

    def IsEmpty(self) -> bool:
        return (self.TableName == "" or self.PrimaryKey == None)

    def GetTableName(self) -> str:
        return self.TableName
    
    def SetTableName(self, TableName: str) -> None:
        self.TableName = TableName

    def GetPrimaryKey(self) -> AttributeValue:
        return self.PrimaryKey
    
    def SetPrimaryKey(self, PrimaryKey: AttributeValue) -> None:
        self.PrimaryKey = PrimaryKey

    def GetAttributes(self) -> list[AttributeValue]:
        return self.Attributes
    
    def AddAttribute(self, Attribute: AttributeValue) -> None:
        self.Attributes.append(Attribute)

    def ChangeAttribute(self, Name: str, Value: any) -> None:
        CurrentAttributes: list[AttributeValue] = self.Attributes
 
        if Name == self.PrimaryKey.Name:
            return

        for Attribute in CurrentAttributes:
            if Attribute.Name == Name:
                Attribute.Value = Value

        self.Attributes = CurrentAttributes

    def GetAttribute(self, Name: str) -> AttributeValue:
        return GetAttributeValueFromList(self.Attributes, Name)
    
    def ConvertToDictionary(self) -> dict:
        ReturnDictionary = {}

        for Attribute in self.GetAttributes():
            ReturnDictionary[Attribute.Name] = Attribute.Value

        ReturnDictionary[self.PrimaryKey.Name] = self.PrimaryKey.Value

        return ReturnDictionary

class Database:
    def __init__(self, FileName: str) -> None:
        self.CreateDatabaseFile(FileName)

        self.Connection = sqlite3.connect(FileName, check_same_thread=False)
        self.Cursor = self.Connection.cursor()

        ### Users table is generated in case it doesn't already exist
        self.GenerateTable(TableName="Users", PrimaryKey=AttributeValue("Username", "TEXT", None),
                           Attributes=[AttributeValue("HashedPassword", "TEXT", None),
                                       AttributeValue("LastActive", "INTEGER", None),
                                       AttributeValue("SetupComplete", "INTEGER", None),
                                       AttributeValue("Streak", "INTEGER", None)])

        ### Subjects table is generated in case it doesn't already exist
        self.GenerateTable(TableName="Subjects", PrimaryKey=AttributeValue("SubjectID", "INTEGER", None),
                           AutoIncrementPrimaryKey=True,
                           Attributes=[AttributeValue("SubjectName", "TEXT", None),
                                       AttributeValue("ExamBoard", "TEXT", None),
                                       AttributeValue("TimeSpent", "INTEGER", None),
                                       AttributeValue("LastReviewed", "INTEGER", None),
                                       AttributeValue("Priority", "REAL", None)],
                            ForeignKeyAttributes=[ForeignKeyAttributeValue("Username", "TEXT", None, "Users", "Username")])

        ### Decks table is generated in case it doesn't already exist
        # mention that upon utilising sqlite, number is not a valid data type
        self.GenerateTable(TableName="Decks", PrimaryKey=AttributeValue("DeckID", "INTEGER", None), AutoIncrementPrimaryKey=True,
                           Attributes=[AttributeValue("DeckName", "TEXT", None)],
                           ForeignKeyAttributes=[ForeignKeyAttributeValue("Username", "TEXT", None, "Users", "Username"),
                                                 ForeignKeyAttributeValue("SubjectID", "TEXT", None, "Subjects", "SubjectID")])

        ### Flashcards table is generated in case it doesn't already exist
        self.GenerateTable(TableName="Flashcards", PrimaryKey=AttributeValue("FlashcardID", "INTEGER", None),
                           AutoIncrementPrimaryKey=True,
                           Attributes=[AttributeValue("FrontContent", "TEXT", None),
                                       AttributeValue("BackContent", "TEXT", None),
                                       AttributeValue("LastReviewed", "INTEGER", None),
                                       AttributeValue("ReviewCount", "INTEGER", None),
                                       AttributeValue("Priority", "INTEGER", None),
                                       AttributeValue("NextDue", "INTEGER", None),
                                       AttributeValue("Difficulty", "REAL", None),
                                       AttributeValue("Stability", "REAL", None)],
                           ForeignKeyAttributes=[ForeignKeyAttributeValue("Username", "TEXT", None, "Users", "Username"),
                                                 ForeignKeyAttributeValue("DeckID", "INTEGER", None, "Decks", "DeckID")])
        
        ### TimetableSlots table is generated in case it doesn't already exist
        self.GenerateTable(TableName="TimetableSlots", PrimaryKey=AttributeValue("TimetableSlotID", "INTEGER", None),
                           AutoIncrementPrimaryKey=True,
                           Attributes=[AttributeValue("PlannedDuration", "INTEGER", None),
                                       AttributeValue("DayOfWeek", "TEXT", None)],
                           ForeignKeyAttributes=[ForeignKeyAttributeValue("DeckID", "INTEGER", None, "Decks", "DeckID")])

        ### Timetable table is generated in case it doesn't already exist
        self.GenerateTable(TableName="Timetable", PrimaryKey=AttributeValue("TimetableID", "INTEGER", None),
                           AutoIncrementPrimaryKey=True,
                           ForeignKeyAttributes=[
                               ForeignKeyAttributeValue("TimetableSlotID", "INTEGER", None, "TimetableSlots", "TimetableSlotID")])
        
    def GetConnection(self):
        return self.Connection
    
    def GetCursor(self):
        return self.Cursor

    ### Generates a table within the chosen database file
    ### Required arguments are: TableName and Primary Key
    ### Optional arguments are: AutoIncrementPrimaryKey, Attributes, ForeignKeyAttributes
    def GenerateTable(self, TableName: str, PrimaryKey: AttributeValue, AutoIncrementPrimaryKey: bool = False, Attributes: list[AttributeValue] = None, ForeignKeyAttributes: list[ForeignKeyAttributeValue] = None) -> None:
        RecordDefinitions: list[str] = []

        if AutoIncrementPrimaryKey == False or PrimaryKey.Type != "INTEGER":
            RecordDefinitions.append(f"{PrimaryKey.Name} {PrimaryKey.Type} PRIMARY KEY")
        else:
            RecordDefinitions.append(f"{PrimaryKey.Name} {PrimaryKey.Type} PRIMARY KEY AUTOINCREMENT")

        if Attributes != None:
            for Attribute in Attributes:  ## Defines normal attributes columns
                RecordDefinitions.append(f"{Attribute.Name} {Attribute.Type}")

        if ForeignKeyAttributes != None:
            for ForeignAttribute in ForeignKeyAttributes:  ## Defines foreign key attributes columns
                RecordDefinitions.append(f"{ForeignAttribute.Name} {ForeignAttribute.Type}")

            for ForeignAttribute in ForeignKeyAttributes:  ## Defines foreign key constraints
                RecordDefinitions.append(
                    f"FOREIGN KEY({ForeignAttribute.Name}) REFERENCES {ForeignAttribute.ForeignTable}({ForeignAttribute.ForeignName})")

        RecordString: str = ",\n".join(RecordDefinitions)
        CommandString: str = f"CREATE TABLE IF NOT EXISTS {TableName}\n({RecordString})"  ## Required in case table already exists

        self.Cursor.execute(CommandString)
        self.Connection.commit()

    def CreateDatabaseFile(self, FileName: str) -> None:
        os.makedirs("./data/", exist_ok=True)  # Makes the folder containing the database file
        if os.path.exists(FileName) == False:  # Checks if the database file doesn't exist before creating a new one
            DatabaseFile = open(FileName, 'w')

    def CreateRecord(self, TableName: str, PrimaryKey: AttributeValue = None, AutoIncrementPrimaryKey: bool = False, Attributes: list[AttributeValue] = None) -> str:  ## AutoIncrement parameter boolean, you also made PrimaryKey an optional thing since it is now
        CommandString = f"INSERT INTO {TableName} ("  ## Required for the SQL statement
        AttributeNames = []
        AttributeValues = []

        if AutoIncrementPrimaryKey == False and PrimaryKey != None:  ## Validates if a primary key actually exists or if AutoIncrement is off
            AttributeNames.append(PrimaryKey.Name)
            AttributeValues.append(f"'{str(PrimaryKey.Value)}'")

        if Attributes != None:
            for Attribute in Attributes:
                AttributeNames.append(Attribute.Name)  # Adds name of the attribute to the list of names
                AttributeValues.append(
                    f"'{str(Attribute.Value)}'")  # Adds the respective value of the attribute to the list of values

        AttributeNamesString = ", ".join(AttributeNames)  # Converts the names array into a string
        AttributeValuesString = ", ".join(AttributeValues)  # Converts the values array into a string

        CommandString = CommandString + AttributeNamesString + ') VALUES\n(' + AttributeValuesString + ');'  # Combines all strings

        try:
            self.Cursor.execute(CommandString)  ## Executes final command
            self.Connection.commit()  ## Commits the change to persistent storage
        except sqlite3.IntegrityError as Error:
            return "Failure to create record, primary key is not unique."
        except sqlite3.OperationalError as Error:
            return "Failure to create record, table does not exist."
        else:
            return "Successfully created record into database."

    def GetRecord(self, TableName: str, Attribute: AttributeValue) -> Record:
        if TableName == "" or Attribute.Name == "" or Attribute.Value == "":
            return Record()
        else:
            NamesString = f"PRAGMA table_info({TableName})"
            self.Cursor.execute(NamesString)

            TableInfo = self.Cursor.fetchall()  ## Returns what the select query returns, or in this case, the PRAGMA macro

            PrimaryKey: AttributeValue = AttributeValue(Name="", Type="", Value=None)  ## Empty Attribute
            PrimaryKeyIndex: int = 0  ## Used to keep track of which attribute is a primary key attribute

            Attributes: list[AttributeValue] = []

            for Index in range(len(TableInfo)):  ## Linear Search
                if TableInfo[Index][5] == 1:
                    PrimaryKeyIndex = Index  ## The 6th entry in each record is a boolean that determines if the attribute is a primary key or not

                Attributes.append(AttributeValue(Name=TableInfo[Index][1], Type=TableInfo[Index][2], Value=None))

            ## Grabs the columns values, as before we only get the attributes names and types, but no values tied.

            try:
                SelectString = f"SELECT * FROM {TableName} WHERE {Attribute.Name} = \"{Attribute.Value}\""
                self.Cursor.execute(SelectString)
            except sqlite3.OperationalError as Error:
                return Record()

            Output = self.Cursor.fetchone()

            if Output is None:  ## Null-checking
                return Record()

            for Index in range(len(Output)):
                if Index == PrimaryKeyIndex:
                    PrimaryKey.Name = Attributes[PrimaryKeyIndex].Name
                    PrimaryKey.Type = Attributes[PrimaryKeyIndex].Type
                    PrimaryKey.Value = Output[Index]
                else:
                    Attributes[Index].Value = Output[Index]

            return Record(TableName=TableName, PrimaryKey=PrimaryKey, Attributes=Attributes)

    def SaveRecord(self, PassedRecord: Record) -> str:
        if PassedRecord is None or PassedRecord.IsEmpty():
            return "Invalid record passed."

        CommandString = f"UPDATE {PassedRecord.GetTableName()} SET\n" ## Begins the SQL command to be executed
        Definitions: list[str] = []
 
        for Attribute in PassedRecord.GetAttributes():
            if Attribute.Name != PassedRecord.GetPrimaryKey().Name: ## Checks if attribute is the primary key attribute
                Definitions.append(f"{Attribute.Name} = \'{Attribute.Value}\'")
                
        CommandString = CommandString + ',\n'.join(Definitions)
        CommandString = CommandString + f'\n WHERE {PassedRecord.GetPrimaryKey().Name} = \'{PassedRecord.GetPrimaryKey().Value}\';'

        try:
            self.Cursor.execute(CommandString)  ## Executes final command
            self.Connection.commit()  ## Commits the change to persistent storage
        except sqlite3.OperationalError as Error:
            return "Failure to create record, table does not exist."
        else:
            return "Successfully created record into database."

    def DeleteRecord(self, TableName: str, PrimaryKey: AttributeValue) -> bool:
        if (TableName == "" or PrimaryKey.Name == "" or PrimaryKey.Value == ""):
            return False
        
        CommandString = f"DELETE FROM {TableName} WHERE {PrimaryKey.Name} = \'{PrimaryKey.Value}\'"

        try:
            self.Cursor.execute(CommandString)  ## Executes final command
            self.Connection.commit()  ## Commits the change to persistent storage
        except sqlite3.OperationalError as Error:
            return "Failure to delete record, table does not exist."
        else:
            return "Successfully deleted record from database."

    def GetAllRecords(self, TableName: str, Attribute: AttributeValue) -> list[Record]:
        if TableName == "" or Attribute.Name == "" or Attribute.Value == "":
            return []

        NamesString: str = f"PRAGMA table_info({TableName})"
        self.Cursor.execute(NamesString)
        TableInfo = self.Cursor.fetchall()

        PrimaryKeyIndex: int = 0
        AttributeTemplate: list[AttributeValue] = []

        for Index in range(len(TableInfo)):
            if TableInfo[Index][5] == 1:
                PrimaryKeyIndex = Index

            AttributeTemplate.append(AttributeValue(Name=TableInfo[Index][1], Type=TableInfo[Index][2], Value=None))

        try:
            SelectString = f"SELECT * FROM {TableName} WHERE {Attribute.Name} = \"{Attribute.Value}\""
            self.Cursor.execute(SelectString)
        except sqlite3.OperationalError as Error:
            return []

        Output = self.Cursor.fetchall()

        if not Output:
            return []

        FinalRecords: list[Record] = []

        for Row in Output:
            RowAttributes: list[AttributeValue] = []
            RowPrimaryKey = None

            for Index in range(len(Row)):
                NewAttribute = AttributeValue(
                    Name=AttributeTemplate[Index].Name,
                    Type=AttributeTemplate[Index].Type,
                    Value=Row[Index]
                )

                if Index == PrimaryKeyIndex:
                    RowPrimaryKey = NewAttribute
                else:
                    RowAttributes.append(NewAttribute)

            NewRecord = Record(PrimaryKey=RowPrimaryKey, Attributes=RowAttributes)
            FinalRecords.append(NewRecord)

        return FinalRecords

    def __del__(self):
        self.Connection.close()

class Authentication:
    def __init__(self, ProgramDatabase: Database):
        self.ProgramDatabase = ProgramDatabase

    def ValidateUsername(self, Username: str) -> bool:
        Length: int = len(Username)

        if (Length < constants.MIN_USERNAME_LENGTH or Length > constants.MAX_USERNAME_LENGTH):
            return False

        if (' ' in Username):
            return False

        UserRecord: Record = self.ProgramDatabase.GetRecord("Users", AttributeValue(Name="Username", Type="", Value=Username.lower()))

        return UserRecord.IsEmpty()

    def ValidatePassword(self, Password: str) -> bool:
        if ((len(Password) < constants.MIN_PASSWORD_LENGTH) or (ContainsDigits(Password) == False)):
            return False

        return True

    def ValidatePasswordWithConfirmation(self, Password: str, ConfirmedPassword: str) -> bool:
        if ((self.ValidatePassword(Password) == False) or (Password != ConfirmedPassword)):
            return False

        return True

    def HashPassword(self, Password: str) -> str:
        return generate_password_hash(Password)

    def VerifyPassword(self, StoredHash: str, UserPassword: str) -> bool:
        return check_password_hash(StoredHash, UserPassword)

    def GetUserRecord(self, Username: str) -> Record:
        return self.ProgramDatabase.GetRecord("Users", AttributeValue("Username", "", Username))

    def Register(self, Username: str, Password: str, ConfirmedPassword: str) -> tuple:
        if (self.ValidateUsername(Username)):
            if (self.ValidatePasswordWithConfirmation(Password, ConfirmedPassword)):
                RecordResult = self.ProgramDatabase.CreateRecord(TableName="Users", PrimaryKey=AttributeValue("Username", "TEXT", Username),
                                                                Attributes=[AttributeValue("HashedPassword", "TEXT", self.HashPassword(Password)),
                                                                            AttributeValue("LastActive", "INTEGER", int(time.time())),
                                                                            AttributeValue("SetupComplete", "INTEGER", 0),
                                                                            AttributeValue("Streak", "INTEGER", 1)])

                if RecordResult == "Successfully created record into database.":
                    return (True, "User successfully registered")
                else:
                    return (False, "User failed to register into database.")
            else:
                return (False, "Password does not meet requirements and/or does not match confirmed password.")
        else:
            return (False, "Username is not valid or already exists.")

    def UpdateStreak(self, UserRecord: Record):
        CurrentTime: int = int(time.time())
        CurrentDayNumber = CurrentTime // 86400 # Dividing the seconds by 86400 (the number of seconds in a day)
        LastDayNumber = UserRecord.GetAttribute("LastActive").Value // 86400 # Dividing the seconds by 86400 (the number of seconds in a day)

        if CurrentDayNumber == LastDayNumber: ## Not a new day login
            pass
        elif CurrentDayNumber == (LastDayNumber + 1): ## If the streak is consecutive by a day
            UserRecord.ChangeAttribute("Streak", UserRecord.GetAttribute("Streak").Value + 1) ## Increments the user's streak
        else: # Streak broken
            UserRecord.ChangeAttribute("Streak", 1) ## Reset the user's streak

        self.ProgramDatabase.SaveRecord(UserRecord)

    def UpdateLastActive(self, UserRecord: Record): 
        UserRecord.ChangeAttribute("LastActive", int(time.time()))
        self.ProgramDatabase.SaveRecord(UserRecord)

    def Login(self, Username: str, Password: str) -> tuple:
        UserRecord: Record = self.ProgramDatabase.GetRecord("Users", AttributeValue(Name="Username", Type="", Value=Username))

        if not UserRecord.IsEmpty():
            PasswordAttribute: AttributeValue = UserRecord.GetAttribute("HashedPassword")

            if (self.VerifyPassword(PasswordAttribute.Value, Password)):
                self.UpdateStreak(UserRecord)
                self.UpdateLastActive(UserRecord)

                return (True, "Successfully logged in.")
            else:
                return (False, "Password is incorrect.")
        else:
            return (False, "User does not exist.")

class SubjectManagement:
    def __init__(self, ProgramDatabase: Database, Authentication: Authentication):
        self.ProgramDatabase = ProgramDatabase
        self.Authentication = Authentication

    def GetDecksFromSubject(self, Subject: Record) -> list[str]:
        DeckID: str = f"{Subject.GetAttribute('SubjectName').Value} : {Subject.GetAttribute('ExamBoard').Value}"

        if DeckID in constants.PREDEFINED_DECKS:
            return constants.PREDEFINED_DECKS[DeckID]
        else:
            return None

    def SetupDecksForSubject(self, Subject: Record):
        Decks = self.GetDecksFromSubject(Subject)

        if Decks is None:
            return

        for Deck in Decks:
            self.ProgramDatabase.CreateRecord("Decks", PrimaryKey = None, AutoIncrementPrimaryKey = True, Attributes = [
                AttributeValue("DeckName", "TEXT", Deck),
                AttributeValue("Username", "TEXT", Subject.GetAttribute('Username').Value),
                AttributeValue("SubjectID", "TEXT", Subject.GetPrimaryKey().Value)
            ])

    def CreateFlashcard(self, FrontContent: str, BackContent: str, Username, DeckID):
        return self.ProgramDatabase.CreateRecord("Flashcards", PrimaryKey = None,
                                          AutoIncrementPrimaryKey = True,
                                          Attributes = [AttributeValue("FrontContent", "TEXT", FrontContent),
                                                        AttributeValue("BackContent", "TEXT", BackContent),
                                                        AttributeValue("LastReviewed", "INTEGER", int(time.time())),
                                                        AttributeValue("ReviewCount", "INTEGER", 0),
                                                        AttributeValue("Priority", "INTEGER", 1),
                                                        AttributeValue("NextDue", "INTEGER", 0),
                                                        AttributeValue("Difficulty", "REAL", 4.0),
                                                        AttributeValue("Stability", "REAL", 1.0),
                                                        AttributeValue("Username", "TEXT", Username),
                                                        AttributeValue("DeckID", "INTEGER", DeckID)])
    
    def HandleReview(self, FlashcardID: int, UserDifficulty: int):
        RatingMap = {
            1: Rating.Again,
            2: Rating.Hard,
            3: Rating.Good,
            4: Rating.Easy
        } ## Mapping the numbers to the ratings

        UserRating = RatingMap.get(UserDifficulty, Rating.Good)

        OldCard = Card() ## Initialisng a card

        FlashcardRecord = self.ProgramDatabase.GetRecord("Flashcards", AttributeValue("FlashcardID", "INTEGER", FlashcardID))

        if FlashcardRecord is None:
            return
        
        FlashcardData = FlashcardRecord.ConvertToDictionary()
        
        if FlashcardData["ReviewCount"] > 0: ## If it has more than 0 reviews, it's not a new card that the user is learning
            OldCard.stability = FlashcardData["Stability"]
            OldCard.difficulty = FlashcardData["Difficulty"]
            OldCard.state = State.Review

            LastReviewDatetime = datetime.fromtimestamp(FlashcardData["LastReviewed"], timezone.utc)
            OldCard.last_review = LastReviewDatetime

        FSRSSchduler = Scheduler()
        NowTime = datetime.now(timezone.utc)

        UpdatedCard, ReviewLog = FSRSSchduler.review_card(OldCard, UserRating)

        ## Saving the new flashcard to the persistent storage

        FlashcardRecord.ChangeAttribute("Difficulty", UpdatedCard.difficulty)
        FlashcardRecord.ChangeAttribute("Stability", UpdatedCard.stability)
        FlashcardRecord.ChangeAttribute("NextDue", int(UpdatedCard.due.timestamp()))
        FlashcardRecord.ChangeAttribute("ReviewCount", FlashcardData["ReviewCount"] + 1)
        FlashcardRecord.ChangeAttribute("LastReviewed", int(NowTime.timestamp()))
        FlashcardRecord.ChangeAttribute("Priority", UserDifficulty)

        self.ProgramDatabase.SaveRecord(FlashcardRecord)

    ## REMEDIAL DEVELOPMENT, DIDNT HAVE '' AROUND FORMAT USERNAME

    def GetUserReviews(self, Username: str):
        Cursor = self.ProgramDatabase.GetCursor()

        Query = f"""
            SELECT 
                SUM(f.ReviewCount) AS total_reviews
            FROM Users u
            JOIN Decks d ON u.Username = d.Username
            JOIN Flashcards f ON d.DeckID = f.DeckID
            WHERE u.Username = \'{Username}\';
        """

        Cursor.execute(Query)
        UserCount = Cursor.fetchone()

        if UserCount[0] is None:
            return 0
        else:
            return UserCount[0]

        return UserCount[0]
    ## Remedial development, LIMIT SPACE

    def GetTopReviews(self, Num: int) -> list:
        Cursor = self.ProgramDatabase.GetCursor()

        Query = f"""
            SELECT u.Username, SUM(f.ReviewCount) AS TotalReviews
            FROM Users u
            JOIN Decks d ON u.Username = d.Username
            JOIN Flashcards f ON d.DeckID = f.DeckID
            GROUP BY u.Username
            ORDER BY TotalReviews DESC
            LIMIT {Num}"""
        
        Cursor.execute(Query)
        TopUsers = Cursor.fetchall()

        return (TopUsers)