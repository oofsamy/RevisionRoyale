import Constants as CONSTANTS
from dataclasses import dataclass
import sqlite3
import os

from werkzeug.security import generate_password_hash, check_password_hash

import time  # have u wrote about importing this in design already??? if not, include it in development!!!

@dataclass
class Attribute:
    Name: str
    Type: str


@dataclass
class ForeignKeyAttribute(Attribute):
    ForeignTable: str
    ForeignName: str


@dataclass
class AttributeValue(Attribute):
    Value: any


@dataclass
class ForeignKeyAttributeValue(ForeignKeyAttribute):
    Value: any


class Table:
    def __init__(self):
        pass


def ContainsDigits(String: str):
    for Character in String:
        if Character.isdigit():
            return True

    return False


class Record:
    def __init__(self, TableName: str = None, PrimaryKey: AttributeValue = None,
                 Attributes: list[AttributeValue] = None):
        self.TableName = TableName
        self.PrimaryKey = PrimaryKey
        self.Attributes = Attributes

    def SetTableName(self, TableName: str) -> None:
        self.TableName = TableName

    def SetPrimaryKey(self, PrimaryKey: AttributeValue) -> None:
        self.PrimaryKey = PrimaryKey

    def AddAttribute(self, Attribute: AttributeValue) -> None:
        self.Attributes.append(Attribute)

    def IsEmpty(self) -> bool:
        return (self.TableName == "" or self.TableName == None or self.PrimaryKey == None)
        ## A valid record will have a Table and a PrimaryKey, if not, it is not valid

    def GetAttributes(self) -> list[AttributeValue]:
        return self.Attributes

    def ChangeAttribute(self, Name: str, Value: any) -> None:## -> bool:
        for Attribute in self.Attributes:
            if Attribute.Name == Name:
                Attribute.Value = Value




