import datetime
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
                    # print("found the org to inspect. now, CALL INSPECTION FUNCTIONS!!! THE MOTHERLODE!!!!")

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
            print("[3] Committee Management")  
            print("[4] Generate a Report")  
            print("[0] Back to main menu")
            print("")

            choice = input("Enter a choice: ")

            if choice == '1':
                self.member_management_menu(orgID, org_name)
                continue
            
            if choice == '2' : 
                self.fees_management_menu(orgID, org_name)
                continue

            if choice == '3' :
                self.committee_management_menu(orgID, org_name)

            elif choice == '4':
                self.report_generation_menu(orgID, org_name)
                continue 
            
            elif choice == '0':
                break
            else:
                print("Invalid choice. Please try again.")

# i should probably try to OOP this..... UGHHHHHH!!!!!
# ============================================== MEMBER MANAGEMENT ===============================================
# ============================================== MEMBER MANAGEMENT ===============================================
# ============================================== MEMBER MANAGEMENT ===============================================
# ============================================== MEMBER MANAGEMENT ===============================================
# ============================================== MEMBER MANAGEMENT ===============================================
# ============================================== MEMBER MANAGEMENT ===============================================
# ============================================== MEMBER MANAGEMENT ===============================================
# ============================================== MEMBER MANAGEMENT ===============================================
# ============================================== MEMBER MANAGEMENT ===============================================
# ============================================== MEMBER MANAGEMENT ===============================================
# ============================================== MEMBER MANAGEMENT ===============================================
# ============================================== MEMBER MANAGEMENT ===============================================

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
                self.add_member(orgID, org_name)
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


    def add_member(self, orgID, org_name):
        newMember_studentnumber = input("Enter student number of member: ")
        newMember_studentrecord = self.db_manager.get_student_record_by_studentNumber(newMember_studentnumber)

        if not newMember_studentrecord:
            print(f"\tStudent with student number {newMember_studentnumber} not found in this database's student records.")
            while True:
                decision_createNewStudent = input("Create a new student record? (y/n): ")
                if decision_createNewStudent == 'y':
                    # assign newMember_studentnumber to the created student number
                    newMember_studentnumber = self.create_newStudentRecord()
                    if not newMember_studentnumber:
                        print("\tStudent registration failed. Student number is invalid.")
                        return  # early exit because no valid student number
                    break
                elif decision_createNewStudent == 'n':
                    print("Student record creation aborted.")
                    return  # early exit to skip committee assignment
                else:
                    print("Invalid choice. Please try again.")
        else:
            print(f"\tStudent with student number '{newMember_studentnumber}' found!")

        already_member = self.db_manager.get_or_check_studentNumber_in_Membership(newMember_studentnumber, orgID, org_name)
        if already_member:
            print(f"\tWarning: Student '{newMember_studentnumber}' is already registered as a member of '{org_name}'.")  
            print("\tMember addition aborted.")
            return

        # committee assignment for a valid student number (found or created)
        assigned = self.committee_and_role_assignment(orgID, org_name, newMember_studentnumber)
        if not assigned:
            print("Committee and role assignment failed or skipped.")
            return
        
        while True:
            batch_year_input = input("Enter batch join-year (YYYY): ").strip()
            if batch_year_input.isdigit() and len(batch_year_input) == 4:
                batch_year = int(batch_year_input)
                break
            else:
                print("Invalid batch join-year. Please enter a 4-digit year.")

        while True:
            join_date_input = input("Enter join date (YYYY-MM-DD) [default today]: ").strip()
            if not join_date_input:
                join_date = None  # default to today
                break
            try:
                from datetime import datetime
                datetime.strptime(join_date_input, "%Y-%m-%d")
                join_date = join_date_input
                break
            except ValueError:
                print("Invalid date format. Please enter a valid date in YYYY-MM-DD format.")

        # Register membership!!!! no need a separate divider area for it
        if self.db_manager.register_membership(newMember_studentnumber, orgID, batch_year, join_date):
            print(f"\tMembership for student '{newMember_studentnumber}' in org '{org_name}' registered successfully!")
        else:
            print("Failed to register membership.")
            return #dk how to handle case where committee assignment works but membership dont :crying_laughing:
        
        print("\tMember-adding Operation Successful!")
        return 


# i should probably try to OOP this..... UGHHHHHH!!!!!
# ============================================== FEES MANAGEMENT ===============================================
# ============================================== FEES MANAGEMENT ===============================================
# ============================================== FEES MANAGEMENT ===============================================
# ============================================== FEES MANAGEMENT ===============================================
# ============================================== FEES MANAGEMENT ===============================================
# ============================================== FEES MANAGEMENT ===============================================
# ============================================== FEES MANAGEMENT ===============================================
# ============================================== FEES MANAGEMENT ===============================================
# ============================================== FEES MANAGEMENT ===============================================
# ============================================== FEES MANAGEMENT ===============================================
# ============================================== FEES MANAGEMENT ===============================================
# ============================================== FEES MANAGEMENT ===============================================


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

