from datetime import datetime
from datetime import date
from database.connector import JERTDatabaseManager
from tabulate import tabulate

class MainApplication:
    def __init__(self):
        self.db_manager = JERTDatabaseManager()


    def main_menu(self):
        print("\n====================MAIN MENU====================")
        print("[1] Student Record View")
        print("[2] Organization View")
        print("[0] Exit")


# ===================================================


    def student_member_view(self):
        try :
            while True:
                print("\n====================STUDENT RECORD VIEW====================")
                print("[1] Add a student record")  # DONE
                print("[2] View all student records") 
                print("[3] Locate a student record")  # DONE
                print("[4] Update a student record")  # DONE
                print("[5] Delete a student record")  # DONE
                print("[6] See Unpaid Fees of a Student (in all of their organizations)")  # DONE
                print("[0] Back")

                choice = input("Enter a choice: ")

                if choice == '1':
                    self.create_newStudentRecord()
                    continue

                elif choice == '2':
                    self.view_all_student_records()
                    continue

                elif choice == '3':
                    student_number = input("\nEnter student number (20XX-XXXXX): ")
                    self.print_member_table_entry_contents_helper(student_number)
                    continue

                elif choice == '4':
                    student_number = input("\nEnter student number to update (20XX-XXXXX): ").strip()
                    self.record_update_student(student_number)
                    continue

                elif choice == '5':
                    self.record_delete_student_harsh()
                    continue

                elif choice == '6':
                    self.see_unpaid_fees_of_student_in_all_orgs()
                    continue

                elif choice == '0':
                    return

                else:
                    print("Invalid choice. Please try again.")

        except KeyboardInterrupt:
            print("Student view interface aborted.")

    def view_all_student_records(self):
        print("\n=========ALL STUDENT RECORDS=========")
        try:
            records = self.db_manager.get_all_student_records()
            if not records:
                print("No student records found.")
                return
            
            better_names = {  # mapping the keys to more readable headers
                'first_name': 'First Name',
                'middle_name': 'Middle Name',
                'last_name': 'Last Name',
                'student_number': 'Student Number',
                'degree_program': 'Degree Program',
                'gender': 'Gender',
                'graduation_status': 'Graduation Status',
                'graduation_date': 'Graduation Date'
            }

            # Process each record for readability
            table_data = []
            for record in records:
                record['graduation_status'] = "Not Yet Graduated" if record['graduation_status'] == 0 else "Graduated"
                record['graduation_date'] = "N/A" if record['graduation_date'] is None else record['graduation_date']
                row = [record.get(key, '') for key in better_names.keys()]
                table_data.append(row)

            headers = list(better_names.values())
            from tabulate import tabulate
            print(tabulate(table_data, headers=headers, tablefmt="grid"))
            
        except KeyboardInterrupt:
            print("Cancelled viewing student records.")
            return


    def see_unpaid_fees_of_student_in_all_orgs(self):
        try:  
            student_number = input("Enter student number (20XX-XXXXX): ")
            entry = self.print_member_table_entry_contents_helper(student_number)

            if not entry :
                print("\tAborting report.")
                return
            else :
                results = self.db_manager.see_unpaid_fees_of_student_in_all_orgs(student_number)
                if not results:
                    print(f"\nNo unpaid fees found for student number '{student_number}'.")
                    return

                print(f"\n=== UNPAID FEES FOR STUDENT NUMBER '{student_number}'===\n")
                headers = [
                    "Org Name",
                    "Academic Year",
                    "Semester",
                    "Fee ID",
                    "Amount",
                    "Due Date",
                    "Late Status"
                ]
                table_data = [[
                    r['org_name'],
                    r['academic_year'],
                    r['semester'],
                    r['fee_id'],
                    r['amount'],
                    r['due_date'].strftime("%Y-%m-%d"),  # formatting date into a more readable format
                    "Late" if (r['late_status']) else "Not Late"
                ] for r in results]

                print(tabulate(table_data, headers=headers, tablefmt="grid")) 
        
        except KeyboardInterrupt:
            print("Aborting report.")
            return

    def record_delete_student_harsh(self):  
        try: 
            print("\n=== DELETING STUDENT RECORD ===")
            print("Note: Student number is uneditable. Please contact your supervisors if you wish to edit this.")
            print(f"Warning: Deleting a student record will delete all their associated fees, organization committee/role history, and organization membership information.")
            print(f"Warning: Deleting a student's record will remove them entirely from this database..")

            print("\n=== DELETING STUDENT RECORD ===")
            student_number = input("Enter student number (20XX-XXXXX): ")
            entry = self.print_member_table_entry_contents_helper(student_number)

            if not entry :
                print("\tAborting delete.")
                return
            else :
                print("\n=== DELETING STUDENT RECORD ===")
                confirm = input(f"Are you sure you want to proceed with deleting this record? (y/n): ").lower()

                if confirm == 'y':

                    self.db_manager.drop_member_committee_records_for_student(student_number)
                    self.db_manager.drop_fees_for_student(student_number)
                    self.db_manager.drop_membership_for_student(student_number)
                    self.db_manager.drop_member_entry_for_student(student_number)

                    print("Student record deleted successfully.")
                    return

                else: 
                    print("\tAborting deletion of member record.")
                    return
        
        except KeyboardInterrupt:
            print("Aborting delete.")
            return

        

    def record_update_student(self, student_number):
        # SEE IF ENTRY EXISTS 
        print("")
        entry = self.print_member_table_entry_contents_helper(student_number)
        if not entry :
            return
        else :
            print("\n=== UPDATING STUDENT RECORD ===")
            print("Note: Student number is uneditable. Please contact your supervisors if you wish to edit this.")

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

                print("\n\tUpdated student data collected successfully!") 

                if self.db_manager.update_studentRecord(member_data):
                    print(f"\tSuccessfully update data of student with student number '{student_number}'!")
                    return student_number  # return for use
                else:
                    print("\tFailed to update the student record.")
                    return None
            
            except KeyboardInterrupt:
                print("\nRegistration cancelled.")
                return None