class Database:
    def __init__(self, FileName: str) -> None:  ## Constructor method of Database class
        self.CreateDatabaseFile(FileName)

        self.Connection = sqlite3.connect(FileName)
        self.Cursor = self.Connection.cursor()

        ### Users table is generated in case it doesn't already exist
        self.GenerateTable(TableName="Users", PrimaryKey=Attribute("Username", "TEXT"),
                           Attributes=[Attribute("HashedPassword", "TEXT"),
                                       Attribute("Level", "REAL"),
                                       Attribute("LastActive", "INTEGER"),
                                       Attribute("JoinDate", "INTEGER"),
                                       Attribute("SetupComplete", "INTEGER"),
                                       Attribute("Streak", "INTEGER")])

        ### Friends table is generated in case it doesn't already exist
        self.GenerateTable(TableName="Friends", PrimaryKey=Attribute("FriendID", "INTEGER"),
                           AutoIncrementPrimaryKey=True,
                           Attributes=[Attribute("EstablishedDate", "INTEGER")],
                           ForeignKeyAttributes=[ForeignKeyAttribute("ReceiverUsername", "TEXT", "Users", "Username")])

        ### Subjects table is generated in case it doesn't already exist
        self.GenerateTable(TableName="Subjects", PrimaryKey=Attribute("SubjectName", "TEXT"),
                           Attributes=[Attribute("ExamBoard", "TEXT"),
                                       Attribute("TimeSpent", "INTEGER"),
                                       Attribute("LastReviewed", "INTEGER"),
                                       Attribute("Priority", "REAL")])

        ### Decks table is generated in case it doesn't already exist
        # mention that upon utilising sqlite, number is not a valid data type
        self.GenerateTable(TableName="Decks", PrimaryKey=Attribute("DeckID", "INTEGER"), AutoIncrementPrimaryKey=True,
                           Attributes=[Attribute("DeckName", "TEXT")],
                           ForeignKeyAttributes=[ForeignKeyAttribute("Username", "TEXT", "Users", "Username"),
                                                 ForeignKeyAttribute("Subject", "TEXT", "Subjects", "SubjectName")])

        ### Flashcards table is generated in case it doesn't already exist
        self.GenerateTable(TableName="Flashcards", PrimaryKey=Attribute("FlashcardID", "INTEGER"),
                           AutoIncrementPrimaryKey=True,
                           Attributes=[Attribute("FrontContent", "TEXT"),
                                       Attribute("BackContent", "TEXT"),
                                       Attribute("LastReviewed", "INTEGER"),
                                       Attribute("ReviewCount", "INTEGER"),
                                       Attribute("Priority", "INTEGER"),
                                       Attribute("NextDue", "INTEGER"),
                                       Attribute("Difficulty", "REAL"),
                                       Attribute("Stability", "REAL")],
                           ForeignKeyAttributes=[ForeignKeyAttribute("Username", "TEXT", "Users", "Username"),
                                                 ForeignKeyAttribute("DeckID", "INTEGER", "Decks", "DeckID")])

        ### RevisionSessions table is generated in case it doesn't already exist
        self.GenerateTable(TableName="RevisionSessions", PrimaryKey=Attribute("SessionID", "INTEGER"),
                           AutoIncrementPrimaryKey=True,
                           Attributes=[Attribute("StartTime", "INTEGER"),
                                       Attribute("Duration", "INTEGER"),
                                       Attribute("CardsReviewed", "INTEGER")],
                           ForeignKeyAttributes=[ForeignKeyAttribute("Username", "TEXT", "Users", "Username"),
                                                 ForeignKeyAttribute("DeckID", "INTEGER", "Decks", "DeckID"),
                                                 ForeignKeyAttribute("Subject", "TEXT", "Subjects", "SubjectName")])

        ### TimetableSlots table is generated in case it doesn't already exist
        self.GenerateTable(TableName="TimetableSlots", PrimaryKey=Attribute("TimetableSlotID", "INTEGER"),
                           AutoIncrementPrimaryKey=True,
                           Attributes=[Attribute("PlannedDuration", "INTEGER"),
                                       Attribute("DayOfWeek", "TEXT")],
                           ForeignKeyAttributes=[ForeignKeyAttribute("DeckID", "INTEGER", "Decks", "DeckID")])

        ### Timetable table is generated in case it doesn't already exist
        self.GenerateTable(TableName="Timetable", PrimaryKey=Attribute("TimetableID", "INTEGER"),
                           AutoIncrementPrimaryKey=True,
                           ForeignKeyAttributes=[
                               ForeignKeyAttribute("TimetableSlotID", "INTEGER", "TimetableSlots", "TimetableSlotID")])

    ### Generates a table within the chosen database file
    ### Required arguments are: TableName and Primary Key
    ### Optional arguments are: AutoIncrementPrimaryKey, Attributes, ForeignKeyAttributes
    def GenerateTable(self, TableName: str, PrimaryKey: Attribute, AutoIncrementPrimaryKey: bool = False,
                      Attributes: list[Attribute] = None,
                      ForeignKeyAttributes: list[ForeignKeyAttribute] = None) -> None:
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
        os.makedirs("./Data/", exist_ok=True)  # Makes the folder containing the database file
        if os.path.exists(FileName) == False:  # Checks if the database file doesn't exist before creating a new one
            DatabaseFile = open(FileName, 'w')

    def CreateRecord(self, TableName: str, PrimaryKey: AttributeValue = None, AutoIncrementPrimaryKey: bool = False,
                     Attributes: list[
                         AttributeValue] = None) -> str:  ## AutoIncrement parameter boolean, you also made PrimaryKey an optional thing since it is now
        CommandString = f"INSERT INTO {TableName} ("  ## Required for the SQL statement
        AttributeNames = []
        AttributeValues = []

        if AutoIncrementPrimaryKey == False and AttributeValue != None:  ## Validates if a primary key actually exists or if AutoIncrement is off
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

            if Output == None:  ## Null-checking
                return Record()

            for Index in range(len(Output)):
                if Index == PrimaryKeyIndex:
                    PrimaryKey.Name = Attributes[PrimaryKeyIndex].Name
                    PrimaryKey.Type = Attributes[PrimaryKeyIndex].Type
                    PrimaryKey.Value = Output[Index]
                else:
                    Attributes[Index].Value = Output[Index]

            return Record(TableName=TableName, PrimaryKey=PrimaryKey, Attributes=Attributes)

    ## make it so it saves every changed attribute in the database model, add this to the database module writeup as a new function entirely, remedial develop from updatelastactive, you're gonna have to make a seperate function for that holy shit

    def ChangeAttribute(self, TableName: str, PrimaryKey: AttributeValue, NewAttribute: AttributeValue):

    def __del__(self):
        self.Connection.close()


## Mention lowercase and uppercase usernames, case sensitive
## Change to more efficient code, return not UserRecord.IsEmpty()
## Mention how usernames will be saved as lower case

