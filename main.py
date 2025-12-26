import Constants as CONSTANTS
from dataclasses import dataclass
import sqlite3
import os

@dataclass
class Attribute:
    Name: str
    Type: str

@dataclass
class ForeignKeyAttribute(Attribute):
    ForeignTable: str
    ForeignName: str

class Record:
    def __init__(self):
        pass

class Database:
    def __init__(self, FileName: str) -> None:
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
                            Attributes=[Attribute("EstablishedDate", "INTEGER")],
                            ForeignKeyAttributes=[ForeignKeyAttribute("ReceiverUsername", "TEXT", "Users", "Username")]) #mention that you changed ReceiverUserID to ReceiverUsername
        
        ### Subjects table is generated in case it doesn't already exist
        self.GenerateTable(TableName="Subjects", PrimaryKey=Attribute("SubjectName", "TEXT"),
                           Attributes=[Attribute("ExamBoard", "TEXT"),
                                       Attribute("TimeSpent", "INTEGER"),
                                       Attribute("LastReviewed", "INTEGER"),
                                       Attribute("Priority", "REAL")])
        
        ### Decks table is generated in case it doesn't already exist
        #mention that upon utilising sqlite, number is not a valid data type
        self.GenerateTable(TableName="Decks", PrimaryKey=Attribute("DeckID", "INTEGER"), 
                           Attributes=[Attribute("DeckName", "TEXT")],
                           ForeignKeyAttributes=[ForeignKeyAttribute("Username", "TEXT", "Users", "Username"),
                                                 ForeignKeyAttribute("Subject", "TEXT", "Subjects", "SubjectName")]) ### also had to change from userid to username here, and subjectID foreign key wasn't right in the NEA design, from SubjectID to just Subject..?

        self.GenerateTable(TableName="Flashcards", PrimaryKey=Attribute("FlashcardID", "INTEGER"),
                           Attributes=[])

        # self.Connection.close() I don't think you should call this until the end of the database usage.

    ### Generates a table within the chosen database file
    ### Required arguments are: TableName and PrimaryKey
    ### Optional arguments are: The list of normal attributes and the list of foreign key attributes
    def GenerateTable(self, TableName: str, PrimaryKey: Attribute, Attributes: list[Attribute] = None, ForeignKeyAttributes: list[ForeignKeyAttribute] = None):
        RecordDefinitions = [f"{PrimaryKey.Name} {PrimaryKey.Type} PRIMARY KEY"]
        ## all collumn definitions must happen before foreign key restraints

        if Attributes != None:
            for Attribute in Attributes:
                RecordDefinitions.append(f"{Attribute.Name} {Attribute.Type}")

        if ForeignKeyAttributes != None:
            for ForeignAttribute in ForeignKeyAttributes:
                RecordDefinitions.append(f"{ForeignAttribute.Name} {ForeignAttribute.Type}")

            for ForeignAttribute in ForeignKeyAttributes:
                RecordDefinitions.append(f"FOREIGN KEY({ForeignAttribute.Name}) REFERENCES {ForeignAttribute.ForeignTable}({ForeignAttribute.ForeignName})")

        RecordString = ",\n".join(RecordDefinitions)
        CommandString = f"CREATE TABLE IF NOT EXISTS {TableName}\n({RecordString})"

        print(CommandString)

        self.Cursor.execute(CommandString)
        self.Connection.commit()

    def GetRecord(self, TableName, Attribute, Value) -> Record:
        if (TableName == "" or Attribute == "" or Value == ""):
            print("Cannot have empty arguments")

            return Record()

        

class AuthenticationModule:
    def __init__():
        pass

    def Login(Username: str, Password: str) -> bool:
        if (Username == ""):
            print("Empty username")

            return False
        
        UserRecord = Database.GetRecord()

        pass

    def Register(Username: str, ) -> bool:
        pass

# class User:
#     def __init__(self, Username, HashedPassword): #wait rethink this, is this gonna be used when the user registers or just when any user object is made?
#         self.UserID = #GeneratePrimaryKey() #idrk how this works in python sql 
#         self.Username = Username 
#         self.HashedPassword = HashedPassword
#         self.Level = CONSTANTS.DEFAULT_LEVEL
#         self.LastActive = Timestamp()
#         self.JoinDate = Timestamp()
#         self.SetupComplete = # 
#         self.Streak = #
#         self.HideActivity = #

ProgramDatabase: Database = None #PDatbase: Database typing

def InitialiseProject():
    os.makedirs("./Data/", exist_ok=True)
    DatabaseFile = open("./Data/ProgramDatabase.db", 'w') # maybe make a new constant, this file path and also another one coz of the global ProgramDatabase variable

def Main():
    InitialiseProject()
        
    ProgramDatabase = Database("./Data/ProgramDatabase.db")

if __name__ == "__main__": # first time running app checks should be made here, such as checking if database.db file exists and blah..
    Main()