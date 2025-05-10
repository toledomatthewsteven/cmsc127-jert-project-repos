import getpass 
import mysql.connector as mariadb #i prefer mysql.connector bcoz... that's what the youtube showed me!!!
from mysql.connector import Error

def get_db_credentials(): 
    print("\n==================== Database Login ====================")
    user = input("Username (default: root): ") or "root" #default
    password = getpass.getpass("Password: ") #secure password input
    host = input("Host (default: localhost): ") or "localhost" #default
    while True:
        db_name = input("Database name (required): ").strip()
        if db_name:
            break #exit loop coz valid
        print("Error: Database name cannot be empty. Please try again.")
    #would try to give a user an option to exit mid-launch but idgaf

    return {
        'user': user,
        'password': password,
        'host': host,
        'database': db_name
    } #an object thing for #credentials

def create_connection(): 
    credentials = get_db_credentials() #ensure credentials exist first
    
    try: 
        connection = mariadb.connect(
            host=credentials['host'],
            user=credentials['user'],
            password=credentials['password']
        )
        
        cursor = connection.cursor()
        
        cursor.execute(f"SHOW DATABASES LIKE '{credentials['database']}'") # Check if database entered via credentials exists
        result = cursor.fetchone()
        
        if not result: #no database returned
            print(f"Database '{credentials['database']}' not found")
            create = input("Create this database? (y/n): ").lower()
            
            if create == 'y':
                try:
                    cursor.execute(f"CREATE DATABASE {credentials['database']}")
                    connection.commit()
                    print(f"Database '{credentials['database']}' created successfully")
                    
                    # Reconnect to the new database
                    connection.close()
                    return mariadb.connect(
                        host=credentials['host'],
                        user=credentials['user'],
                        password=credentials['password'],
                        database=credentials['database']
                    )
                except Error as e:
                    print(f"Error creating database: {e}")
                    raise
            else:
                print("Database creation aborted")
                return None
        
        else: # Database exists - reconnect specifically to it
            connection.close() #close current "blank connection"
            return mariadb.connect(
                host=credentials['host'],
                user=credentials['user'],
                password=credentials['password'],
                database=credentials['database']
            )
            
    except Error as e:
        print(f"Database error: {e}")
        if 'connection' in locals() and connection.is_connected():
            connection.close()
        return None

def main_menu():
    # 
    print ("\n====================MAIN MENU====================")
    print("[1] Student/Member View")
    print("[2] Organization View")
    print("[0] Exit")


def student_member_view():
    print("")
    print ("====================STUDENT VIEW====================")
    print("[1] See a student's unpaid fees in all their organizations")
    print("[0] Exit")
    choice = input("Enter a choice: ")

    if choice == '1': 
        choice = input("Enter a student number (202X-XXXXX): ") 

        return
    elif choice == '0': 
        #gtfo!!!
        return
    else:
        print("Invalid choice. Please try again.")


def main():
    # Establish database connection
    connection = create_connection()
    if not connection:
        return
    if connection:
        print("Successfully connected to the database!")

    try:
        while True:
            main_menu() #print main menu
            choice = input("Enter a choice: ")
            
            if choice == '1': 
                student_member_view()
            elif choice == '2': 
                print("Organization view goes here")
            elif choice == '0':
                print("Exiting program...")
                break
            else:
                print("Invalid choice. Please try again.")

    
    finally:
        if connection.is_connected():
            connection.close()
            print("Database connection closed.")

# ========
main()