# =============================================================

    def student_organization_view(self):
        while True:
            print("\n====================STUDENT ORGANIZATION VIEW====================")
            print("[1] See all registered organizations")
            print("[2] Register an organization") 
            print("[3] Inspect an organization") 
            # print("[4] Drop/Delete an Organization") #T0D0: touchup to delete all necessary components as well.. actually, just wont implement this bruh IT AINT IN SPECS
            print("[0] Back ")
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

            # elif choice == '4':
            #     self.drop_organization()
            #     continue
            
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
            print("[0] Back ")
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
            print("[1] Add a Member") # DONE
            print("[2] Update a Member's Information") # DONE
            print("[3] Delete a Member's Record") #DONE
            print("[4] Search for a Member")  # DONE
            print("[5] Track a Member's Committee/Role/Status History") # DONE 
            print("[0] Back ")
            print("")

            choice = input("Enter a choice: ")

            if choice == '1':
                self.add_member(orgID, org_name)
                continue
            
            if choice == '2' : 
                self.update_member(orgID, org_name)
                continue

            elif choice == '3':
                self.delete_member_record(orgID, org_name)
                continue 

            elif choice == '4':
                self.search_org_member_record(orgID, org_name)
                continue 

            elif choice == '5':
                self.track_org_member(orgID, org_name)
                continue 

            elif choice == '0':
                break
            
            else:
                print("Invalid choice. Please try again.")


    def delete_member_record(self, orgID, org_name): 
        print()
        print(f"\n========== Delete Member Interface: '{org_name}' ==========")
        print(f"Warning: Deleting a member's record will delete all their associated fees, committee/role history, and membership information.")
        print(f"Warning: Deleting a member's record for organization '{org_name}' will not delete their record from this entire database.")
        print(f"\n========== Delete Member Interface: '{org_name}' ==========")
        
        try:
            student_number = input("Enter student number of member to delete from organizational records: ").strip()
            print("")
            
            history = self.db_manager.get_or_check_studentNumber_in_Membership(student_number, orgID, org_name) # Check if student exists in membership relationship

            if not history:
                print(f"\tSeems like student number '{student_number}' is not a member of '{org_name}'. Aborting deletion.")
                return
            
            # Print it lang lol
            
            member_table_entry = self.db_manager.get_student_record_by_studentNumber(student_number)
            if member_table_entry: 
                member_table_entry['graduation_status'] = "Not Yet Graduated" if member_table_entry['graduation_status'] == 0 else "Graduated" #readability concern 
                member_table_entry['graduation_date'] = "N/A" if member_table_entry['graduation_date'] is None else member_table_entry['graduation_date']

                better_names = { # mapping the keys to more readable headers
                    'first_name': 'First Name',
                    'middle_name': 'Middle Name',
                    'last_name': 'Last Name',
                    'student_number': 'Student Number',
                    'degree_program': 'Degree Program',
                    'gender': 'Gender',
                    'graduation_status': 'Graduation Status',
                    'graduation_date': 'Graduation Date'
                }

                headers = [better_names.get(key, key) for key in member_table_entry.keys()]
                values = [member_table_entry[key] for key in member_table_entry.keys()]

                print(tabulate([values], headers=headers, tablefmt="grid"))
            else:
                print(f"No record found for student number {student_number}.")
                return 
            
            confirm = input(f"Are you sure you want to proceed with deleting this member? (y/n): ").lower()
            if confirm == 'y':

                #drop from membership
                #drop all fees related to them (AND MUST BE UNDER THE ORG... lol)
                #drop all member_committee records related to them (AND THE ORG)

                self.db_manager.drop_member_committee_records_from_org(student_number, orgID)
                self.db_manager.drop_fees_for_member_from_org(student_number, orgID)
                self.db_manager.drop_membership_from_org(student_number, orgID)
                print("Member records deleted successfully.")

            else: 
                print("\tAborting deletion of member record.")
                return
        except KeyboardInterrupt:
            print("Deletion process aborted.")
            return 

    def search_org_member_record(self, orgID, org_name):
        print(f"\n========== Search Member Interface: '{org_name}' ==========")
        try:
            student_number = input("Enter student number of member to search for: ").strip()
            
            history = self.db_manager.get_or_check_studentNumber_in_Membership(student_number, orgID, org_name) # Check if student exists in membership relationship

            if not history:
                print(f"\tSeems like student number '{student_number}' is not a member of '{org_name}'.")
                return
            
            member_table_entry = self.db_manager.get_student_record_by_studentNumber(student_number)
            if member_table_entry: 
                member_table_entry['graduation_status'] = "Not Yet Graduated" if member_table_entry['graduation_status'] == 0 else "Graduated" #readability concern 
                member_table_entry['graduation_date'] = "N/A" if member_table_entry['graduation_date'] is None else member_table_entry['graduation_date']

                better_names = { # mapping the keys to more readable headers
                    'first_name': 'First Name',
                    'middle_name': 'Middle Name',
                    'last_name': 'Last Name',
                    'student_number': 'Student Number',
                    'degree_program': 'Degree Program',
                    'gender': 'Gender',
                    'graduation_status': 'Graduation Status',
                    'graduation_date': 'Graduation Date'
                }

                headers = [better_names.get(key, key) for key in member_table_entry.keys()]
                values = [member_table_entry[key] for key in member_table_entry.keys()]

                print(tabulate([values], headers=headers, tablefmt="grid"))
            else:
                print(f"No record found for student number {student_number}.")

        except KeyboardInterrupt:
            print("Search process aborted.")
            return
    
    def track_org_member(self, orgID, org_name):
        print(f"\n========== Tracking Member History Interface: '{org_name}' ==========")
        try:
            student_number = input("Enter student number of member to track history of: ").strip()
            
            history = self.db_manager.get_member_committee_history(student_number, orgID) # Check if student exists in committee history

            if not history:
                print(f"\tNo historical records found for student number '{student_number}' in '{org_name}'.")
                return
            
            table_data = [[
                record['committee_name'],
                record['committee_role'],
                record['academic_year'],
                record['semester'],
                record['membership_status']
            ] for record in history]

            print(f"\n=== Committee/Role/Status History for Student Number '{student_number}' ===") # Print as table 
            print(tabulate(table_data, headers=["Committee", "Role", "Academic Year", "Semester", "Status"], tablefmt="grid"))

            latest_entry = max(history, key=lambda entry: self.get_acad_year_semester_key(entry)) 
            latest_ay = latest_entry['academic_year']
            latest_sem = latest_entry['semester']
            latest_committee = latest_entry['committee_name']
            latest_role = latest_entry['committee_role']
            latest_status = latest_entry['membership_status']

            print("\nNote: This table only reflects entries where the committee, role, or status changed or initialized.")
            print("If there are no later entries after a given year/semester, it means the member remains in that committee/role/status until further notice.")
            print(f"For example, as of Academic Year {latest_ay}, {latest_sem} Semester,")
            print(f"the member is in '{latest_committee}' with the role '{latest_role}' and status '{latest_status}'.")
            print("Since there are no more recent entries, the member is assumed to still hold this role and status in this committee.")

        except KeyboardInterrupt:
            print("Tracking process aborted.")
            return
        
    def get_acad_year_semester_key(self, entry): 
        year_str = entry['academic_year'] # Extract start year as integer
        year_start = int(year_str.split('-')[0]) 
        semester_str = entry['semester'] # Convert semester to a number
        semester_num = 1 if semester_str.lower() == 'first' else 2
        
        return (year_start, semester_num)
    


    def update_member(self, orgID, org_name):
        print(f"\n========== Update Member Interface: '{org_name}' ==========")
        try:
            student_number = input("Enter student number of member to update: ").strip()
            
            history = self.db_manager.get_member_committee_history(student_number, orgID) # Check if student exists in committee history

            if not history:
                print(f"\tNo committee records found for student number '{student_number}' in '{org_name}'.")

                membercheck = self.db_manager.get_membership_record(student_number, orgID)
                if membercheck:
                    print("Proceeding to create new committee/role/status log for this member...")
                    join_date_obj = membercheck['join_date']
                    self.committee_and_role_assignment(orgID, org_name, student_number, join_date_obj)



                return
            
            table_data = [[
                record['committee_name'],
                record['committee_role'],
                record['academic_year'],
                record['semester'],
                record['membership_status']
            ] for record in history]

            print(f"\n=== Committee History for Student Number '{student_number}' ===") # Print as table
            print(tabulate(table_data, headers=["Committee", "Role", "Academic Year", "Semester", "Status"], tablefmt="grid"))

            # Choose update option
            while True:
                print("\nDo you want to:")
                print("[1] Update an existing entry (change status/committee/role in a past AY & Sem)")
                print("[2] Add a new committee/role/status entry (new assignment/adding history log)")
                # ugh should i even entertain the case where they want to update the fucking join_date or batch year.. .
                    #there's so much dependent on that and anomalies that could be caused .... 
                    #it's not that relevant in our scope rn sooo ill leave it alone. FUCK OFF!
                #t0d0: ... kill urself



                choice = input("Enter your choice (1/2): ").strip()

                if choice == '1':
                    print("\tProceeding to update an existing entry...")
                    self.update_existing_committee_entry(orgID, org_name, student_number, history)
                    break 
                elif choice == '2':
                    print("\tProceeding to add a new assignment...")
                    self.add_new_committee_assignment(orgID, org_name, student_number, history)
                    break 
                else:
                    print("Invalid choice. Please enter 1 or 2.")


        except KeyboardInterrupt:
            print("Update process aborted.")
            return

    def update_existing_committee_entry(self, orgID, org_name, student_number, history):
        print("\n=== UPDATING EXISTING LOG ===")

        academic_year = input("Enter academic year of log to edit (format YYYY-YYYY, e.g. 2024-2025): ").strip()
        semester = input("Enter semester of log to edit ('First' or 'Second'): ").strip().capitalize()

        # no need to rlly validate these since we are searching for it anyway
        # RESOLVED t0d0: search in history if there is a match !! if none, gtfo.
        matching_records = [
            rec for rec in history
            if rec['academic_year'] == academic_year and rec['semester'] == semester
        ]
        if not matching_records:
            print(f"\tNo existing committee entry found for {academic_year}'s {semester} semester. Aborting update.")
            return None

        # Membership status input
        valid_statuses = ['Active', 'Inactive', 'Expelled', 'Suspended', 'Alumni']
        while True:
            membership_status = input(f"Enter membership status of current membership {valid_statuses}: ").strip().capitalize()
            if membership_status in valid_statuses:
                break
            print(f"Error: Membership status must be one of {valid_statuses}.")

        # if NOT Active, skip committee and role assignment
        if membership_status != 'Active':
            if self.db_manager.update_existing_committee_log(student_number, orgID, None, None, academic_year, semester, membership_status):
                print(f"\tSuccessfully updated log with status {membership_status} (no committee/role assignment).")
                return True
            else:
                print("\n\tFailed to update log.")
                return False

        committees_with_roles = self.db_manager.get_committees_and_roles_by_orgID(orgID)  # Fetch committees and roles
        if not committees_with_roles:
            print(f"\n\tNo committees currently registered under '{org_name}'.")
            print(f"\n\tCannot proceed with committee and role assignment.")
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
            assigned_committee = input("Enter committee to reassign the member to: ").strip()
            if not assigned_committee:
                print("\tError: Committee name cannot be empty.")
                continue
            if assigned_committee not in committee_roles_dict:
                print(f"\tError: Committee '{assigned_committee}' does not exist under '{org_name}'.")
                print("\tPlease choose from the listed committees.")
                continue
            break

        available_roles = committee_roles_dict[assigned_committee]  # Role selection with validation
        if not available_roles:
            print(f"\tNote: Committee '{assigned_committee}' has no predefined roles... Assigning as a general member.")
            assigned_role = None
        else:
            while True:
                assigned_role = input(f"Enter role to assign in '{assigned_committee}': ").strip()
                if not assigned_role:
                    print("Error: Role cannot be empty.")
                    continue
                if assigned_role not in available_roles:
                    print(f"\tError: Role '{assigned_role}' does not exist in committee '{assigned_committee}'.")
                    print(f"\tAvailable roles: {', '.join(available_roles)}")
                    continue
                break

        if self.db_manager.update_existing_committee_log(student_number, orgID, assigned_committee, assigned_role, academic_year, semester, membership_status):
            print(f"\tSuccessfully updated log!")
            return True
        else:
            print("\n\tFailed to update log.")
            return False


    def add_new_committee_assignment(self, orgID, org_name, student_number, history):
        print("\n=== REASSIGNMENT OF COMMITTEE, ROLE, OR STATUS ===")

        # Academic Year and Semester (with validation)
        while True:
            academic_year = input("Enter academic year of start of new committee residence (format YYYY-YYYY, e.g. 2024-2025): ").strip()
            semester = input("Enter semester of current membership ('First' or 'Second'): ").strip().capitalize()

            if not (len(academic_year) == 9 and academic_year[4] == '-' and
                    academic_year[:4].isdigit() and academic_year[5:].isdigit() and
                    int(academic_year[5:]) == int(academic_year[:4]) + 1):
                print("\tError: Academic year must be in the format YYYY-YYYY with consecutive years.")
                continue

            if semester not in ['First', 'Second']:
                print("\tError: Semester must be 'First' or 'Second'.")
                continue

            acad_year_start = int(academic_year[:4])

            membership = self.db_manager.get_membership_record(student_number, orgID)
            if not membership:
                print(f"\tWarning: No membership record found for student {student_number} in organization {orgID}. Are you really a member?")
                print('\tAborting operation.')
                return

            join_year = membership['batch_year']
            if acad_year_start < join_year:
                print(f"\tError: Academic year start {acad_year_start} is earlier than the student’s org join year ({join_year}). Please enter a valid academic year.")
                continue

            duplicate_entry = any(
                record['academic_year'] == academic_year and record['semester'] == semester
                for record in history
            )
            if duplicate_entry:
                print(f"\tError: An entry for academic year '{academic_year}' and semester '{semester}' already exists for this student.")
                print("\tPlease enter a different academic year or semester, or please cancel this assignment to use the proper function call.")
                continue

            break  # Valid academic year and semester

        # Membership Status
        valid_statuses = ['Active', 'Inactive', 'Expelled', 'Suspended', 'Alumni']
        while True:
            membership_status = input(f"Enter membership status of current membership {valid_statuses}: ").strip().capitalize()
            if membership_status in valid_statuses:
                break
            print(f"Error: Membership status must be one of {valid_statuses}.")

        if membership_status != 'Active':
            # Non-active statuses: skip committee and role assignment
            if self.db_manager.register_member_under_committee_with_role(
                student_number, orgID, None, None, academic_year, semester, membership_status):
                print(f"\tSuccessfully updated membership status to {membership_status} without committee/role assignment.")
                return True
            else:
                print("\n\tFailed to update membership status.")
                return False

        # Committee and Role (only for active members)
        committees_with_roles = self.db_manager.get_committees_and_roles_by_orgID(orgID)
        if not committees_with_roles:
            print(f"\n\tNo committees currently registered under '{org_name}'.")
            print(f"\n\tCannot proceed with committee and role assignment.")
            return None

        committee_roles_dict = {}
        for record in committees_with_roles:
            comm_name = record['committee_name']
            role_name = record['committee_role']
            if comm_name not in committee_roles_dict:
                committee_roles_dict[comm_name] = []
            committee_roles_dict[comm_name].append(role_name)

        print("\nAvailable Committees and Their Roles:")
        for comm, roles in committee_roles_dict.items():
            print(f" + {comm}: {', '.join(roles)}")

        # Committee selection
        while True:
            assigned_committee = input("Enter committee to reassign the member to: ").strip()
            if not assigned_committee:
                print("\tError: Committee name cannot be empty.")
                continue

            if assigned_committee not in committee_roles_dict:
                print(f"\tError: Committee '{assigned_committee}' does not exist under '{org_name}'.")
                print("\tPlease choose from the listed committees.")
                continue
            break

        available_roles = committee_roles_dict[assigned_committee]
        if not available_roles:
            print(f"\tNote: Committee '{assigned_committee}' has no predefined roles... Assigning as a general member.")
            assigned_role = None
        else:
            while True:
                assigned_role = input(f"Enter role to assign in '{assigned_committee}': ").strip()
                if not assigned_role:
                    print("Error: Role cannot be empty.")
                    continue

                if assigned_role not in available_roles:
                    print(f"\tError: Role '{assigned_role}' does not exist in committee '{assigned_committee}'.")
                    print(f"\tAvailable roles: {', '.join(available_roles)}")
                    continue
                break

        # Final registration
        if self.db_manager.register_member_under_committee_with_role(
            student_number, orgID, assigned_committee, assigned_role, academic_year, semester, membership_status):
            print(f"\tSuccessfully assigned member to committee '{assigned_committee}' with role '{assigned_role}' and status {membership_status}.")
            return True
        else:
            print("\n\tFailed to assign member to a committee and role.")
            return False


    def add_member(self, orgID, org_name):
        print(f"\n========== Add Member Interface: '{org_name}' ==========")
        try: 
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
                            print("\tStudent registration failed. Student number is invalid or registration was manually terminated.")
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
            
            # ================================

            while True:
                batch_year_input = input("Enter batch join-year (YYYY): ").strip()
                if batch_year_input.isdigit() and len(batch_year_input) == 4:
                    batch_year = int(batch_year_input)
                    break
                else:
                    print("Invalid batch year. Please enter a 4-digit year.")

            while True:
                join_date_input = input("Enter join date (YYYY-MM-DD) [default today]: ").strip()
                if not join_date_input:
                    join_date = None
                    join_date_obj = datetime.today()
                else:
                    try:
                        join_date_obj = datetime.strptime(join_date_input, "%Y-%m-%d")
                        join_date = join_date_input
                    except ValueError:
                        print("Invalid date format. Use YYYY-MM-DD.")
                        continue
                if join_date_obj.year != batch_year:
                    print(f"Warning: Join date year ({join_date_obj.year}) and batch year ({batch_year}) mismatch.")
                    continue
                break

            # Register membership
            if self.db_manager.register_membership(newMember_studentnumber, orgID, batch_year, join_date):
                print(f"\tMembership for student '{newMember_studentnumber}' in org '{org_name}' registered successfully!")
            else:
                print("Failed to register membership.")
                return

            self.committee_and_role_assignment(orgID, org_name, newMember_studentnumber, join_date_obj)
            print("\tMember-adding Operation Successful!")
            return

        except KeyboardInterrupt:
            print("\nRegistration cancelled.")
            return None

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

            print("[1] Create an Invoice")    
            print("[2] Pay a Fee")    
            print('[3] View All Fee Records')
            print("[0] Back to main menu")
            print("")

            choice = input("Enter a choice: ")

            if choice == '1':
                self.create_newFeeRecord(orgID)
                continue 
            
            if choice == '2':
                self.pay(orgID)
                continue

            if choice == '3':
                self.fees_view_all(orgID)
                continue
            
            elif choice == '0':
                break
            else:
                print("Invalid choice. Please try again.")

    def fees_view_all(self, orgID):
        print("\n========= ALL FEES FOR ORGANIZATION =========")
        fees = self.db_manager.get_fees_of_orgID(orgID)
        
        if not fees:
            print("No fees found for this organization.")
            return
        
        better_headers = {
            'fee_id': 'Fee ID',
            'amount': 'Amount',
            'due_date': 'Due Date',
            'semester': 'Semester',
            'academic_year': 'Academic Year',
            'payment_date': 'Payment Date',
            'payment_status': 'Payment Status',
            'student_number': 'Student Number',
            'organization_id': 'Organization ID',
            'late_status': 'Late Status'
        }
        
        # Convert payment_status and late_status to readable
        table_data = []
        for fee in fees:
            row = [
                fee.get('fee_id'),
                fee.get('amount'),
                fee.get('due_date').strftime("%Y-%m-%d") if fee.get('due_date') else "N/A",
                fee.get('semester'),
                fee.get('academic_year'),
                fee.get('payment_date').strftime("%Y-%m-%d") if fee.get('payment_date') else "N/A",
                "Paid" if fee.get('payment_status') else "Unpaid",
                fee.get('student_number'),
                fee.get('organization_id'),
                "Late" if (fee.get('late_status') or (fee.get('payment_status') and fee.get('payment_date') > fee.get('due_date'))) else "Not Late"
            ]
            table_data.append(row)
        
        headers = list(better_headers.values())
        print(tabulate(table_data, headers=headers, tablefmt="grid"))

    
    def create_newFeeRecord(self, orgID):
        print("\n=== CREATING NEW FEE RECORD ===")

        try: 
            while True:
                amount = input("Amount: ").strip()
                if amount and amount.isdigit():
                    amount = int(amount)
                    if amount < 0:
                        print("Error: Amount cannot be negative")
                    else:
                        break
                elif amount and  not amount.isdigit():
                    print("Error: Amount must be an digit")
                else:
                    print("Error: Amount cannot be empty.")

            while True:
                due_date_input = input("Due date (YYYY-MM-DD): ").strip()
                try:
                    from datetime import datetime
                    datetime.strptime(due_date_input, "%Y-%m-%d")
                    due_date = due_date_input
                    break
                except ValueError:
                    print("Error: Please enter a valid date in YYYY-MM-DD format.")
            
            while True: 
                semester = input("Semester (1 or 2): ").strip()
                if semester and semester.isdigit():
                    semester = int(semester)
                    if semester < 0 and semester > 2:
                        print("Error: Semesters can only be 1 or 2")
                    else:
                        break
                elif semester and not semester.isdigit():
                    print("Error: Semester must be an digit")
                else:
                    print("Error: Semester cannot be empty.")

            while True: #TODO: Make Academic Year checking
                academic_year = input("Academic Year (YYYY-YYYY): ").strip()
                if len(academic_year) == 9 and academic_year[4] == '-':
                    prefix = academic_year[:4]
                    suffix = academic_year[5:]
                    if prefix.isdigit() and suffix.isdigit():
                        break
                print("Error: Academic Year must be in the format XXXX-XXXX (where X is a digit).")


            while True:
                student_number = input("Student number (XXXX-XXXXX): ").strip()
                
                # Basic format check
                if len(student_number) == 10 and student_number[4] == '-' and \
                student_number[:4].isdigit() and student_number[5:].isdigit():
                    
                    if self.db_manager.get_or_check_studentNumber_in_Membership(student_number, orgID, "asd"):
                        break  # Valid and found student number, exit loop
                    else:
                        print("ERROR: Student not found.")
                
                else:
                    print("Error: Student number must be in the format XXXX-XXXXX (where X is a digit).")


            # Create a dictionary for the member
            fee_data = {
                'amount': amount,
                'due_date': due_date,
                'semester': semester,
                'academic_year': academic_year,
                'student_number': student_number,
                'organization_id': orgID
            }

            print("\nData collected successfully!") 

            if self.db_manager.register_new_feeRecord(fee_data):
                print(f"\tSuccessfully registered fee")
                return None  # return for use
            else:
                print("\tFailed to register new fee record.")
                return None
            
        except KeyboardInterrupt:
            print("\nRegistration cancelled.")
            return None
        
    def pay(self, orgID): # PAY requirement for FEE MANAGEMENT
        print("\n=========PAYING FEE==========")
        
        try:
            while True:
                feeID = input("Enter fee id to be paid: ")
                fee = self.db_manager.get_fee_by_fee_id(orgID, feeID)
                if fee:
                    while True:
                        payment_date = input("Enter payment date (YYYY-MM-DD) or press enter for today: ").strip()
                        if not payment_date:
                            # Automatically set today’s date
                            payment_date = datetime.now().strftime("%Y-%m-%d")
                            print(f"\tUsing today’s date: {payment_date}")
                            break
                        try:
                            datetime.strptime(payment_date, "%Y-%m-%d")
                            break
                        except ValueError:
                            print("\tInvalid date format or invalid date. Please try again.")
                    
                    self.db_manager.pay_fee(orgID, feeID, payment_date)
                    print("\tPayment Successful.")
                    return None
                print("\tFee not found")
        except KeyboardInterrupt:
            print("\nPayment Cancelled")
            return None

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
            # print("[3] Dissolve a Committee/Team (UNINMPLEMENTED)")  
            print("[0] Back ")
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

            # if choice == '3':
            #     print("3")
            #     continue 
            
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
            print("[1] View and Sort All Members of the Organization")
            print("[2] View Members of the Organization with Unpaid Membership Fees for a Given Sem/AY")
            # print("[3] View a Member's Unpaid Membership Fees for All Organizations") #this dont belong here
            print("[3] View All Executive Committee Members of the Organization for a Given AY")
            print("[4] View All Presidents (or Any Other Role) of the Organization for a Given AY in Reverse Chronological Order")
            print("[5] View All Late Payments Made by All Members of the Organization for a Given Sem/AY")
            print("[6] View the Percentage of Active vs. Inactive Members of the Organization for the Last <n> Semesters")
            print("[7] View All Alumni Members of the Organization as of a Given Date")
            print("[8] View the Total Amount of Paid and Unpaid Fees of the Organization as of a Given Date")
            print("[9] View the Member(s) of the Organization with the Highest Debt for a Given Sem/AY")
            print("[0] Back")
            

            choice = input("Enter a choice: ")

            if choice == '1':
                self.view_and_sort_all_members_menu(orgID, org_name)
                continue 

            if choice == '2':
                self.get_unpaid_mem(orgID)
                continue 

            if choice == '3':
                self.get_execs_by_acad_year(orgID)
                continue 

            if choice == '4':
                #print("4")
                self.get_members_by_role(orgID)
                continue 

            if choice == '5':
                # print("5")
                self.view_all_late_payments_given_sem(orgID, org_name)
                continue 

            if choice == '6':
                self.view_percentage_active_inactive_members(orgID, org_name) 
                continue 

            if choice == '7':
                self.get_alumni_from_date(orgID)
                continue 

            if choice == '8':
                self.get_amount_fee(orgID)
                continue 

            if choice == '9':
                # print("9")
                self.view_highest_unpaid_fees_members(orgID, org_name)
                continue 

            elif choice == '0':
                break
            else:
                print("Invalid choice. Please try again.")

    # ================== view_and_sort_all_members_menu ==================
    # ================== view_and_sort_all_members_menu ==================
    # ================== view_and_sort_all_members_menu ==================
    # ================== view_and_sort_all_members_menu ==================

    # (1) View and Sort All Members of the Organization
    def view_and_sort_all_members_menu(self, orgID, org_name):
        while True:
            print(F"\n==================== [1] View and Sort All Members of the Organization : '{org_name}'====================")
            print("[1] Sort by Role")
            print("[2] Sort by Status") 
            print("[3] Sort by Gender")
            print("[4] Sort by Degree Program") #starting here coz it's easiest and we have a statement already
            print("[5] Sort by Batch (join-year)")
            print("[6] Sort by Committee")
            print("[0] Back")

            choice = input("Enter a choice: ")

            if choice == '1':
                self.view_and_sort_ByRole(orgID, org_name)
                continue 

            if choice == '2': #sort by status
                self.view_and_sort_ByStatus(orgID, org_name)
                continue 

            if choice == '3':
                self.view_and_sort_ByGender(orgID, org_name)
                continue 

            if choice == '4':
                self.view_and_sort_ByDegreeProgram(orgID, org_name)
                continue 

            if choice == '5':
                self.view_and_sort_ByBatchJoinYear(orgID, org_name)
                continue 

            if choice == '6':
                self.view_and_sort_ByCommittee(orgID, org_name)
                continue 
            
            elif choice == '0':
                break
            else:
                print("Invalid choice. Please try again.")
    
    def view_and_sort_ByRole(self, orgID, org_name):
        results = self.db_manager.view_and_sort_ByRole(orgID)  # returns list of dicts

        if not results:
            print(f"\nNo members with roles found for organization '{org_name}'.")
            return

        print(f"\n=== MEMBERS OF '{org_name}' SORTED BY COMMITTEE AND ROLE ===\n")
        print("Note: This table only reflects entries where the committee and role are their latest entries.") 

        headers = [
            "Student Number", 
            "Name", 
            "Committee", 
            "Role", 
            "Degree Program", 
            "Gender"
        ]
        table_data = [[
            r['student_number'],
            r['member_name'],
            r['committee_name'],
            r['committee_role'],
            r['degree_program'],
            r['gender']
        ] for r in results]

        # Print the table
        print(tabulate(table_data, headers=headers, tablefmt="grid"))

    def view_and_sort_ByStatus(self, orgID, org_name):
        results = self.db_manager.view_and_sort_ByStatus(orgID)  # returns list of dicts

        if not results:
            print(f"\nNo members found for organization '{org_name}'.")
            return

        print(f"\n=== MEMBERS OF '{org_name}' SORTED BY LATEST MEMBERSHIP STATUS ===\n")
        print("Note: This table reflects only the latest membership status for each member.")

        headers = [
            "Student Number",
            "Name",
            "Degree Program",
            "Gender",
            "Latest Membership Status"
        ]
        table_data = [[
            r['student_number'],
            r['member_name'],
            r['degree_program'],
            r['gender'],
            r['latest_status']
        ] for r in results]

        # Print the table
        print(tabulate(table_data, headers=headers, tablefmt="grid"))

    def view_and_sort_ByGender(self, orgID, org_name):
        results = self.db_manager.view_and_sort_ByGender(orgID) #returns lsit of dicts

        if not results:
            print(f"\nNo members found for organization '{org_name}'.")
            return

        print(f"\n=== MEMBERS OF '{org_name}' SORTED BY GENDER ===\n")
        
        # Prepare data for tabulate
        headers = ["Student Number", "Name", "Degree Program", "Gender"]
        table_data = [[r['student_number'], r['member_name'], r['degree_program'], r['gender']] for r in results]

        # Print the table
        print(tabulate(table_data, headers=headers, tablefmt="grid"))

    def view_and_sort_ByDegreeProgram(self, orgID, org_name):
        results = self.db_manager.view_and_sort_ByDegreeProgram(orgID) #returns lsit of dicts

        if not results:
            print(f"\nNo members found for organization '{org_name}'.")
            return

        print(f"\n=== MEMBERS OF '{org_name}' SORTED BY DEGREE PROGRAM ===\n")
        
        # Prepare data for tabulate
        headers = ["Student Number", "Name", "Degree Program", "Gender"]
        table_data = [[r['student_number'], r['member_name'], r['degree_program'], r['gender']] for r in results]

        # Print the table
        print(tabulate(table_data, headers=headers, tablefmt="grid"))

    def view_and_sort_ByBatchJoinYear(self, orgID, org_name):
        results = self.db_manager.view_and_sort_ByBatchJoinYear(orgID) #returns lsit of dicts

        if not results:
            print(f"\nNo members found for organization '{org_name}'.")
            return

        print(f"\n=== MEMBERS OF '{org_name}' SORTED BY BATCH/JOIN-YEAR ===\n")
        
        # Prepare data for tabulate
        headers = ["Student Number", "Name", "Batch (Join Year)"]
        table_data = [[r['student_number'], r['member_name'], r['batch_year']] for r in results]

        # Print the table
        print(tabulate(table_data, headers=headers, tablefmt="grid"))

    def view_and_sort_ByCommittee(self, orgID, org_name):
        results = self.db_manager.view_and_sort_ByCommittee(orgID)  # returns list of dicts

        if not results:
            print(f"\nNo members with roles found for organization '{org_name}'.")
            return

        print(f"\n=== MEMBERS OF '{org_name}' SORTED BY COMMITTEE ===\n")
        print("Note: This table only reflects entries where the committee are their latest entries.") 

        headers = [
            "Student Number", 
            "Name", 
            "Committee",  
            "Degree Program", 
            "Gender"
        ]
        table_data = [[
            r['student_number'],
            r['member_name'],
            r['committee_name'], 
            r['degree_program'],
            r['gender']
        ] for r in results]

        # Print the table
        print(tabulate(table_data, headers=headers, tablefmt="grid"))

    # REPORT 5: 
    def view_all_late_payments_given_sem(self, orgID, org_name):

        acad_year = input("Enter academic year (e.g. '2024-2025'): ").strip()
        semester  = input("Enter semester (1 or 2): ").strip()

        results = self.db_manager.view_all_late_payments_given_sem(orgID, acad_year, semester)

        if not results:
            print(f"\nNo late payments found for '{org_name}' in Sem {semester}, AY {acad_year}.")
            return

        headers = [
            "Fee ID", "Student No", "Member Name", "Amount",
            "Due Date", "Payment Date", "Days Late", "AY", "Sem"
        ]

        table = []

        for row in results:
            due_date_str = row['due_date'].strftime("%Y-%m-%d")

            pd = row['payment_date']

            payment_date_str = pd.strftime("%Y-%m-%d") if pd else "N/A"

            dl = row.get('days_late')
            
            if dl is None and pd is None:
                dl = (date.today() - row['due_date']).days

            table.append([
                row['fee_id'],
                row['student_number'],
                row['member_name'],
                f"PHP {row['amount']:.2f}",
                due_date_str,
                payment_date_str,
                dl,
                row['academic_year'],
                row['semester']
            ])

        print(f"\n=== Late Payments for '{org_name}' (Sem {semester}, AY {acad_year}) ===")
        print(tabulate(table, headers=headers, tablefmt="grid"))

    # REPORT 6: View percentage of active vs inactive members of the organization for the last n sems
    def view_percentage_active_inactive_members(self, orgID, org_name):
        data = self.db_manager.view_percentage_active_inactive_members(orgID)
        if not data: 
            print(f"No membership data found in {org_name}.")
            return
        
        headers = [
            "Academic Year",
            "Semester",
            "Active Members",
            "Inactive Members",
            "Total Members",
            "Active %",
            "Inactive %"
        ]

        table = []
        for row in data:
            table.append([
                row['academic_year'],
                row['semester'],
                row['active_members'],
                row['inactive_members'],
                row['total_members'],
                f"{row['active_percentage']:.2f}%",
                f"{row['inactive_percentage']:.2f}%"
            ])

        print(f"\n=== Active vs Inactive Members for '{org_name}' ===")
        print(tabulate(table, headers=headers, tablefmt="grid"))

    # REPORT 9: View the member(s) of an organization with the highest debt for a given sem/AY
    def view_highest_unpaid_fees_members(self, orgID, org_name):
        sem = input("Enter semester (e.g., 1): ")
        acad_year = input("Enter academic year (e.g., 20XX-20YY): ")

        results = self.db_manager.view_highest_unpaid_fees_members(orgID, sem, acad_year)

        if not results:
            print(f"\nNo unpaid fees found for '{org_name}' in Semester {sem} and AY {acad_year}.")
            return

        print(f"\n=== TOP 10 MEMBERS WITH HIGHEST UNPAID FEES IN '{org_name}' (Sem {sem}, AY {acad_year}) ===\n")
        headers = [
            "Student Number",
            "Name",
            "Degree Program",
            "Gender",
            "Total Debt"
        ]

        from tabulate import tabulate
        table_data = [[
            r['student_number'],
            r['member_name'],
            r['degree_program'],
            r['gender'],
            f"PHP {r['Debt this Semester']:.2f}"
        ] for r in results]

        print(tabulate(table_data, headers=headers, tablefmt="grid"))


    # ================== view_and_sort_all_members_menu ==================
    # ================== view_and_sort_all_members_menu ==================
    # ================== view_and_sort_all_members_menu ==================
    # ================== view_and_sort_all_members_menu ==================



