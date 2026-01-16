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
    def __init__(self, TableName: str = None, PrimaryKey: AttributeValue = None, Attributes: list[AttributeValue] = None): #will have a primary key attribute I believe, table attribute, 
        self.TableName = TableName
        self.PrimaryKey = PrimaryKey
        self.Attributes = Attributes

    def SetTableName(self, TableName: str) -> None:
        self.TableName = TableName

    def SetPrimaryKey(self, PrimaryKey: AttributeValue) -> None:
        self.PrimaryKey = PrimaryKey

    def AddAttribute(self, Attribute: AttributeValue):
        self.Attributes.append(Attribute)

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
        self.GenerateTable(TableName="Friends", PrimaryKey=Attribute("FriendID", "INTEGER"), AutoIncrementPrimaryKey=True,
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


        #self.CreateRecord("Users", PrimaryKey=AttributeValue("Username", Type=None, Value="oofsamy"), Attributes=[AttributeValue("HashedPassword", Type=None, Value="ExampleHash"),
                                                                                                                  # AttributeValue("Level", Type=None, Value=2),
                                                                                                                  # AttributeValue("LastActive", Type=None, Value=time.time()),
                                                                                                                  # AttributeValue("JoinDate", Type=None, Value=time.time()),
                                                                                                                  # AttributeValue("SetupComplete", Type=None, Value=1),
                                                                                                                  # AttributeValue("Streak", Type=None, Value=1)])

        #MyUser: Record = self.GetRecord(TableName = "Users", Attribute=AttributeValue(Name="Username", Type=None, Value="oofsamy"))
        #MyUser: Record = self.GetRecord(TableName = "", Attribute=AttributeValue(Name = "", Type = "", Value = None))
        #MyUser: Record = self.GetRecord(TableName = "FooBar", Attribute=AttributeValue(Name = "Username", Type = "", Value = "test"))
        MyUser: Record = self.GetRecord(TableName = "Decks", Attribute=AttributeValue(Name = "DeckID", Type = None, Value = "Test"))

        

        print(MyUser.TableName, MyUser.PrimaryKey, MyUser.Attributes)

        # self.Cursor.execute("SELECT * FROM Users;")
        # print(self.Cursor.fetchall())

        #self.GetRecord(TableName="Friends", Attribute="ReceiverUsername", Value="oofsamy")

        #for x in range(21):
        #    print(self.CreateRecord("Friends", AutoIncrementPrimaryKey = True, Attributes=[AttributeValue(Name = "ReceiverUsername", Type=None, Value="spidenix")]))

        #print(self.CreateRecord("Users", PrimaryKey=AttributeValue("Username", Type=None, Value="oofsamy"), Attributes=[AttributeValue("Level", Type=None, Value=4)]))
        #print(self.CreateRecord("Friends", PrimaryKey=AttributeValue("FriendID", Type=None, Value=4), Attributes=[AttributeValue("ReceiverUsername", Type=None, Value="oofsamy")]))
        #print(self.CreateRecord("Friends", PrimaryKey=AttributeValue("FriendID", Type=None, Value=5), Attributes=[AttributeValue("ReceiverUsername", Type=None, Value="asdasd")]))
        #print(self.CreateRecord(TableName="FooBar", PrimaryKey=AttributeValue("ID", Type=None, Value="Test")))
        #print(self.CreateRecord(TableName="Users", Attributes=[AttributeValue("Level", Type=None, Value=4)]))

        # self.Connection.close() I don't think you should call this until the end of the database usage.

    ### Generates a table within the chosen database file
    ### Required arguments are: TableName and PrimaryKey
    ### Optional arguments are: The list of normal attributes and the list of foreign key attributes

    ### maybe think abt autoincrement primary key, requiring a new parameter, will make primarykey an optional parameter for CreateRecord
    def GenerateTableOld(self, TableName: str, PrimaryKey: Attribute, Attributes: list[Attribute] = None, ForeignKeyAttributes: list[ForeignKeyAttribute] = None) -> None:
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

    def GenerateTable(self, TableName: str, PrimaryKey: Attribute, AutoIncrementPrimaryKey: bool = False, Attributes: list[Attribute] = None, ForeignKeyAttributes: list[ForeignKeyAttribute] = None) -> None:
        RecordDefinitions: list[str] = []

        if AutoIncrementPrimaryKey == False or PrimaryKey.Type != "INTEGER":
            RecordDefinitions.append(f"{PrimaryKey.Name} {PrimaryKey.Type} PRIMARY KEY")
        else:
            RecordDefinitions.append(f"{PrimaryKey.Name} {PrimaryKey.Type} PRIMARY KEY AUTOINCREMENT")

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
        os.makedirs("./Data/", exist_ok=True) # Makes the folder containing the database file
        if os.path.exists(FileName) == False: # Checks if the database file doesn't exist before creating a new one
            DatabaseFile = open(FileName, 'w')

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

    def CreateRecord(self, TableName: str, PrimaryKey: AttributeValue = None, AutoIncrementPrimaryKey: bool = False, Attributes: list[AttributeValue] = None) -> str: ## AutoIncrement parameter boolean, you also made PrimaryKey an optional thing since it is now
        CommandString = f"INSERT INTO {TableName} (" ## Required for the SQL statement
        AttributeNames = []
        AttributeValues = []
        
        if AutoIncrementPrimaryKey == False and AttributeValue != None: ## Validates if a primary key actually exists or if AutoIncrement is off
            AttributeNames.append(PrimaryKey.Name)
            AttributeValues.append(f"'{str(PrimaryKey.Value)}'")

        if Attributes != None:
            for Attribute in Attributes:
                AttributeNames.append(Attribute.Name) # Adds name of the attribute to the list of names
                AttributeValues.append(f"'{str(Attribute.Value)}'") # Adds the respective value of the attribute to the list of values
        
        AttributeNamesString = ", ".join(AttributeNames) #Converts the names array into a string
        AttributeValuesString = ", ".join(AttributeValues) #Converts the values array into a string

        CommandString = CommandString + AttributeNamesString + ') VALUES\n(' + AttributeValuesString + ');' # Combines all strings

        try:
            self.Cursor.execute(CommandString) ## Executes final command
            self.Connection.commit() ## Commits the change to persistent storage
        except sqlite3.IntegrityError as Error:
            return "Failure to create record, primary key is not unique."
        except sqlite3.OperationalError as Error:
            return "Failure to create record, table does not exist."
        else:
            return "Successfully created record into database."

    ## remember to remedial develop another stage for the GenerateTable method to return errors instead!!!

    def GetRecord(self, TableName: str, Attribute: AttributeValue) -> Record:
        if TableName == "" or Attribute.Name == "" or Attribute.Value == "":
            return Record()
        else:
            ReturnRecord = Record()

            NamesString = f"PRAGMA table_info({TableName})"
            self.Cursor.execute(NamesString)

            TableInfo = self.Cursor.fetchall() ## Returns what the select query returns, or in this case, the PRAGMA macro

            PrimaryKey: AttributeValue = AttributeValue(Name="", Type="", Value=None) ## Empty Attribute
            PrimaryKeyIndex: int = 0 ## Used to keep track of which attribute is a primary key attribute

            Attributes: list[AttributeValue] = []

            for Index in range(len(TableInfo)): ## Linear Search
                if TableInfo[Index][5] == 1:
                    PrimaryKeyIndex = Index ## The 6th entry in each record is a boolean that determines if the attribute is a primary key or not

                Attributes.append(AttributeValue(Name = TableInfo[Index][1], Type = TableInfo[Index][2], Value = None))

            ## Grabs the columns values, as before we only get the attributes names and types, but no values tied.

            SelectString = f"SELECT * FROM {TableName} WHERE {Attribute.Name} = \"{Attribute.Value}\""
            self.Cursor.execute(SelectString)

            Output = self.Cursor.fetchone()

            for Index in range(len(Output)):
                if Index == PrimaryKeyIndex:
                    PrimaryKey.Name = Attributes[PrimaryKeyIndex].Name
                    PrimaryKey.Type = Attributes[PrimaryKeyIndex].Type
                    PrimaryKey.Value = Output[Index]
                else:
                    Attributes[Index].Value = Output[Index]

            return Record(TableName = TableName, PrimaryKey = PrimaryKey, Attributes=Attributes)

    # def GetRecord(self, TableName, Attribute, Value) -> Record: ## boy, talk about how when testing this function, u realised the database aint saving like at all man, and u only realised via this function.
    #         print("Cannot have empty arguments")

    #         return Record()S

    #     SelectString = f"SELECT * FROM {TableName} WHERE {Attribute}={Value}"

    #     self.Cursor.execute(SelectString)
        
    #     Output = self.Cursor.fetchone()

    #     print(Output)

        ## SELECT * FROM TableName WHERE

    def __del__(self): ## talk about destructor method being added here
        self.Connection.close()

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
    ProgramDatabase = Database(CONSTANTS.DEFAULT_DATABASE_LOCATION)

#This line of code below checks to see if the python script is being run directly (rather than a module)
 # first time running app checks should be made here, such as checking if database.db file exists and blah..
if __name__ == "__main__":
    Main()