# ============================================== COMMITTEE MANAGEMENT ===============================================
# ============================================== COMMITTEE MANAGEMENT ===============================================
# ============================================== COMMITTEE MANAGEMENT ===============================================
# ============================================== COMMITTEE MANAGEMENT ===============================================
# ============================================== COMMITTEE MANAGEMENT ===============================================
# ============================================== COMMITTEE MANAGEMENT ===============================================
    
    def committee_management_menu(self, orgID, org_name):
        while True:
            print(F"\n====================COMMITTEE MANAGEMENT: '{org_name}'====================")
            print("[1] Create a Committee/Team")    
            print("[2] View All Committees/Teams and their Roles") 
            #idgaf to implemenet better committee management. too much na yan.
            print("[3] Dissolve a Committee/Team (UNINMPLEMENTED)")  
            print("[0] Back to main menu")
            print("")

            choice = input("Enter a choice: ")

            if choice == '1':
                self.create_committee(orgID, org_name)
                continue 

            if choice == '2': 
                committees = self.db_manager.get_committees_by_orgID_with_roles(orgID)

                if not committees:
                    print(f"\nNo committees currently registered under '{org_name}'.")
                else:
                    print("\nRegistered Committees and Roles:")
                    for comm in committees:
                        print(f" + {comm['committee_name']}")
                        if comm['roles']:
                            for role in comm['roles']:
                                print(f"    - {role}")
                        else:
                            print("    (No roles assigned)")
                continue 

            if choice == '3':
                print("3")
                continue 
            
            elif choice == '0':
                break
            else:
                print("Invalid choice. Please try again.")

    def create_committee(self, orgID, orgName):
        print(f"\n=== Creating a new committee for organization '{orgName}'===")

        while True: # Get committee name
            committee_name = input("Enter committee name (max 30 chars): ").strip()
            if 1 <= len(committee_name) <= 30:
                break
            print("Error: Committee name must be between 1 and 30 characters.")

        roles = [] # Collect initial roles (at least one role required)
        print("Enter committee roles (type 'done' to finish):")
        while True:
            role = input(f"Role #{len(roles)+1}: ").strip()
            if role.lower() == 'done':
                if roles:
                    break
                else:
                    print("Please enter at least one role before finishing.")
                    continue
            if 1 <= len(role) <= 30:
                roles.append(role)
            else:
                print("Error: Role must be between 1 and 30 characters.")

        # print("\nSummary:")
        # print(f"Committee name: {committee_name}")
        # print(f"Organization ID: {orgID}")
        # print(f"Roles: {roles}")
        
        newCommittee_newCommitteeRoles = {
            'committee_name': committee_name,
            'organization_id': orgID,
            'roles': roles
        }

        

        if self.db_manager.register_committee_with_roles(newCommittee_newCommitteeRoles):
            print(f"\nSuccessfully registered committee '{committee_name}' under '{orgName}'!")
        else:
            print("\nFailed to register new committee.")
            return


    

# ============================================== REPORT GENERATOR ===============================================
# ============================================== REPORT GENERATOR ===============================================
# ============================================== REPORT GENERATOR ===============================================
# ============================================== REPORT GENERATOR ===============================================
# ============================================== REPORT GENERATOR ===============================================
# ============================================== REPORT GENERATOR ===============================================
# ============================================== REPORT GENERATOR ===============================================
# ============================================== REPORT GENERATOR ===============================================
# ============================================== REPORT GENERATOR ===============================================
# ============================================== REPORT GENERATOR ===============================================




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

    #  ================== MINI DIVIDER =========================

    def committee_and_role_assignment(self, orgID, org_name, newMember_studentnumber):
        print("\n=== COMMITTEE & ROLE ASSIGNMENT ===")

        committees_with_roles = self.db_manager.get_committees_and_roles_by_orgID(orgID) # Fetch committees and roles

        if not committees_with_roles:
            print(f"\nNo committees currently registered under '{org_name}'.")
            print(f"\nCannot proceed with committee and role assignment.")
            return None

        committee_roles_dict = {}  # Organize committees and roles for validation
        for record in committees_with_roles:
            comm_name = record['committee_name']
            role_name = record['committee_role']
            if comm_name not in committee_roles_dict:
                committee_roles_dict[comm_name] = []
            committee_roles_dict[comm_name].append(role_name)

        print("\nAvailable Committees and Their Roles:")
        for comm, roles in committee_roles_dict.items():
            print(f" + {comm}: {', '.join(roles)}")

        print()
        while True:  # Committee selection with validation
            assigned_committee = input("Enter committee to assign the new member to: ").strip()
            if not assigned_committee:
                print("Error: Committee name cannot be empty.")
                continue

            if assigned_committee not in committee_roles_dict:
                print(f"Error: Committee '{assigned_committee}' does not exist under '{org_name}'.")
                print("Please choose from the listed committees.")
                continue
            break

        available_roles = committee_roles_dict[assigned_committee]  # Role selection with validation
        if not available_roles:
            print(f"Note: Committee '{assigned_committee}' has no predefined roles... Assigning as a general member.")
            assigned_role = None
        else:
            while True:
                assigned_role = input(f"Enter role to assign in '{assigned_committee}': ").strip()
                if not assigned_role:
                    print("Error: Role cannot be empty.")
                    continue

                if assigned_role not in available_roles:
                    print(f"Error: Role '{assigned_role}' does not exist in committee '{assigned_committee}'.")
                    print(f"Available roles: {', '.join(available_roles)}")
                    continue
                break

        while True:
            academic_year = input("Enter academic year of current membership (format YYYY-YYYY, e.g. 2024-2025): ").strip()
            if len(academic_year) == 9 and academic_year[4] == '-' and \
            academic_year[:4].isdigit() and academic_year[5:].isdigit() and \
            int(academic_year[5:]) == int(academic_year[:4]) + 1:
                break
            print("Error: Academic year must be in the format YYYY-YYYY with consecutive years.") #iiyak n me


        while True:
            semester = input("Enter semester of current membership ('First' or 'Second'): ").strip().capitalize()
            if semester in ['First', 'Second']:
                break
            print("Error: Semester must be 'First' or 'Second'.")

        # Membership status input
        valid_statuses = ['Active', 'Inactive', 'Expelled', 'Suspended', 'Alumni']
        while True:
            membership_status = input(f"Enter membership status of current membership  {valid_statuses}: ").strip().capitalize()
            if membership_status in valid_statuses:
                break
            print(f"Error: Membership status must be one of {valid_statuses}.")

        # print(f"\nAssigning member '{newMember_studentnumber}' to committee '{assigned_committee}'" +
        #     (f" with role '{assigned_role}'." if assigned_role else ".") +
        #     f" Academic Year: {academic_year}, Semester: {semester}, Status: {membership_status}")

        if self.db_manager.register_member_under_committee_with_role(
            newMember_studentnumber, orgID, assigned_committee, assigned_role, academic_year, semester, membership_status):

            print(f"\tSuccessfully assigned member to committee '{assigned_committee}' with role '{assigned_role}'!")
            return True
        else:
            print("\n\tFailed to assign new student to a committee and role.")
            return False

