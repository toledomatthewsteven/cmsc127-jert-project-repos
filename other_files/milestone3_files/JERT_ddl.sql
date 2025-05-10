--JERT : CMSC 127 ST13L

-- TODO: CANT DO INLINE MULTIPLE PRIMARY KEY DEFINING, SO CREATE CONSTRAINT LINES (or inlines... wherever)
-- TODO: ADD NOT NULL CONSTRAINTS WHERE APPROPRIATE 
-- TODO: MAKE ORGANIZATION_ID AN AUTO_INCREMENTING THING

--MEMBER

CREATE TABLE member(
    first_name varchar(15) NOT NULL,
    middle_name varchar(15),
    last_name varchar(25) NOT NULL,
    student_number char(10) PRIMARY KEY NOT NULL,  
    degree_program varchar(30) NOT NULL,
    gender char(1) NOT NULL,
    graduation_status boolean DEFAULT 0,
    graduation_date date
);

--ORGANIZATION
-- TODO: AUTO INCR ORG ID, ALSO ADD NOT NULLS
 --TODO: please make unique, edric
CREATE TABLE student_organization(
    organization_id int PRIMARY KEY AUTO_INCREMENT NOT NULL, 
    org_name varchar(100) UNIQUE NOT NULL,
    org_type varchar(20) NOT NULL,
    semesters_active int NOT NULL,
    num_members int NOT NULL,
    year_established year NOT NULL,
    abbreviation varchar(10)
);

--FEE
--Semester is int for simplicity purposes
--Acad Year is varchar(10) string for things like "2024-2025"
-- NULL NOT PAID
-- boolean is automatically 0 = false, 1 = true
CREATE TABLE fee(
    fee_id int AUTO_INCREMENT,
    amount int  NOT NULL,
    due_date date NOT NULL,
    semester int  NOT NULL,
    academic_year varchar(10) NOT NULL,
    payment_date date, 
    payment_status boolean DEFAULT 0, 
    late_status boolean DEFAULT 0,
    student_number char(10), 
    organization_id int 
);

ALTER TABLE fee ADD CONSTRAINT fee_id_fk FOREIGN KEY(student_number) REFERENCES member(student_number);
ALTER TABLE fee ADD CONSTRAINT fee_org_fk FOREIGN KEY(organization_id) REFERENCES student_organization(organization_id);

-- COMMITTEE
CREATE TABLE committee(
    committee_name varchar(30) PRIMARY KEY,
    organization_id int
);

ALTER TABLE committee ADD CONSTRAINT committee_org_fk FOREIGN KEY(organization_id) REFERENCES student_organization(organization_id);


-- COMMITTEE ROLE
--inquire about this primary key thing that wont work? or smth? whatever edric said
--lol we didnt inquire about it .... or did we? idk

CREATE TABLE committee_roles(
    committee_role varchar(30) NOT NULL,
    committee_name varchar(30) NOT NULL,

    CONSTRAINT committee_role_pk PRIMARY KEY(committee_name,committee_role)
);

ALTER TABLE committee_roles ADD CONSTRAINT committee_name_fk FOREIGN KEY(committee_name) REFERENCES committee(committee_name);

--MEMBERSHIP (mem_org_relation) 

CREATE TABLE membership(
    student_number char(10),
    organization_id int,
    batch_year year NOT NULL,
    join_date date NOT NULL,
    CONSTRAINT mem_pk PRIMARY KEY(student_number,organization_id)
);

ALTER TABLE membership ADD CONSTRAINT membership_student_fk FOREIGN KEY(student_number) REFERENCES member(student_number);
ALTER TABLE membership ADD CONSTRAINT membership_org_fk FOREIGN KEY(organization_id) REFERENCES student_organization(organization_id);



-- MEMCOMMITTEEE
--TODO: change active status from boolean to string ("inactive", active, etc)

CREATE TABLE member_committee(
    student_number char(10),
    committee_name varchar(30),
    academic_year varchar(10),
    semester varchar(20),
    membership_status varchar(10),
    committee_role varchar(30),
    CONSTRAINT mem_comm_pk PRIMARY KEY(student_number, committee_name,academic_year,semester)
);

ALTER TABLE member_committee ADD CONSTRAINT memcomm_student_fk FOREIGN KEY(student_number) REFERENCES member(student_number);
ALTER TABLE member_committee ADD CONSTRAINT memcomm_comm_fk FOREIGN KEY(committee_name) REFERENCES committee(committee_name);



