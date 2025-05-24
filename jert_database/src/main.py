from database.connector import JERTDatabaseManager

class MainApplication:
    def __init__(self):
        self.db_manager = JERTDatabaseManager()


    def main_menu(self):
        print("\n====================MAIN MENU====================")
        print("[1] Student/Member View")
        print("[2] Organization View")
        print("[0] Exit")


# ===================================================


    def student_member_view(self):
        print("\n====================STUDENT VIEW====================")
        print("[1] See unpaid fees")
        print("[0] Back to main menu")
        
        choice = input("Enter a choice: ")
        if choice == '1':
            student_number = input("Enter student number (20XX-XXXXX): ")
            # add/perform database operations using self.db_manager.get_connection() ,, maybe in a different class?





        elif choice != '0':
            print("Invalid choice. Please try again.")



# =============================================================

    def student_organization_view(self):
        while True:
            print("\n====================STUDENT ORGANIZATION VIEW====================")
            print("[1] See all registered organizations")
            print("[2] Register an organization") 
            print("[3] Inspect an organization") 
            print("[4] Drop/Delete an Organization") 
            print("[0] Back to main menu")
            print("")

            choice = input("Enter a choice: ")

            if choice == '1':
                organizations = self.db_manager.get_all_organizations()
                
                if not organizations:
                    print("\nNo organizations currently registered.")
                else:
                    print("\nRegistered Organizations:")
                    for org in organizations:
                        print(f" + {org['org_name']}")
                continue
            
            if choice == '2' : 
                self.register_new_organization()
                continue

            elif choice == '3':
                org_name = input("Enter an organization name (case-sensitive): ").strip()
                organization = self.db_manager.get_organization_by_name(org_name)
                
                if organization: #found!
                    print("found the org to inspect. now, CALL INSPECTION FUNCTIONS!!! THE MOTHERLODE!!!!")

                    self.inspect_student_organization_view(organization['organization_id'], org_name) #since organization returned a dictionary...

                    # print("org found!")
                else:
                    print(f"\nOrganization '{org_name}' not found.")
                
                continue

            elif choice == '4':
                self.drop_organization()
                continue
            
            elif choice == '0':
                break
            else:
                print("Invalid choice. Please try again.")

# =====================================================

    def inspect_student_organization_view(self, orgID, org_name):
        # print("by here, we should have the org id")
        # print(orgID) #trust we have it talaga
        #we should probs move this into a different file/class #oop but im lazy asf
        while True:
            print(F"\n====================INSPECTING: '{org_name}'====================")
            print("[1] Member Management")
            print("[2] Fee Management") 
            print("[3] Generate a Report")  
            print("[0] Back to main menu")
            print("")

            choice = input("Enter a choice: ")

            if choice == '1':
                self.member_management_menu(orgID, org_name)
                continue
            
            if choice == '2' : 
                self.fees_management_menu(orgID, org_name)
                continue

            elif choice == '3':
                self.report_generation_menu(orgID, org_name)
                continue 
            
            elif choice == '0':
                break
            else:
                print("Invalid choice. Please try again.")

    def member_management_menu(self, orgID, org_name):
        # we can probably separate these into classes lol #OOP ... this main.py long as fuck right now.. but im lazy asf
        while True:
            print(F"\n====================MEMBER MANAGEMENT: '{org_name}'====================")
            print("[1] Add a Member")
            print("[2] Update a Member's Information.") 
            print("[3] Delete a Member's Record") 
            print("[4] Search for a Member")  
            print("[5] Track a Member's Membership Status (is this the right label)")   
            print("[0] Back to main menu")
            print("")

            choice = input("Enter a choice: ")

            if choice == '1':
                print("1")
                continue
            
            if choice == '2' : 
                print("2")
                continue

            elif choice == '3':
                print("3")
                continue 

            elif choice == '4':
                print("4")
                continue 

            elif choice == '5':
                print("5")
                continue 
            
            elif choice == '0':
                break
            else:
                print("Invalid choice. Please try again.")

    def fees_management_menu(self, orgID, org_name):
        while True:
            print(F"\n====================FEES MANAGEMENT: '{org_name}'====================")
            print("[1] idk what to put here but... the project scoresheet called for invoicing and payment...")    
            print("[0] Back to main menu")
            print("")

            choice = input("Enter a choice: ")

            if choice == '1':
                print("1")
                continue 
            
            elif choice == '0':
                break
            else:
                print("Invalid choice. Please try again.")

    def report_generation_menu(self, orgID, org_name):
        while True:
            print(F"\n====================REPORT GENERATOR: '{org_name}'====================")
            print("[1] Filter and View All Members of the Organization")
            print("[2] View Members of the Organization with Unpaid Membership Fees for a Given Sem/AY")
            # print("[3] View a Member's Unpaid Membership Fees for All Organizations") #this dont belong here
            print("[3] View All Executive Committee Members of the Organization for a Given AY")
            print("[4] View All Presidents (or Any Other Role) of the Organization for a Given AY in Reverse Chronological Order")
            print("[5] View All Late Payments Made by All Members of the Organization for a Given Sem/AY")
            print("[6] View the Percentage of Active vs. Inactive Members of the Organization for the Last <n> Semesters")
            print("[7] View All Alumni Members of the Organization as of a Given Date")
            print("[8] View the Total Amount of Paid and Unpaid Fees of the Organization as of a Given Date")
            print("[9] View the Member(s) of the Organization with the Highest Debt for a Given Sem/AY")
            print("[0] Back to main menu")
            

            choice = input("Enter a choice: ")

            if choice == '1':
                print("1")
                continue 

            if choice == '2':
                print("2")
                continue 

            if choice == '3':
                print("3")
                continue 

            if choice == '4':
                print("4")
                continue 

            if choice == '5':
                print("5")
                continue 

            if choice == '6':
                print("6")
                continue 

            if choice == '7':
                print("7")
                continue 

            if choice == '8':
                print("8")
                continue 

            if choice == '9':
                print("9")
                continue 

            
            elif choice == '0':
                break
            else:
                print("Invalid choice. Please try again.")