#  ================== MINI DIVIDER =========================

    def create_newStudentRecord(self):
        print("\n=== CREATING NEW STUDENT RECORD ===")

        try: 
            while True: # First name (required)
                first_name = input("First name: ").strip()
                if first_name:
                    break
                print("Error: First name cannot be empty.")

            middle_name = input("Middle name (optional): ").strip() or None # Middle name (optional)

            while True: # Last name (required)
                last_name = input("Last name: ").strip()
                if last_name:
                    break
                print("Error: Last name cannot be empty.")

            while True:  # Student number (XXXX-XXXXX)
                student_number = input("Student number (XXXX-XXXXX): ").strip()
                if len(student_number) == 10 and student_number[4] == '-':
                    prefix = student_number[:4]
                    suffix = student_number[5:]
                    if prefix.isdigit() and suffix.isdigit():
                        break
                print("Error: Student number must be in the format XXXX-XXXXX (where X is a digit).")


            while True: # Degree program (required)
                degree_program = input("Degree program (e.g. 'BS Computer Science'): ").strip()
                if degree_program:
                    break
                print("Error: Degree program cannot be empty.")

            while True: # Gender (required, 1 character)
                gender = input("Gender (M/F): ").strip().upper()
                if gender in ['M', 'F']:
                    break
                print("Error: Gender must be 'M' or 'F'. (Sorry, to our SOSC3 profs.)") 

            while True: # Graduation status (optional, default False)
                grad_status_input = input("Graduated? (Y/N, default N): ").strip().upper() or 'N'
                if grad_status_input in ['Y', 'N']:
                    graduation_status = True if grad_status_input == 'Y' else False
                    break
                print("Error: Must be 'Y' or 'N'.")

            # Graduation date (only if graduated)
            graduation_date = None
            if graduation_status:
                while True:
                    grad_date_input = input("Graduation date (YYYY-MM-DD): ").strip()
                    try:
                        datetime.strptime(grad_date_input, "%Y-%m-%d")
                        graduation_date = grad_date_input
                        break
                    except ValueError:
                        print("Error: Please enter a valid date in YYYY-MM-DD format.")

            # Create a dictionary for the member
            member_data = {
                'first_name': first_name,
                'middle_name': middle_name,
                'last_name': last_name,
                'student_number': student_number,
                'degree_program': degree_program,
                'gender': gender,
                'graduation_status': graduation_status,
                'graduation_date': graduation_date
            }

            print("\n\tMember data collected successfully!") 

            if self.db_manager.register_new_studentRecord(member_data):
                print(f"\tSuccessfully registered student with student number '{student_number}'!")
                return student_number  # return for use
            else:
                print("\tFailed to register new student record.")
                return None

            #  gotta put code here to insert into the database (for member table, for member-org relationship, for member-committee)
            # actually ,jk. not here. back to the original function! 
            
        except KeyboardInterrupt:
            print("\nRegistration cancelled.")
            return None


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

