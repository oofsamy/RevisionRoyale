import Constants as CONSTANTS
from dataclasses import dataclass
import sqlite3
import os

import time # have u wrote about importing this in design already??? if not, include it in development!!!

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

class Record:
    def __init__(self): #will have a primary key attribute I believe, table attribute, 
        pass

    #def 

class User(Record): # maybe have a hierarchy chart (maybe even add this post design??) of how everything inherits this base record class to make it serialisable?
    pass

class Database:
    def __init__(self, FileName: str) -> None: ## Constructor method of Database class
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

        ### Flashcards table is generated in case it doesn't already exist
        self.GenerateTable(TableName="Flashcards", PrimaryKey=Attribute("FlashcardID", "INTEGER"),
                           Attributes=[Attribute("FrontContent", "TEXT"),
                                       Attribute("BackContent", "TEXT"),
                                       Attribute("LastReviewed", "INTEGER"),
                                       Attribute("ReviewCount", "INTEGER"),
                                       Attribute("Priority", "INTEGER"),
                                       Attribute("NextDue", "INTEGER"),
                                       Attribute("Difficulty", "REAL"),
                                       Attribute("Stability", "REAL")],
                            ForeignKeyAttributes=[ForeignKeyAttribute("Username", "TEXT", "Users", "Username"), ## changed to username here too
                                                  ForeignKeyAttribute("DeckID", "INTEGER", "Decks", "DeckID")]) 
        
        ### RevisionSessions table is generated in case it doesn't already exist
        self.GenerateTable(TableName="RevisionSessions", PrimaryKey=Attribute("SessionID", "INTEGER"),
                            Attributes=[Attribute("StartTime", "INTEGER"),
                                        Attribute("Duration", "INTEGER"),
                                        Attribute("CardsReviewed", "INTEGER")],
                            ForeignKeyAttributes=[ForeignKeyAttribute("Username", "TEXT", "Users", "Username"), ## changed to username here too
                                                  ForeignKeyAttribute("DeckID", "INTEGER", "Decks", "DeckID"),
                                                  ForeignKeyAttribute("Subject", "TEXT", "Subjects", "SubjectName")])
        
        ### TimetableSlots table is generated in case it doesn't already exist
        self.GenerateTable(TableName="TimetableSlots", PrimaryKey=Attribute("TimetableSlotID", "INTEGER"),
                           Attributes=[Attribute("PlannedDuration", "INTEGER"),
                                       Attribute("DayOfWeek", "TEXT")],
                           ForeignKeyAttributes=[ForeignKeyAttribute("DeckID", "INTEGER", "Decks", "DeckID")])

        ### Timetable table is generated in case it doesn't already exist
        self.GenerateTable(TableName="Timetable", PrimaryKey=Attribute("TimetableID", "INTEGER"),
                           ForeignKeyAttributes=[ForeignKeyAttribute("TimetableSlotID", "INTEGER", "TimetableSlots", "TimetableSlotID")])

        # self.CreateRecord("Users", PrimaryKey=AttributeValue("Username", Type=None, Value="oofsamy"), Attributes=[AttributeValue("HashedPassword", Type=None, Value="ExampleHash"),
        #                                                                                                           AttributeValue("Level", Type=None, Value=2),
        #                                                                                                           AttributeValue("LastActive", Type=None, Value=time.time()),
        #                                                                                                           AttributeValue("JoinDate", Type=None, Value=time.time()),
        #                                                                                                           AttributeValue("SetupComplete", Type=None, Value=1),
        #                                                                                                           AttributeValue("Streak", Type=None, Value=1)])
        
        self.CreateRecord("Users", PrimaryKey=AttributeValue("Username", Type=None, Value="oofsamy"), Attributes=[AttributeValue("Level", Type=None, Value=4)])
        self.CreateRecord("Friends", PrimaryKey=AttributeValue("FriendID", Type=None, Value=4), Attributes=[AttributeValue("ReceiverUsername", Type=None, Value="oofsamy")])
        self.CreateRecord("Friends", PrimaryKey=AttributeValue("FriendID", Type=None, Value=5), Attributes=[AttributeValue("ReceiverUsername", Type=None, Value="asdasd")])
        #self.CreateRecord("FooBar", PrimaryKey=AttributeValue("ID", Type=None, Value="Test"))

        # self.Connection.close() I don't think you should call this until the end of the database usage.

    ### Generates a table within the chosen database file
    ### Required arguments are: TableName and PrimaryKey
    ### Optional arguments are: The list of normal attributes and the list of foreign key attributes

    ### maybe think abt autoincrement primary key, requiring a new parameter, will make primarykey an optional parameter for CreateRecord
    def GenerateTable(self, TableName: str, PrimaryKey: Attribute, Attributes: list[Attribute] = None, ForeignKeyAttributes: list[ForeignKeyAttribute] = None) -> None:
        RecordDefinitions: list[str] = [f"{PrimaryKey.Name} {PrimaryKey.Type} PRIMARY KEY"]

        if Attributes != None:
            for Attribute in Attributes: ## Defines normal attributes columns 
                RecordDefinitions.append(f"{Attribute.Name} {Attribute.Type}")

        if ForeignKeyAttributes != None:
            for ForeignAttribute in ForeignKeyAttributes: ## Defines foreign key attributes columns
                RecordDefinitions.append(f"{ForeignAttribute.Name} {ForeignAttribute.Type}")

            for ForeignAttribute in ForeignKeyAttributes: ## Defines foreign key constraints
                RecordDefinitions.append(f"FOREIGN KEY({ForeignAttribute.Name}) REFERENCES {ForeignAttribute.ForeignTable}({ForeignAttribute.ForeignName})")

        RecordString: str = ",\n".join(RecordDefinitions)
        CommandString: str = f"CREATE TABLE IF NOT EXISTS {TableName}\n({RecordString})" ## Required in case table already exists

        self.Cursor.execute(CommandString)
        self.Connection.commit()

    def CreateDatabaseFile(self, FileName: str) -> None:
        os.makedirs("./Data/", exist_ok=True) # Creates the Data folder to contain the file
        DatabaseFile = open(FileName, 'w') # Creates the ProgramDatabase.db file

    def CreateRecordOld(self, TableName: str, PrimaryKey: AttributeValue, Attributes: list[AttributeValue] = None, ForeignKeyAttributes: list[ForeignKeyAttributeValue] = None) -> None:
        CommandString = f"INSERT INTO {TableName} (" ## Required for the SQL statement
        AttributeNames = [PrimaryKey.Name] #Begins the list of attributes' names
        AttributeValues = [f"'{str(PrimaryKey.Value)}'"] #Begins the list of attributes' values

        for Attribute in Attributes:
            AttributeNames.append(Attribute.Name) # Adds name of the attribute to the list of names
            AttributeValues.append(f"'{str(Attribute.Value)}'") # Adds the respective value of the attribute to the list of values

        AttributeNamesString = ", ".join(AttributeNames) #Converts the array into a string
        AttributeValuesString = ", ".join(AttributeValues) #Converts the array into a string

        CommandString = CommandString + AttributeNamesString + ') VALUES\n(' + AttributeValuesString + ');' # Combines all strings

        self.Cursor.execute(CommandString) ## Commits the change to persistent storage
        self.Connection.commit()
        
        ## do a test where empty primary key
        ## do a test where table doesn't exist
        ## create a test error where an already existign non unique pk entree is made
        ## maybe write about foreignkeyattributes being an unused variable and so its redundant in the remedial dev
        ## do a foreign key test

    def CreateRecord(self, TableName: str, PrimaryKey: AttributeValue, Attributes: list[AttributeValue] = None) -> None:
        CommandString = f"INSERT INTO {TableName} (" ## Required for the SQL statement
        AttributeNames = [PrimaryKey.Name] #Begins the list of attributes' names
        AttributeValues = [f"'{str(PrimaryKey.Value)}'"] #Begins the list of attributes' values

        if Attributes != None:
            for Attribute in Attributes:
                AttributeNames.append(Attribute.Name) # Adds name of the attribute to the list of names
                AttributeValues.append(f"'{str(Attribute.Value)}'") # Adds the respective value of the attribute to the list of values
        
        AttributeNamesString = ", ".join(AttributeNames) #Converts the array into a string
        AttributeValuesString = ", ".join(AttributeValues) #Converts the array into a string

        CommandString = CommandString + AttributeNamesString + ') VALUES\n(' + AttributeValuesString + ');' # Combines all strings

        try:
            self.Cursor.execute(CommandString) ## Commits the change to persistent storage
            self.Connection.commit()
        except sqlite3.IntegrityError as Error:
            print("Failure to create record, primary key is not unique.") ## then talk about how you completely change the function to return the error/success to allow for the ui to utilise the error messages instead of printing, mention how u ran into these when creating the error handling here!!!
        except sqlite3.OperationalError as Error:
            print("Failure to create record, table does not exist.")



    def GetRecord(self, TableName, Attribute, Value) -> Record:
        if (TableName == "" or Attribute == "" or Value == ""):
            print("Cannot have empty arguments")

            return Record()

        SelectString = f"SELECT * FROM {TableName} WHERE {Attribute}={Value}"

        self.Cursor.execute(SelectString)
        
        Output = self.Cursor.fetchone()

        print(Output)

        ## SELECT * FROM TableName WHERE

        

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

def Main():
    ProgramDatabase = Database("./Data/ProgramDatabase.db")

#This line of code below checks to see if the python script is being run directly (rather than a module)
 # first time running app checks should be made here, such as checking if database.db file exists and blah..
if __name__ == "__main__":
    Main()