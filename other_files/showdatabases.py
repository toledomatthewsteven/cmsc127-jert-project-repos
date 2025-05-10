import mysql.connector as mariadb
from mysql.connector import Error

def create_connection():
    """Create a database connection using root credentials"""
    try:
        connection = mariadb.connect(host='localhost', user='root', password='password' )
        return connection
    except Error as e:
        print(f"Error connecting to MariaDB: {e}")
        return None

def show_all_databases(connection): 
    try:
        cursor = connection.cursor()
        cursor.execute("SHOW DATABASES")
        databases = cursor.fetchall()
        
        print("\n==================== Databases ====================")
        for idx, db in enumerate(databases, 1):
            print(f"[{idx}] {db[0]}")
        print("===================================================\n")

    except Error as e:
        print(f"Error fetching databases: {e}")

def main_menu():
    """Display the main menu and handle user input"""
    print ("====================MAIN MENU====================\n[1] Show all databases\n[0] Exit \n================================================")

def main():
    # Establish database connection
    connection = create_connection()
    if not connection:
        return
    
    try:
        while True:
            main_menu() #print main menu
            choice = input("Enter a choice: ")
            
            if choice == '1':
                show_all_databases(connection)
            elif choice == '0':
                print("Exiting program...")
                break
            else:
                print("Invalid choice. Please try again.")
    finally:
        if connection.is_connected():
            connection.close()
            print("Database connection closed.")

# if __name__ == "__main__":
main()