# ======= HELPER FUNCTIONS ======

    def register_new_organization(self):
        print("\n=== REGISTER NEW ORGANIZATION ===") 

        try: 
            while True:
                org_name = input("Organization name: ").strip()
                if org_name:
                    break
                print("Error: Organization name cannot be empty.")
            
            
            while True:
                abbreviation = input("Abbreviation (3-10 letters): ").strip()
                if 3 <= len(abbreviation) <= 10:
                    break
                print("Error: Must be 3-10 letters.")
            
            while True:
                org_type = input(f"Type: ").strip()
                if org_type:
                    break
                print(f"Error: Type cannot be empty.")
            
            while True:
                year_str = input("Year established (YYYY): ").strip()
                if year_str.isdigit() and len(year_str) == 4:
                    year_established = int(year_str)
                    break
                print("Error: Year established must be valid.")
            
            while True:
                try:
                    semesters_active = int(input("Semesters active: "))
                    if semesters_active >= 0:
                        break
                    print("Error: Cannot be negative!")
                except ValueError:
                    print("Error: Please enter a whole number!")
            
            # Create a dictionary woot woot
            org_data = {
                'name': org_name,
                'abbreviation': abbreviation,
                'type': org_type,
                'year_established': year_established,
                'semesters_active': semesters_active
            }
            
            if self.db_manager.register_organization(org_data):
                print(f"\nSuccessfully registered {org_name}!")
            else:
                print("\nFailed to register organization.")
        
        except KeyboardInterrupt:
            print("\nRegistration cancelled.")
            return
        
    def drop_organization(self):
        organizations = self.db_manager.get_all_organizations()
        
        if not organizations:
            print("\nNo organizations currently registered.")
            return
        else:
            print("\nRegistered Organizations:")
            for org in organizations:
                print(f" + {org['org_name']}")
        
        org_name = input("\nEnter organization name to drop: ").strip()
        confirm = input(f"WARNING: This will delete ALL memberships for '{org_name}'. Confirm? (y/n): ").lower()

        if confirm == 'y':
            if self.db_manager.drop_organization(org_name):
                print("Organization deleted successfully.")
            else:
                print("Deletion failed or organization not found.")



# =============================================================


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
                    self.student_organization_view()

                    # print("Organization view goes here")

                    # cursor = self.db_manager.connection.cursor() #dont forget ()
                    # cursor.execute("SHOW TABLES")
                    # for x in cursor:
                    #     print(x)

                    # print("")
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

