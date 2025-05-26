import datetime
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
        print("You must enter a database name to create or use. If you forgot the database name you use, please consult your organization's documentation team.")
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
                    exit(1) #straight up exit #idgaf

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
    # ============================================ STUFF USED BY MAIN =========================
    # ============================================ STUFF USED BY MAIN =========================
    # ============================================ STUFF USED BY MAIN =========================
    # ============================================ STUFF USED BY MAIN =========================
    # ============================================ STUFF USED BY MAIN =========================
    # ============================================ STUFF USED BY MAIN =========================

    
    # ============================================ GETTERS =========================
    # ============================================ GETTERS =========================
    # ============================================ GETTERS =========================
    # ============================================ GETTERS =========================
    # ============================================ GETTERS =========================

    def get_all_organizations(self):  #damn how'd this get lost in the commits
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

    def get_member_committee_history(self, student_number, orgID):
        cursor = self.connection.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT committee_name, committee_role, academic_year, semester, membership_status
                FROM member_committee
                WHERE student_number = %s AND committee_name IN (
                    SELECT committee_name FROM committee WHERE organization_id = %s
                )
                ORDER BY academic_year DESC, semester DESC
            """, (student_number, orgID))
            return cursor.fetchall()
        except Error as e:
            print(f"Database error fetching committee history for student: {e}")
            return []
        finally:
            cursor.close()

    def get_membership_record(self, student_number, orgID):
        cursor = self.connection.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT student_number, organization_id, batch_year, join_date
                FROM membership
                WHERE student_number = %s AND organization_id = %s
            """, (student_number, orgID))
            
            record = cursor.fetchone()  # fetch one record or None if not found
            return record

        except Error as e:
            print(f"Database error fetching membership record: {e}")
            return None

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

    
        
    def get_or_check_studentNumber_in_Membership(self, student_number, orgID, orgName):
        cursor = self.connection.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT * FROM membership
                WHERE student_number = %s AND organization_id = %s
            """, (student_number, orgID))
            
            record = cursor.fetchone()
            
            if record:
                # print(f"Warning: Student '{student_number}' is already a member of organization '{orgName}'.")
                return True 
            else:
                return False 
            
        except Error as e:
            print(f"Database error when checking membership: {e}")
            return None

        finally:
            cursor.close()

        
    def get_student_record_by_studentNumber(self, studentnumberInput): 
        cursor = self.connection.cursor(dictionary=True)
        try: 
            cursor.execute("""
                SELECT * FROM member
                WHERE student_number = %s
            """, (studentnumberInput,))  
            
            result = cursor.fetchone() #RETURNS A DICTIONARY
            cursor.close()
            return result
            
        except Error as e:
            print(f"Database error when fetching student record by student id: {e}")
            return None
            
        finally:
            cursor.close()

    def get_committees_by_orgID(self, orgID):
        cursor = self.connection.cursor(dictionary=True)
        try: 
            cursor.execute("""
                SELECT * FROM committee
                WHERE organization_id = %s
            """, (orgID, ))  
            
            results = cursor.fetchall()  # fetch all rows as list of dictionaries
            return results  # return the list of dictionaries
            
        except Error as e:
            print(f"Database error when fetching committees by orgID: {e}")
            return None
            
        finally:
            cursor.close()

    def get_committees_and_roles_by_orgID(self, orgID):
        cursor = self.connection.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT c.committee_name, r.committee_role
                FROM committee c
                LEFT JOIN committee_roles r 
                    ON c.committee_name = r.committee_name AND c.organization_id = r.organization_id
                WHERE c.organization_id = %s
            """, (orgID,))
            
            results = cursor.fetchall()  # list of dicts with keys 'committee_name', 'committee_role'
            return results

        except Error as e:
            print(f"Database error when fetching committees and roles: {e}")
            return None

        finally:
            cursor.close()



    def get_committees_by_orgID_with_roles(self, orgID):
        cursor = self.connection.cursor(dictionary=True)
        try:
            # Fetch all committees for the given organization
            cursor.execute("""
                SELECT * FROM committee
                WHERE organization_id = %s
            """, (orgID,))
            
            committees = cursor.fetchall()  # list of dicts
            
            # If no committees found, return empty list
            if not committees:
                return []
            
            # Fetch all roles for these committees using organization_id
            cursor.execute("""
                SELECT * FROM committee_roles
                WHERE organization_id = %s
            """, (orgID,))
            
            roles = cursor.fetchall()  # list of dicts
            
            # Organize roles by (committee_name, organization_id)
            role_map = {}
            for role in roles:
                comm_key = (role['committee_name'], role['organization_id'])
                if comm_key not in role_map:
                    role_map[comm_key] = []
                role_map[comm_key].append(role['committee_role'])
            
            # Add roles list to each committee dictionary
            for committee in committees:
                comm_key = (committee['committee_name'], committee['organization_id'])
                committee['roles'] = role_map.get(comm_key, [])
            
            return committees  # list of committee dicts with 'roles' key

        except Error as e:
            print(f"Database error when fetching committees and roles by orgID: {e}")
            return None
        
        finally:
            cursor.close()

    
    def get_fees(self, orgID):
        cursor = self.connection.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT *
                FROM fee
                ORDER BY payment_date
            """)

            feelist = cursor.fetchall()
            cursor.close()
            return feelist
            
        except Error as e:
            print(f"Database error when fetching all fees: {e}")
            return []
        finally:  
            cursor.close()


    # ============================================ REGISTRATIONS =========================
    # ============================================ REGISTRATIONS =========================
    # ============================================ REGISTRATIONS =========================
    # ============================================ REGISTRATIONS =========================
    # ============================================ REGISTRATIONS =========================
    # ============================================ REGISTRATIONS =========================
    # ============================================ REGISTRATIONS =========================
    
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
            print(f"\tRegistration failed: {e}")
            self.connection.rollback()
            cursor.close()
            return False
    

    def register_member_under_committee_with_role(self, student_number, orgID, committeeName, roleName, academic_year, semester, membership_status):
        cursor = self.connection.cursor()
        try:
            # Double check committee existence for orgID
            cursor.execute("""
                SELECT * FROM committee
                WHERE committee_name = %s AND organization_id = %s
            """, (committeeName, orgID))
            committee = cursor.fetchone()
            if not committee:
                print(f"Error: Committee '{committeeName}' does not exist under organization ID {orgID}.")
                return False

            # Double check role existence in committee
            cursor.execute("""
                SELECT * FROM committee_roles
                WHERE committee_name = %s AND committee_role = %s
            """, (committeeName, roleName))
            role = cursor.fetchone()
            if not role:
                print(f"Error: Role '{roleName}' does not exist under committee '{committeeName}'.")
                return False

            # Insert into member_committee proper
            cursor.execute("""
                INSERT INTO member_committee (student_number, committee_name, academic_year, semester, membership_status, committee_role)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (student_number, committeeName, academic_year, semester, membership_status, roleName))

            self.connection.commit()
            # print(f"Member '{student_number}' registered in committee '{committeeName}' with role '{roleName}' for {academic_year} {semester} ({membership_status}).")
            return True

        except Error as e:
            print(f"Database error during member registration under committee and role: {e}")
            self.connection.rollback()
            return False

        finally:
            cursor.close()
    
    def register_membership(self, student_number, organization_id, batch_year, join_date=None):
        cursor = self.connection.cursor()
        try:
            sql = """
                INSERT INTO membership (student_number, organization_id, batch_year, join_date)
                VALUES (%s, %s, %s, %s)
            """
            if join_date is None:
                join_date = datetime.date.today()  # default to today's date
            values = (student_number, organization_id, batch_year, join_date)
            cursor.execute(sql, values)
            self.connection.commit()
            cursor.close()
            return True
        except Error as e:
            print(f"Failed to register membership: {e}")
            self.connection.rollback()
            cursor.close()
            return False




    
    def register_committee_with_roles(self, committeeData): 
        # committeeData = {
        #     'committee_name': str,
        #     'organization_id': int,
        #     'roles': list of str
        # } 

        cursor = self.connection.cursor()
        try:
            cursor.execute(
                "SELECT COUNT(*) FROM committee WHERE committee_name = %s AND organization_id = %s", 
                (committeeData['committee_name'], committeeData['organization_id'])
            )  # Check if committee already exists

            if cursor.fetchone()[0] > 0:
                print(f"Committee '{committeeData['committee_name']}' already exists for this organization.")
                cursor.close()
                return False

            # Insert into committee table
            sql_committee = """
                INSERT INTO committee (committee_name, organization_id)
                VALUES (%s, %s)
            """
            cursor.execute(sql_committee, (committeeData['committee_name'], committeeData['organization_id']))

            # Updated: Insert roles into committee_roles with organization_id
            sql_role_exists = """
                SELECT COUNT(*) FROM committee_roles 
                WHERE committee_name = %s AND committee_role = %s AND organization_id = %s
            """
            sql_insert_role = """
                INSERT INTO committee_roles (committee_role, committee_name, organization_id)
                VALUES (%s, %s, %s)
            """
            for role in committeeData['roles']:
                cursor.execute(sql_role_exists, (committeeData['committee_name'], role, committeeData['organization_id']))
                if cursor.fetchone()[0] == 0:
                    cursor.execute(sql_insert_role, (role, committeeData['committee_name'], committeeData['organization_id']))
                else:
                    print(f"Role '{role}' already exists in committee '{committeeData['committee_name']}' for organization {committeeData['organization_id']}, skipping insertion.")

            self.connection.commit()
            cursor.close()
            return True

        except Error as e:
            print(f"Failed to register committee and roles: {e}")
            self.connection.rollback()
            cursor.close()
            return False


    
    def register_new_studentRecord(self, memberDataDictionary): 
        cursor = self.connection.cursor()
        try:
            sqlStatementString = """
                INSERT INTO member (
                    first_name, 
                    middle_name, 
                    last_name, 
                    student_number, 
                    degree_program, 
                    gender, 
                    graduation_status, 
                    graduation_date
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            values = (
                memberDataDictionary['first_name'],
                memberDataDictionary['middle_name'],
                memberDataDictionary['last_name'],
                memberDataDictionary['student_number'],
                memberDataDictionary['degree_program'],
                memberDataDictionary['gender'],
                memberDataDictionary['graduation_status'],
                memberDataDictionary['graduation_date']
            )
            
            cursor.execute(sqlStatementString, values)
            self.connection.commit()
            cursor.close() 
            return True
            
        except Error as e:
            print(f"\tRegistration failed: {e}")
            self.connection.rollback()
            cursor.close()
            return False
        

    # ============================================ FEE SEPARATOR====================

     
    def register_new_feeRecord(self, feeDataDictionary): 
        cursor = self.connection.cursor()
        try:
            sqlStatementString = """
                INSERT INTO fee (
                    amount,
                    due_date,
                    semester,
                    academic_year,
                    student_number,
                    organization_id
                ) VALUES (%s, %s, %s, %s, %s, %s)
            """
            values = (
                feeDataDictionary['amount'],
                feeDataDictionary['due_date'],
                feeDataDictionary['semester'],
                feeDataDictionary['academic_year'],
                feeDataDictionary['student_number'],
                feeDataDictionary['organization_id']
            )
            
            cursor.execute(sqlStatementString, values)
            self.connection.commit()
            cursor.close() 
            return True
            
        except Error as e:
            print(f"\tRegistration failed: {e}")
            self.connection.rollback()
            cursor.close()
            return False
    # ============================================ DROPPERS =========================
    # ============================================ DROPPERS =========================
    # ============================================ DROPPERS =========================
    # ============================================ DROPPERS =========================
    # ============================================ DROPPERS =========================

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
    
    # ============================================ UPDATERS ============================================
    # ============================================ UPDATERS ============================================
    # ============================================ UPDATERS ============================================
    # ============================================ UPDATERS ============================================
    # ============================================ UPDATERS ============================================

    def update_existing_committee_log(self, student_number, orgID, assigned_committee, assigned_role, academic_year, semester, membership_status):
        cursor = self.connection.cursor()
        try:
            # Update only committee_name, committee_role, membership_status for the matching student_number, academic_year, semester
            sql = """
                UPDATE member_committee
                SET committee_name = %s,
                    committee_role = %s,
                    membership_status = %s
                WHERE student_number = %s
                AND academic_year = %s
                AND semester = %s
            """
            cursor.execute(sql, (assigned_committee, assigned_role, membership_status, student_number, academic_year, semester))
            self.connection.commit()
            
            if cursor.rowcount == 0:
                print("\tNo matching record found to update.") #not rlly gonna be reached but, just in case.
                return False
            return True
        except Error as e:
            print(f"Database error when updating committee log: {e}")
            return False
        finally:
            cursor.close()


    # ============================================ REPORT GENERATORS ============================================
    # ============================================ REPORT GENERATORS ============================================
    # ============================================ REPORT GENERATORS ============================================
    # ============================================ REPORT GENERATORS ============================================
    # ============================================ REPORT GENERATORS ============================================

    def view_and_sort_ByDegreeProgram(self, orgID): 
        cursor = self.connection.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT 
                    m.student_number,
                    CASE 
                        WHEN m.middle_name IS NULL THEN CONCAT(m.last_name, ', ', m.first_name)
                        ELSE CONCAT(m.last_name, ', ', m.first_name, ' ', m.middle_name)
                    END AS member_name,
                    m.degree_program,
                    m.gender
                FROM 
                    member m
                JOIN 
                    membership mem ON m.student_number = mem.student_number
                WHERE 
                    mem.organization_id = %s
                ORDER BY 
                    m.degree_program,
                    m.last_name,
                    m.first_name;
            """, (orgID,))
            
            results = cursor.fetchall()  # list of dicts
            return results

        except Error as e:
            print(f"Database error when viewing/sorting by degree program: {e}")
            return None

        finally:
            cursor.close()
