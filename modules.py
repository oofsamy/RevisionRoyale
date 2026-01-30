### Library Imports

from werkzeug.security import generate_password_hash, check_password_hash
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

class Database:
    def __init__(self, FileName: str) -> None:
        self.CreateDatabaseFile(FileName)

        self.Connection = sqlite3.connect(FileName, check_same_thread=False)
        self.Cursor = self.Connection.cursor()

        ### Users table is generated in case it doesn't already exist
        self.GenerateTable(TableName="Users", PrimaryKey=AttributeValue("Username", "TEXT", None),
                           Attributes=[AttributeValue("HashedPassword", "TEXT", None),
                                       AttributeValue("Level", "REAL", None),
                                       AttributeValue("LastActive", "INTEGER", None),
                                       AttributeValue("JoinDate", "INTEGER", None),
                                       AttributeValue("SetupComplete", "INTEGER", None),
                                       AttributeValue("Streak", "INTEGER", None)])

        ### Friends table is generated in case it doesn't already exist
        self.GenerateTable(TableName="Friends", PrimaryKey=AttributeValue("FriendID", "INTEGER", None),
                           AutoIncrementPrimaryKey=True,
                           Attributes=[AttributeValue("EstablishedDate", "INTEGER", None)],
                           ForeignKeyAttributes=[ForeignKeyAttributeValue("ReceiverUsername", "TEXT", None, "Users", "Username")])

        ### Subjects table is generated in case it doesn't already exist
        self.GenerateTable(TableName="Subjects", PrimaryKey=AttributeValue("SubjectName", "TEXT", None),
                           Attributes=[AttributeValue("ExamBoard", "TEXT", None),
                                       AttributeValue("TimeSpent", "INTEGER", None),
                                       AttributeValue("LastReviewed", "INTEGER", None),
                                       AttributeValue("Priority", "REAL", None)])

        ### Decks table is generated in case it doesn't already exist
        # mention that upon utilising sqlite, number is not a valid data type
        self.GenerateTable(TableName="Decks", PrimaryKey=AttributeValue("DeckID", "INTEGER", None), AutoIncrementPrimaryKey=True,
                           Attributes=[AttributeValue("DeckName", "TEXT", None)],
                           ForeignKeyAttributes=[ForeignKeyAttributeValue("Username", "TEXT", None, "Users", "Username"),
                                                 ForeignKeyAttributeValue("Subject", "TEXT", None, "Subjects", "SubjectName")])

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

        ### RevisionSessions table is generated in case it doesn't already exist
        self.GenerateTable(TableName="RevisionSessions", PrimaryKey=AttributeValue("SessionID", "INTEGER", None),
                           AutoIncrementPrimaryKey=True,
                           Attributes=[AttributeValue("StartTime", "INTEGER", None),
                                       AttributeValue("Duration", "INTEGER", None),
                                       AttributeValue("CardsReviewed", "INTEGER", None)],
                           ForeignKeyAttributes=[ForeignKeyAttributeValue("Username", "TEXT", None, "Users", "Username"),
                                                 ForeignKeyAttributeValue("DeckID", "INTEGER", None, "Decks", "DeckID"),
                                                 ForeignKeyAttributeValue("Subject", "TEXT", None, "Subjects", "SubjectName")])

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

    def SaveRecord(self, PassedRecord: Record) -> str:
        if PassedRecord == None or PassedRecord.IsEmpty():
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

    def __del__(self):
        self.Connection.close()       

class Authentication:
    def __init__(self, ProgramDatabase: Database):
        self.ProgramDatabase = ProgramDatabase

    def ValidateUsername(self, Username: str) -> bool:
        Length: int = len(Username)

        if (Length < 4 or Length > 32):
            return False

        UserRecord: Record = self.ProgramDatabase.GetRecord("Users", AttributeValue(Name="Username", Type="", Value=Username.lower()))

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
                RecordResult = self.ProgramDatabase.CreateRecord(TableName="Users", PrimaryKey=AttributeValue("Username", "TEXT", Username),
                                                                Attributes=[AttributeValue("HashedPassword", "TEXT", self.HashPassword(Password)),
                                                                            AttributeValue("Level", "INTEGER", 1),
                                                                            AttributeValue("LastActive", "INTEGER", int(time.time())),
                                                                            AttributeValue("JoinDate", "INTEGER", int(time.time())),
                                                                            AttributeValue("SetupComplete", "INTEGER", 0),
                                                                            AttributeValue("Streak", "INTEGER", 1)])

                if RecordResult == "Successfully created record into database.":
                    return "User successfully registered"
                else:
                    return "User failed to register into database."
            else:
                return "Password does not meet requirements and/or does not match confirmed password."
        else:
            return "Username is not valid or already exists."

    def UpdateStreak(self, UserRecord: Record):
        CurrentTime: int = int(time.time())
        CurrentDayNumber = CurrentTime // 86400 # Dividing the seconds by 86400 (the number of seconds in a day)
        LastDayNumber = GetAttributeValueFromList(UserRecord.GetAttributes(), "LastActive").Value // 86400 # Dividing the seconds by 86400 (the number of seconds in a day)

        if CurrentDayNumber == LastDayNumber: ## Not a new day login
            pass
        elif CurrentDayNumber == (LastDayNumber + 1): ## If the streak is consecutive by a day
            UserRecord.ChangeAttribute("Streak", GetAttributeValueFromList(UserRecord.GetAttributes(), "Streak").Value + 1) ## Increments the user's streak
        else: # Streak broken
            UserRecord.ChangeAttribute("Streak", 1) ## Reset the user's streak

        self.ProgramDatabase.SaveRecord(UserRecord)

    def UpdateLastActive(self, UserRecord: Record): 
        UserRecord.ChangeAttribute("LastActive", int(time.time()))
        self.ProgramDatabase.SaveRecord(UserRecord)

    def Login(self, Username: str, Password: str) -> bool:
        UserRecord: Record = self.ProgramDatabase.GetRecord("Users", AttributeValue(Name="Username", Type="", Value=Username))

        if not UserRecord.IsEmpty():
            PasswordAttribute: AttributeValue = GetAttributeValueFromList(UserRecord.GetAttributes(), "HashedPassword")

            if (self.VerifyPassword(PasswordAttribute.Value, Password)):
                self.UpdateStreak(UserRecord)
                self.UpdateLastActive(UserRecord)

                return True
            else:
                return False
        else:
            return False
