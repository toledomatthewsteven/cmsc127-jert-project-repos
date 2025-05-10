import getpass
import mysql.connector as mariadb
from mysql.connector import Error

import database.schemacreator as sc_creator

class JERTDatabaseManager:
    def __init__(self):
        self.connection = None
        self.credentials = None

    def get_db_credentials(self): 
        print("\n==================== Database Login ====================")
        self.credentials = {
            'user': input("Username (default: root): ") or "root",
            'password': getpass.getpass("Password: "),
            'host': input("Host (default: localhost): ") or "localhost",
            'database': self.validate_db_name()
        }
        return self.credentials

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
                host=self.credentials['host'],
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
                            host=self.credentials['host'],
                            user=self.credentials['user'],
                            password=self.credentials['password'],
                            database=self.credentials['database']
                        )

                        sc_creator.create_member_table(self.connection)
                        sc_creator.create_student_organization_table(self.connection)
                        sc_creator.create_fee_table(self.connection)
                        
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
                print(result)

                self.connection = mariadb.connect(
                    host=self.credentials['host'],
                    user=self.credentials['user'],
                    password=self.credentials['password'],
                    database=self.credentials['database']
                )

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


    #TODO: CREATE SCHEMAS AND SHIT......

    def create_member_table(self):
        cursor = self.connection.cursor()
        cursor.execute("""
            CREATE TABLE member (
                first_name VARCHAR(15) NOT NULL,
                middle_name VARCHAR(15),
                last_name VARCHAR(25) NOT NULL,
                student_number CHAR(10) PRIMARY KEY NOT NULL,
                degree_program VARCHAR(30) NOT NULL,
                gender CHAR(1) NOT NULL,
                graduation_status BOOLEAN DEFAULT 0,
                graduation_date DATE
            )
            """) # triple quotation marks enclosing a string can help make it readable via multiple lines
        print("Created member schema in new database!")

    