# =============================================== HELPER FUNCTIONS =============================================== 
# =============================================== HELPER FUNCTIONS =============================================== 
# =============================================== HELPER FUNCTIONS =============================================== 
# =============================================== HELPER FUNCTIONS =============================================== 
# =============================================== HELPER FUNCTIONS =============================================== 
# =============================================== HELPER FUNCTIONS =============================================== 
# =============================================== HELPER FUNCTIONS =============================================== 

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
        try: 
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
                if self.db_manager.drop_organization(org_name): #t0d0: fix this to also drop all related fees, committees, member-committee stuff
                    #JK it aint even implemented idgaf it not in the specs
                    print("Organization deleted successfully.")
                else:
                    print("Deletion failed or organization not found.")
        except KeyboardInterrupt:
            print("\tDropping interrupted.")

    #  ================== MINI DIVIDER =========================
        
           
    def committee_and_role_assignment(self, orgID, org_name, newMember_studentnumber, join_date_obj=None):
        print("\n=== COMMITTEE & ROLE ASSIGNMENT ===")

        while True:
            academic_year = input("Enter academic year for committee residency (format YYYY-YYYY, e.g. 2024-2025): ").strip()
            if len(academic_year) == 9 and academic_year[4] == '-' and \
                academic_year[:4].isdigit() and academic_year[5:].isdigit() and \
                int(academic_year[5:]) == int(academic_year[:4]) + 1: 
                
                acad_year_start = int(academic_year[:4])
                acad_year_end = int(academic_year[5:])

                if join_date_obj: #exists
                    join_date_year = join_date_obj.year
                    if acad_year_end < join_date_year:
                        print(f"\tError: Committee assignment academic year ({academic_year}) ends before join year ({join_date_year}).")
                        continue
                
                break  #Valid academic year
            else:
                print("\tError: Academic year must be in the format YYYY-YYYY with consecutive years.")

        
        while True:
            semester = input("Enter semester ('First' or 'Second'): ").strip().capitalize()
            if semester in ['First', 'Second']:
                break
            print("\tError: Semester must be 'First' or 'Second'.")

        valid_statuses = ['Active', 'Inactive', 'Expelled', 'Suspended', 'Alumni']
        while True:
            membership_status = input(f"Enter membership status {valid_statuses}: ").strip().capitalize()
            if membership_status in valid_statuses:
                break
            print(f"\tError: Membership status must be one of {valid_statuses}.") 
        
        if membership_status != 'Active': #Skip committee/role if not Active
            print(f"\tNote: Member with status '{membership_status}' will not be assigned a committee or role.")
            if self.db_manager.register_member_under_committee_with_role(
                newMember_studentnumber, orgID, None, None, academic_year, semester, membership_status):
                print(f"\tSuccessfully registered member with status '{membership_status}'.")
                return int(academic_year[:4])
            else:
                print("\tFailed to register member with status.")
                return False

        committees_with_roles = self.db_manager.get_committees_and_roles_by_orgID(orgID)
        if not committees_with_roles:
            print(f"\nNo committees registered under '{org_name}'. Cannot assign committee or role.")
            return None

        # actually organize the committess and their roles
        committee_roles_dict = {}
        for record in committees_with_roles:
            comm_name = record['committee_name']
            role_name = record['committee_role']
            committee_roles_dict.setdefault(comm_name, []).append(role_name)

        print("\nAvailable Committees and Their Roles:")
        for comm, roles in committee_roles_dict.items():
            print(f" + {comm}: {', '.join(roles) if roles else 'No roles'}")

        while True:
            assigned_committee = input("Enter committee to assign the member to: ").strip()
            if assigned_committee in committee_roles_dict:
                break
            print(f"Error: Committee '{assigned_committee}' not found. Please choose from the list.")

        available_roles = committee_roles_dict[assigned_committee]
        if available_roles:
            while True:
                assigned_role = input(f"Enter role in '{assigned_committee}' ({', '.join(available_roles)}): ").strip()
                if assigned_role in available_roles:
                    break
                print("Error: Invalid role. Please select from the available roles.")
        else:
            print(f"Note: Committee '{assigned_committee}' has no predefined roles.")
            assigned_role = None

        if self.db_manager.register_member_under_committee_with_role(
            newMember_studentnumber, orgID, assigned_committee, assigned_role, academic_year, semester, membership_status):
            print(f"\tSuccessfully assigned member to '{assigned_committee}' with role '{assigned_role or 'None'}'.")
            return int(academic_year[:4])
        else:
            print("\tFailed to assign member to committee and role.")
            return False

