import getpass
import mysql.connector as mariadb
from mysql.connector import Error

import database.schemacreator as sc_creator
from database.schemacreator import REQUIRED_TABLES

class JERTDatabaseManager:
    def __init__(self):
        self.connection = None
        self.credentials = None
    
    def get_db_name(self):
        while True:
            databaseName = input("Create/Locate a Database (required): ").strip()
            if databaseName:
                return databaseName
            print("Error: Database name cannot be empty. Please try again.")

    def userExtractor(self, adminConnection, username):
        cursor = adminConnection.cursor()
        cursor.execute("SELECT EXISTS(SELECT 1 FROM mysql.user WHERE user = %s)", (username,))
        exists = cursor.fetchone()[0] #result of the "exists" query is 0 or 1
        cursor.close()
        return bool(exists)

    def createJERTuser(self, adminConnection, username, password):
        cursor = adminConnection.cursor()
        try:
            cursor.execute("CREATE USER %s@'localhost' IDENTIFIED BY %s", (username, password))
            adminConnection.commit()
            print(f"\tUser '{username}' created successfully.")
        except Error as e:
            print(f"Failed to create user: {e}")
        finally:
            cursor.close()
    
    def grantJERTuserPermissions(self, adminConnection, username, password, databaseName):
        cursor = adminConnection.cursor()
        try:
            cursor.execute(f"GRANT ALL PRIVILEGES ON {databaseName}.* TO %s@'localhost'", (username,))  # grant access only to specific database
            adminConnection.commit()
            print(f"\tNecessary permissions granted to '{username}' on database '{databaseName}'.")
        except Error as e:
            print(f"Failed to grant permissions: {e}")
        finally:
            cursor.close()

    def adminConnectionGetter(self):
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

    def mariadbGetCredentials(self):
        username = "jertOrganizationManager"
        jertPasswordCredential = ''

        print("\n========== Root & jertOrganizationManager Login ==========")
        print("\tNote: Root user will not be used for the JERT Database. \n\tIt is only for checking if the JERT user exists.")

        adminConnection = self.adminConnectionGetter()
        if not adminConnection:
            print("Cannot proceed without admin access. Possible cause of error: wrong password for 'root'.")
            exit(1)  # straight up exit the program

        if not self.userExtractor(adminConnection, username):  # if user does not exist
            print(f"\tUser '{username}' does not exist.")
            jertPassword = getpass.getpass(f"Set password for about-to-be-created user '{username}': ")
            self.createJERTuser(adminConnection, username, jertPassword)
            jertPasswordCredential = jertPassword
        else :
            jertPasswordCredential = getpass.getpass(f"Password for '{username}': ")
            try:
                testConnection = mariadb.connect(
                    user=username,
                    password=jertPasswordCredential,
                    host="localhost"
                )
                testConnection.close()  # success 
            except mariadb.Error as e:
                print(f"Incorrect password for '{username}'. Exiting program.")
                exit(1)

        print("\n==================== Database Access ====================")
        databaseName = self.get_db_name()  # prompt early so user permissions can be scoped

        self.credentials = {
            'user': username,
            'password': jertPasswordCredential,
            'database': databaseName
        }

        try:

            cursor = adminConnection.cursor()
            cursor.execute(f"SHOW DATABASES LIKE '{self.credentials['database']}'")

            result = cursor.fetchone()
            if not result:  # no database returned
                print(f"\tDatabase '{self.credentials['database']}' not found")
                create = input("Create this database? (y/n): ").lower()

                if create == 'y':
                    try:
                        cursor.execute(f"CREATE DATABASE {self.credentials['database']}")
                        adminConnection.commit()
                        print(f"\tDatabase '{self.credentials['database']}' created successfully")

                        self.grantJERTuserPermissions(adminConnection, username, jertPasswordCredential, databaseName) 
                        newconnection = mariadb.connect(
                            host='localhost',
                            user=self.credentials['user'],
                            password=self.credentials['password'],
                            database=self.credentials['database']
                        )


                        sc_creator.create_member_table(newconnection)
                        sc_creator.create_student_organization_table(newconnection)
                        sc_creator.create_fee_table(newconnection)
                        sc_creator.create_committee_table(newconnection)
                        sc_creator.create_committee_roles_table(newconnection)
                        sc_creator.create_membership_table(newconnection)
                        sc_creator.create_member_committee_table(newconnection)
                        # other create tables here?

                        newconnection.commit() 
                        newconnection.close()

                        self.connection = mariadb.connect(
                            host='localhost',
                            user=self.credentials['user'],
                            password=self.credentials['password'],
                            database=self.credentials['database']
                        )

                        return self.credentials 
                    except Error as e:
                        print(f"Error creating database: {e}")
                        exit(1) #straight up exit #idgaf
                else:
                    print("Database creation aborted")
                    exit(1) #straight up exit #idgaf

            else:  # database found
                # self.connection.close()
                print("\tDatabase recognized!")

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

                # return self.connection
        except Error as e:
            print(f"Database error: {e}")
            self.close_connection()
            return False
        
        adminConnection.close() 

        return self.credentials 

    # ===================

    def first_instructions_explanation(self):
        print("\n==================== Weclome to the JERT Organization Manager System ====================")
        
        print("\tPlease grant root user access to create/check for the jertOrganizationManager account.")

        print("\tYou will be prompted to create your own database or search for your own previously existing database.")
        print("\tIf the database exists and valid for this organization system, it will be used.")
        print("\tIf the database exists and is invalid for this organization system, the program will exit, and please rerun it to try and use a different database.")
        print("\tIf the database does not exist, you will be asked if you want to create it.")

        print('\tjertOrganizationManager will then be given access to only that database.')

    def connect(self):
        self.first_instructions_explanation()
        try: 
            self.mariadbGetCredentials()
            return True
        except Error as e:
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
            
            print("\tDatabase entered is valid for use!")
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
