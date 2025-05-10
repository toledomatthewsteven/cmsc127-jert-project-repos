from database.connector import JERTDatabaseManager

class MainApplication:
    def __init__(self):
        self.db_manager = JERTDatabaseManager()

    def main_menu(self):
        print("\n====================MAIN MENU====================")
        print("[1] Student/Member View")
        print("[2] Organization View")
        print("[0] Exit")

    def student_member_view(self):
        print("\n====================STUDENT VIEW====================")
        print("[1] See unpaid fees")
        print("[0] Back to main menu")
        
        choice = input("Enter a choice: ")
        if choice == '1':
            student_id = input("Enter student number (202X-XXXXX): ")
            # add/perform database operations using self.db_manager.get_connection() ,, maybe in a different class?





        elif choice != '0':
            print("Invalid choice. Please try again.")


    def run(self):
        if not self.db_manager.connect():
            return
        else:
            print("Successfully connected to the database!")
            
        try:
            while True:
                self.main_menu()
                choice = input("Enter a choice: ")
                
                if choice == '1':
                    self.student_member_view()
                elif choice == '2':
                    print("Organization view goes here")

                    cursor = self.db_manager.connection.cursor() #dont forget ()
                    cursor.execute("SHOW TABLES")
                    for x in cursor:
                        print(x)

                    print("")
                elif choice == '0':
                    print("Exiting program...")
                    break
                else:
                    print("Invalid choice. Please try again.")
                    
        finally:
            self.db_manager.close_connection()


# ==== is this proper? idgaf.

app = MainApplication()
app.run()