#  ================== MINI DIVIDER =========================

    def print_member_table_entry_contents_helper(self, student_number):
        #see if entry exists
        member_table_entry = self.db_manager.get_student_record_by_studentNumber(student_number)
        if member_table_entry: 
            member_table_entry['graduation_status'] = "Not Yet Graduated" if member_table_entry['graduation_status'] == 0 else "Graduated" #readability concern 
            member_table_entry['graduation_date'] = "N/A" if member_table_entry['graduation_date'] is None else member_table_entry['graduation_date']

            better_names = { # mapping the keys to more readable headers
                'first_name': 'First Name',
                'middle_name': 'Middle Name',
                'last_name': 'Last Name',
                'student_number': 'Student Number',
                'degree_program': 'Degree Program',
                'gender': 'Gender',
                'graduation_status': 'Graduation Status',
                'graduation_date': 'Graduation Date'
            }

            headers = [better_names.get(key, key) for key in member_table_entry.keys()]
            values = [member_table_entry[key] for key in member_table_entry.keys()]

            print(tabulate([values], headers=headers, tablefmt="grid"))
            return member_table_entry
        else:
            print(f"No record found for student number {student_number}.")
            return None

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

            print("\n\tStudent data collected successfully!") 

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


    #=============================IM PUTTING ALL MY REPORTS I MADE HERE - EDRIC EDRIC EDRIC 
    #=============================IM PUTTING ALL MY REPORTS I MADE HERE - EDRIC EDRIC EDRIC 
    #=============================IM PUTTING ALL MY REPORTS I MADE HERE - EDRIC EDRIC EDRIC 
    #=============================IM PUTTING ALL MY REPORTS I MADE HERE - EDRIC EDRIC EDRIC 
    #=============================IM PUTTING ALL MY REPORTS I MADE HERE - EDRIC EDRIC EDRIC 

    def get_unpaid_mem(self, orgID):
        try:
            while True:
                academic_year = input("Enter academic year to find (format YYYY-YYYY, e.g. 2024-2025): ").strip()
                if len(academic_year) == 9 and academic_year[4] == '-' and \
                academic_year[:4].isdigit() and academic_year[5:].isdigit() and \
                int(academic_year[5:]) == int(academic_year[:4]) + 1:
                    break
                print("Error: Academic year must be in the format YYYY-YYYY with consecutive years.") #iiyak n me
            while True:
                semester = input("\nEnter the semester (1 or 2): ")
                if semester in ["1", "2"]:
                    break
                print("Semester can only be 1 or 2.")

            results = self.db_manager.get_unpaid_mem(orgID,academic_year,semester)
            if len(results) == 0:
                print("None Found.")
                return None
            headers = ["Student Number", "Name", "Degree Program"]

            table_data = [[
                r['student_number'],
                r['member_name'],
                r['degree_program']
            ] for r in results]
            print(f"\n========== Unpaid Members of the {semester} semester of {academic_year} ===========")
            print(tabulate(table_data,headers,tablefmt="grid"))
            return None
        
        except KeyboardInterrupt:
           print("Cancelled Report.")

    def get_execs_by_acad_year(self, orgID): #REPORT 4
        try:  

            committees = self.db_manager.get_committees_by_orgID(orgID)
            committee_print = [r['committee_name']for r in committees] 
            if 'Executive' not in committee_print:
                print("\nThere is no 'Executive' committee in this org.")
                return None
            
            while True:
                academic_year = input("Enter academic year of the executives to find (format YYYY-YYYY, e.g. 2024-2025): ").strip()
                if len(academic_year) == 9 and academic_year[4] == '-' and \
                academic_year[:4].isdigit() and academic_year[5:].isdigit() and \
                int(academic_year[5:]) == int(academic_year[:4]) + 1:
                    break
                print("Error: Academic year must be in the format YYYY-YYYY with consecutive years.") #iiyak n me
            # while True:
            #     semester = input("\nEnter the semester (First or Second): ")
            #     if semester in ["First", "Second"]:
            #         break
            #     print("Semester can only be First or Second.")
            
            # results = self.db_manager.get_exec_by_acad_year(orgID,academic_year,semester)
            results = self.db_manager.get_exec_by_acad_year(orgID,academic_year)
            if len(results) == 0:
                print("None Found.")
                return None
            headers = ["Student Number", "Name", "Degree Program", "Gender"]
            table_data = [[
                r['student_number'],
                r['member_name'],
                r['degree_program'],
                r['gender']
            ] for r in results]
            print(f"\n========== Executive Members for AY {academic_year} ===========")
            print(tabulate(table_data,headers,tablefmt="grid"))
            return None
        except KeyboardInterrupt:
            print("Cancelled Report.")

    def get_members_by_role(self, orgID): #REPORT 5
        try:  
            while True: 
                committees = self.db_manager.get_committees_by_orgID(orgID)
                committee_print = [r['committee_name']for r in committees] 
                print(tabulate([[name]for name in committee_print], ["Committees"], tablefmt="outline"))
                committee = input("\nSelect a committee to choose a role from: ")
                if committee in committee_print:
                    while True:
                        roles = self.db_manager.get_committees_and_roles_by_orgID(orgID)
                        roles = [c['committee_role'] for c in roles if c['committee_name'] == committee]
                        print(tabulate([[name] for name in roles], [f"Roles in {committee} committee"], tablefmt="outline"))
                        role = input("\nChoose a role from the committee: ")
                        if role in roles:
                            results = self.db_manager.get_members_by_role_date(orgID, role)
                            if len(results) == 0:
                                print("None Found.")
                                return None
                            headers = ["Student Number", "Name", "Degree Program", "Gender", "Academic Year of Role"]
                            table_data = [[
                                r['student_number'],
                                r['member_name'],
                                r['degree_program'],
                                r['gender'],
                                r['academic_year']
                            ] for r in results]
                            print(f"\n======== History of Members in {committee} Committee ==========")
                            print(tabulate(table_data,headers,tablefmt="grid"))
                            return None
                            
                        print("Role not found.")
                print("\nCommittee not found.")
        except KeyboardInterrupt:
            print("\nCancelled report.")
                        

    def get_alumni_from_date(self, orgID): #REPORT 7
        try:
            while True:
                date_input = input("Enter date (YYYY-MM-DD): ").strip()
                try:
                    from datetime import datetime
                    datetime.strptime(date_input, "%Y-%m-%d")
                    date = date_input
                    break
                except ValueError:
                    print("Error: Please enter a valid date in YYYY-MM-DD format.")
            result = self.db_manager.get_alumni_from_date(orgID, date)
            headers = [
                "Student Number",
                "Name",
                "Degree Program",
                "Gender",
                "Graduation Date",
                "Batch Joined"
            ]

            from tabulate import tabulate
            table_data = [[
                r['student_number'],
                r['member_name'],
                r['degree_program'],
                r['gender'],
                r['graduation_date'],
                r['batch_year']
            ] for r in result]
            print(tabulate(table_data, headers=headers, tablefmt="grid"))
            return None
        except KeyboardInterrupt:
            print("Cancelling Report.")
            return None

    def get_amount_fee(self, orgID): # REPORT 8 - GET TOTAL PAID/UNPAID FEES AS OF GIVEN DATE
        print("\n=======GENERATING REPORT=======")

        try:
            while True:
                date_input = input("Enter date (YYYY-MM-DD) or press Enter for today's date: ").strip()
                from datetime import datetime, date as dt_date
                
                if not date_input: # Allow default to today if no date is entered
                    date = dt_date.today().strftime("%Y-%m-%d")
                    print(f"Using today's date: {date}")
                    break

                try:
                    datetime.strptime(date_input, "%Y-%m-%d")
                    date = date_input
                    break
                except ValueError:
                    print("Error: Please enter a valid date in YYYY-MM-DD format.")

            result = self.db_manager.get_amount_fee(orgID, date)

            if result:
                print(f"\n=== FEES AS OF {date} ===\n")
                headers = ["Org Name", "Paid", "Unpaid"]
                table_data = [[r['org_name'], r['paid'], r['unpaid']] for r in result]
                print(tabulate(table_data, headers=headers, tablefmt="grid"))
            else:
                print("No data available for the specified date and organization.")

            return None

        except KeyboardInterrupt:
            print("\nCancelling Report.")
            return None

# =============================================================


    def run(self):
        if not self.db_manager.connect():
            return
        else:
            print("Successfully connected to the database!")
            print("Note: When in doubt/want to cancel an operation: hit CTRL + C.")
            # print(self) #why are we print(self) ing :crying_laughing:
        try:
            
                while True:
                    try: 
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
                    except KeyboardInterrupt:
                        print("\nCTRL + C triggered! Going back to main menu.") 
        finally:
            self.db_manager.close_connection()


# ==== is this proper? idgaf.

app = MainApplication()
app.run()

