import getpass
import mysql.connector as mariadb
from mysql.connector import Error

import database.schemacreator as sc_creator
from database.schemacreator import REQUIRED_TABLES

class JERTDatabaseManager:
    def __init__(self):
        self.connection = None
        self.credentials = None

    def userExtractor(self, adminConnection, username):
        cursor = adminConnection.cursor()
        cursor.execute("SELECT EXISTS(SELECT 1 FROM mysql.user WHERE user = %s)", (username,))
        exists = cursor.fetchone()[0] #result of the "exists" query is 0 or 1
        cursor.close()
        return bool(exists)

    def createJERTuser(self, adminConnection, username, password):
        cursor = adminConnection.cursor()
        try:
            cursor.execute(f"CREATE USER %s@'localhost' IDENTIFIED BY %s", (username, password))
            cursor.execute(f"GRANT ALL PRIVILEGES ON *.* TO %s@'localhost' WITH GRANT OPTION", (username,))
            # all priviledges lmao whatever!... rn this user is granted priviledge to ALL ... tables , databases, and stuff... 
            # but we only want them to be working with that one databse they'll use.... but the flow of our program rn is ... check if user exists first,,
            # should the flow be.... create table / see if table exists via admin... then create user with access to only that?
            adminConnection.commit()
            print(f"User '{username}' created successfully.")
        except Error as e:
            print(f"Failed to create user: {e}")
        finally:
            cursor.close()

    def adminConnectionGetter(self):
        print("\n========== Root Login (Required) ==========")
        password = getpass.getpass("Password for root user: ")
        try:
            return mariadb.connect(
                host="localhost",
                user="root",
                password=password
            )
        except Error as e:
            print(f"Root connection failed: {e}")
            return None

    def doesUserExistCheck(self, username):
        adminConnection = self.adminConnectionGetter()
        if not adminConnection:
            print("Cannot proceed without admin access.")
            exit(1) #straight up exit the program
        
        if not self.userExtractor(adminConnection, username): #if user does not exist
            print(f"User '{username}' does not exist.")
            jertPassword = getpass.getpass(f"Set password for about-to-be-created user '{username}': ")
            self.createJERTuser(adminConnection, username, jertPassword)
        adminConnection.close()
        #if jertOrganizationManager exists, then allat is skipped (except for admin)

    def get_db_credentials(self):
        username = "jertOrganizationManager"
        self.doesUserExistCheck(username) #ensure the user exists (or create if needed)

        print("\n==================== Database Login ====================")
        self.credentials = {
            'user': username,
            'password': getpass.getpass(f"Password for '{username}': "), 
            'database': self.validate_db_name() #TODO: see if we need to change this later on to have a fixed database. 
                #but rn it's easier to test if we have this prompt
        }
        return self.credentials

    # ===================

    def validate_db_name(self): 
        while True:
            db_name = input("Database name (required): ").strip()
            if db_name:
                return db_name
            print("Error: Database name cannot be empty. Please try again.")

    def connect(self):
        if not self.credentials:
            self.get_db_credentials()
            
        try: 
            self.connection = mariadb.connect( #blank database connection, just connect it lol
                host= 'localhost',
                user=self.credentials['user'],
                password=self.credentials['password']
            )
            
            cursor = self.connection.cursor()
            cursor.execute(f"SHOW DATABASES LIKE '{self.credentials['database']}'")

            result = cursor.fetchone() 
            if not result: #no database returned
                print(f"Database '{self.credentials['database']}' not found")
                create = input("Create this database? (y/n): ").lower()
            
                if create == 'y':
                    try:
                        cursor.execute(f"CREATE DATABASE {self.credentials['database']}")
                        self.connection.commit()
                        print(f"Database '{self.credentials['database']}' created successfully")
                        
                        # Reconnect to the new database
                        self.connection.close()
                        self.connection = mariadb.connect(
                            host= 'localhost',
                            user=self.credentials['user'],
                            password=self.credentials['password'],
                            database=self.credentials['database']
                        )

                        sc_creator.create_member_table(self.connection)
                        sc_creator.create_student_organization_table(self.connection)
                        sc_creator.create_fee_table(self.connection)
                        sc_creator.create_committee_table(self.connection)
                        sc_creator.create_committee_roles_table(self.connection)
                        sc_creator.create_membership_table(self.connection)
                        sc_creator.create_member_committee_table(self.connection)
                        
                        #other create tables here?

                        self.connection.commit()

                        return self.connection 
                    except Error as e:
                        print(f"Error creating database: {e}")
                        raise
                else:
                    print("Database creation aborted")
                    return None
            
            else: #database found!!! #diva
                self.connection.close()
                print("Database recognized!")
                # print(result)

                self.connection = mariadb.connect(
                    host='localhost',
                    user=self.credentials['user'],
                    password=self.credentials['password'],
                    database=self.credentials['database']
                )

                if not self.is_the_db_valid(self.connection):
                    print("!! Database schema validation failed. Please use a valid database or make a new one. !!")
                    self.connection.close()
                    return None 

                return self.connection
        except Error as e:
            print(f"Database error: {e}")
            self.close_connection()
            return False

    def close_connection(self): 
        if self.connection and self.connection.is_connected(): # close whatever database connection!
            self.connection.close()
            print("Database connection closed.")

    def get_connection(self): #ala getter? yuh
        return self.connection if (self.connection and self.connection.is_connected()) else (None) 
            #none returned if connection (itself) doesnt exist and it isnt connected :p





    def is_the_db_valid(self, connection): #check if db loaded (that alr exists) has the needed tables/cols
        cursor = connection.cursor() 
        try: 
            # ===============TABLES CHECKING===============
            cursor.execute("SHOW TABLES") 
            tables_in_db = cursor.fetchall() # returns tuples [<tablename> , ] of all tables

            # only get the first item in the tuple
            existing_tables = []
            for table_tuple in tables_in_db:
                table_name = table_tuple[0]
                existing_tables.append(table_name)
            
            required_tables = list(REQUIRED_TABLES.keys())
            missing_tables = []

            for table_name in required_tables:
                if table_name not in existing_tables:
                    missing_tables.append(table_name)

            if len(missing_tables) > 0:
                print("Missing tables: " + ", ".join(missing_tables))
                return False
            
            #===============COLUMNS PER TABLE CHECKING===============
            for table, required_columns in REQUIRED_TABLES.items():
                cursor.execute(f"DESCRIBE {table}") #returns tuples AGAIN
                table_columns_in_table = cursor.fetchall()
                existing_columns = []
                for table_column_tuple in table_columns_in_table:
                    column_name = table_column_tuple[0]
                    existing_columns.append(column_name)
                
                missing_columns = []
                for col in required_columns:
                    if col not in existing_columns:
                        missing_columns.append(col)
                
                if missing_columns:
                    print(f"Table '{table}' missing columns: {', '.join(missing_columns)}")
                    cursor.close()
                    return False
            
            print("Database entered is valid for use!")
            cursor.close()
            return True

        except Error as e:
            print(f"Error: {e}")
            cursor.close()
            return False 
        






    # ============================================ STUFF USED BY MAIN =========================

    def get_all_organizations(self): 
        cursor = self.connection.cursor(dictionary=True)
        try: 
            cursor.execute("""
                SELECT organization_id, org_name
                FROM student_organization
                ORDER BY org_name
            """)

            org_list = cursor.fetchall()
            cursor.close()
            return org_list
            
        except Error as e:
            print(f"Database error when fetching all organizations: {e}")
            return []
        finally:  
            cursor.close()

    def get_organization_by_name(self, orgName): 
        cursor = self.connection.cursor(dictionary=True)
        try: 
            cursor.execute("""
                SELECT * FROM student_organization
                WHERE org_name = %s
            """, (orgName,))  
            
            result = cursor.fetchone() #RETURNS A DICTIONARY
            cursor.close()
            return result
            
        except Error as e:
            print(f"Database error when fetching organization by name: {e}")
            return None
            
        finally:
            cursor.close()
    
    def register_organization(self, orgDataDictionary): 
        cursor = self.connection.cursor()
        try:
            sqlStatementString = """
                INSERT INTO student_organization (
                    org_name, 
                    org_type, 
                    semesters_active, 
                    year_established, 
                    abbreviation
                ) VALUES (%s, %s, %s, %s, %s)
            """
            values = (
                orgDataDictionary['name'],
                orgDataDictionary['type'],
                orgDataDictionary['semesters_active'],
                orgDataDictionary['year_established'],
                orgDataDictionary['abbreviation']
            )
            
            cursor.execute(sqlStatementString, values)
            self.connection.commit()
            cursor.close()
            print("Organization registered successfully! == Message from connector.py")
            return True
            
        except Error as e:
            print(f"Registration failed: {e}")
            self.connection.rollback()
            cursor.close()
            return False
    
    def drop_organization(self, orgName):
        cursor = self.connection.cursor()
        try: 
            cursor.execute("SELECT organization_id FROM student_organization WHERE org_name = %s", (orgName,))
            org = cursor.fetchone()
            if org is None:
                return False
            
            org_id = org[0]

            cursor.execute("DELETE FROM membership WHERE organization_id = %s", (org_id,))
            cursor.execute("DELETE FROM student_organization WHERE organization_id = %s", (org_id,))

            self.connection.commit()
            cursor.close()
            return True
        except Exception as e:
            print("Error:", e)
            cursor.close()
            return False
