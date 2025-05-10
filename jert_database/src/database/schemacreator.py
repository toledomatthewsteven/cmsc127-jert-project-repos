from mysql.connector import Error

def create_member_table(connection): 
    cursor = connection.cursor()
    try: 
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS member(
                first_name varchar(15) NOT NULL,
                middle_name varchar(15),
                last_name varchar(25) NOT NULL,
                student_number char(10) PRIMARY KEY NOT NULL,  
                degree_program varchar(30) NOT NULL,
                gender char(1) NOT NULL,
                graduation_status boolean DEFAULT 0,
                graduation_date date
            )
        """)

        connection.commit() 
        print("\tMember table created successfully in new database!")
    except Error as e:
        print(f"Error creating member table: {e}")
        raise
    finally:
        cursor.close()

def create_student_organization_table(connection):
    cursor = connection.cursor()
    try: 
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS student_organization(
            organization_id int PRIMARY KEY AUTO_INCREMENT NOT NULL, 
            org_name varchar(100) UNIQUE NOT NULL,
            org_type varchar(20) NOT NULL,
            semesters_active int NOT NULL,
            num_members int NOT NULL,
            year_established year NOT NULL,
            abbreviation varchar(10)
        )""")

        connection.commit() 
        print("\tStudent Organization table created successfully in new database!")
    except Error as e:
        print(f"Error creating student organization table: {e}")
        raise
    finally:
        cursor.close()

def create_fee_table(connection):

    cursor = connection.cursor()
    try: 
        cursor = connection.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS fee(
            fee_id int PRIMARY KEY AUTO_INCREMENT,
            amount int  NOT NULL,
            due_date date NOT NULL,
            semester int  NOT NULL,
            academic_year varchar(10) NOT NULL,
            payment_date date, 
            payment_status boolean DEFAULT 0, 
            late_status boolean DEFAULT 0,
            student_number char(10), 
            organization_id int 
            )
        """) #whatchumean we forgot to primary key the fe id..
        cursor.execute("ALTER TABLE fee ADD CONSTRAINT fee_id_fk FOREIGN KEY(student_number) REFERENCES member(student_number)")
        cursor.execute("ALTER TABLE fee ADD CONSTRAINT fee_org_fk FOREIGN KEY(organization_id) REFERENCES student_organization(organization_id)")

        connection.commit() 
        print("\tFee table created successfully in new database!")
    except Error as e:
        print(f"Error creating fee table: {e}")
        raise
    finally:
        cursor.close()

def create_committee_table(connection):
    cursor = connection.cursor()
    try: 
        cursor = connection.cursor()
        cursor.execute("""
            CREATE TABLE committee(
                committee_name varchar(30) PRIMARY KEY,
                organization_id int
            )
        """) 
        cursor.execute("ALTER TABLE committee ADD CONSTRAINT committee_org_fk FOREIGN KEY(organization_id) REFERENCES student_organization(organization_id)")
        
        connection.commit() 
        print("\tCommittee table created successfully in new database!")
    except Error as e:
        print(f"Error creating committee table: {e}")
        raise
    finally:
        cursor.close()

def create_committee_roles_table(connection):
    cursor = connection.cursor()
    try: 
        cursor = connection.cursor()
        cursor.execute("""
            CREATE TABLE committee_roles(
                committee_role varchar(30) NOT NULL,
                committee_name varchar(30) NOT NULL,

                CONSTRAINT committee_role_pk PRIMARY KEY(committee_name,committee_role)
            )
        """) 
        cursor.execute("ALTER TABLE committee_roles ADD CONSTRAINT committee_name_fk FOREIGN KEY(committee_name) REFERENCES committee(committee_name)")
        
        connection.commit() 
        print("\tCommittee role (relationship) table created successfully in new database!")
    except Error as e:
        print(f"Error creating committee role table: {e}")
        raise
    finally:
        cursor.close()

def create_membership_table(connection):
    cursor = connection.cursor()
    try: 
        cursor = connection.cursor()
        cursor.execute("""
            CREATE TABLE membership(
                student_number char(10),
                organization_id int,
                batch_year year NOT NULL,
                join_date date NOT NULL,
                CONSTRAINT mem_pk PRIMARY KEY(student_number,organization_id)
            )
        """) 
        cursor.execute("ALTER TABLE membership ADD CONSTRAINT membership_student_fk FOREIGN KEY(student_number) REFERENCES member(student_number)")
        cursor.execute("ALTER TABLE membership ADD CONSTRAINT membership_org_fk FOREIGN KEY(organization_id) REFERENCES student_organization(organization_id)")

        connection.commit() 
        print("\tMembership (relationship) table created successfully in new database!")
    except Error as e:
        print(f"Error creating membership table: {e}")
        raise
    finally:
        cursor.close()

def create_member_committee_table(connection):
    cursor = connection.cursor()
    try: 
        cursor = connection.cursor()
        cursor.execute("""
            CREATE TABLE member_committee(
                student_number char(10),
                committee_name varchar(30),
                academic_year varchar(10),
                semester varchar(20),
                membership_status varchar(10),
                committee_role varchar(30),
                CONSTRAINT mem_comm_pk PRIMARY KEY(student_number, committee_name,academic_year,semester)
            )
        """) 
        cursor.execute("ALTER TABLE member_committee ADD CONSTRAINT memcomm_student_fk FOREIGN KEY(student_number) REFERENCES member(student_number)")
        cursor.execute("ALTER TABLE member_committee ADD CONSTRAINT memcomm_comm_fk FOREIGN KEY(committee_name) REFERENCES committee(committee_name)")

        connection.commit() 
        print("\tMember-committee (relationship) table created successfully in new database!")
    except Error as e:
        print(f"Error creating member-committee table: {e}")
        raise
    finally:
        cursor.close()