class Authentication:
    def __init__(self, ProgramDatabase: Database):
        self.ProgramDatabase = ProgramDatabase

    def ValidateUsername(self, Username: str) -> bool:
        Length: int = len(Username)

        if (Length < 4 or Length > 32):
            return False

        UserRecord: Record = self.ProgramDatabase.GetRecord("Users", AttributeValue(Name="Username", Type="",
                                                                                    Value=Username.lower()))

        return UserRecord.IsEmpty()

    def ValidatePassword(self, Password: str) -> bool:
        if ((len(Password) < 8) or (ContainsDigits(Password) == False)):
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

    def Register(self, Username: str, Password: str, ConfirmedPassword: str) -> str:
        if (self.ValidateUsername(Username)):
            if (self.ValidatePasswordWithConfirmation(Password, ConfirmedPassword)):
                RecordResult = self.ProgramDatabase.CreateRecord(TableName="Users",
                                                             PrimaryKey=AttributeValue("Username", "TEXT", Username),
                                                             Attributes=[
                                                                 AttributeValue("HashedPassword", "TEXT",
                                                                                self.HashPassword(Password)),
                                                                 AttributeValue("Level", "INTEGER", 1),
                                                                 AttributeValue("LastActive", "INTEGER",
                                                                                int(time.time())),
                                                                 AttributeValue("JoinDate", "INTEGER",
                                                                                int(time.time())),
                                                                 AttributeValue("SetupComplete", "INTEGER", 0),
                                                                 AttributeValue("Streak", "INTEGER", 1)
                                                             ])

                if RecordResult == "Successfully created record into database.":
                    return "User successfully registered"
                else:
                    return "User failed to register into database."
            else:
                return "Password does not meet requirements and/or does not match confirmed password."
        else:
            return "Username is not valid or already exists."

    # Potential remedial development, i need to change the last active date whenever they login, but i havent even got that in the database module let alone the auth module, so i could remedial for both and mention the database remedial in the user remedial!!

    def UpdateStreak(self, UserRecord: Record) -> int:
        pass

    def UpdateLastActive(self, UserRecord: Record) -> int:
        UserRecord.ChangeAttribute("LastActive", int(time.time()))

    def Login(self, Username: str, Password: str) -> bool:
        UserRecord: Record = self.ProgramDatabase.GetRecord("Users", AttributeValue(Name="Username", Type="", Value=Username))

        if not UserRecord.IsEmpty():
            PasswordAttribute: AttributeValue = GetAttributeValueFromList(UserRecord.GetAttributes(), "HashedPassword")

            if (self.VerifyPassword(PasswordAttribute.Value, Password)):
                self.UpdateLastActive(UserRecord)

                return True
            else:
                return False
        else:
            return False

def GetAttributeValueFromList(Attributes: list[AttributeValue], Name: str) -> AttributeValue:
    for Attribute in Attributes:
        if Attribute.Name == Name:
            return Attribute

    return None


class User:
    def __init__(self, Username: str, AuthModule: Authentication):
        self.AuthModule: Authentication = AuthModule
        self.Initialised: bool = False

        UserRecord: Record = self.GetUserRecord(Username)
        UserAttributes: list[AttributeValue] = UserRecord.GetAttributes()

        if Record.IsEmpty() == False:
            self.Initialised = True
            self.Username = Username
            self.HashedPassword = GetAttributeValueFromList(UserAttributes,
                                                            "HashedPassword")  ### COULD BE A HUGE REMEDIAL DEVELOPMENT, MAYBE THE LIST OF ATTRIBUTES IS ALREADY IN ORDER?????
            self.Level = GetAttributeValueFromList(UserAttributes, "Level")
            self.LastActive = GetAttributeValueFromList(UserAttributes, "LastActive")
            self.JoinDate = GetAttributeValueFromList(UserAttributes, "JoinDate")
            self.SetupComplete = GetAttributeValueFromList(UserAttributes, "SetupComplete")
            self.Streak = GetAttributeValueFromList(UserAttributes, "Streak")

    def GetUserRecord(self, Username: str):
        UserRecord: Record = self.AuthModule.ProgramDatabase.GetRecord("Users",
                                                                       AttributeValue("Username", "TEXT", Username))

        return Record


def Main():
    ProgramDatabase = Database(CONSTANTS.DEFAULT_DATABASE_LOCATION)
    AuthenticationModule = Authentication(ProgramDatabase)

    #AuthenticationModule.Register("oofsamy", "MyPassword123", "MyPassword123")
    AuthenticationModule.Login("oofsamy", "MyPassword123")

if __name__ == "__main__":
    Main()
