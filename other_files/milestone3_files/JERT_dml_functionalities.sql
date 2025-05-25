--JERT : CMSC 127 ST13L

-- 1) MEMBERSHIP MANAGEMENT
-- a. Add, update, delete, and search for members

-- Given these relational tables
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

CREATE TABLE membership(
    student_number char(10),
    organization_id int,
    batch_year year NOT NULL,
    join_date date NOT NULL,
    CONSTRAINT mem_pk PRIMARY KEY(student_number,organization_id)
);

CREATE TABLE member_committee(
    student_number char(10),
    committee_name varchar(30),
    academic_year varchar(10),
    semester varchar(20),
    membership_status varchar(10),
    committee_role varchar(30),
    CONSTRAINT mem_comm_pk PRIMARY KEY(student_number, committee_name,academic_year,semester)
);

-- ADD
-- Inserts member 


INSERT INTO member (first_name, middle_name, last_name, student_number, degree_program, gender, graduation_status, graduation_date) 
            VALUES ('John Adrian', 'Bodrigues', 'Caduzale', '202512345','BS Quantum Computing', 'M', false, NULL);

--only add if this if that member does not exist yet (thus, check for student number )unique_

-- Adds into membership table
INSERT INTO membership (student_number, organization_id, batch_year, join_date)
            VALUES ('2025-12345', 1, 2025, CURDATE())

-- Assigns to committee
INSERT INTO member_committee (student_number, committee_name, academic_year, semester, membership_status, committee_role)
            VALUES ('202512345', 'Academics', '2025-2026', 1, 'Active', 'Committee Director')

-- UPDATE
-- Updates a member in the org
UPDATE member SET
    first_name='Stephen Jayden',
    middle_name='Colledo',
    last_name='Fanttico',
    degree_program='BS Computer Engineering',
    gender='M',
    graduation_status=true,
    graduation_date= CURDATE()
WHERE
    student_number='202512345';

--  Updates the correspoding membership
UPDATE membership SET
  batch_year='2024-2025',
WHERE
  student_number='202512345'
  AND organization_id= 1;

-- Updates committee
UPDATE member_committee SET
  academic_year='2027-2028',
  semester=2,
  membership_status= 'Inactive',
  committee_role= 'Member'
WHERE
  student_number='202512345' AND 
  committee_name='Academics' AND 
  academic_year='2025-2026' AND 
  semester=1;

-- DELETE
-- Removes the member
DELETE FROM member WHERE student_number='202512345';

-- Removes from membership
DELETE FROM membership WHERE student_number= '202512345' AND organization_id=1;

-- Removes committee assignment
DELETE FROM member_committee WHERE
  student_number='202512345' AND 
  committee_name='Academics'AND 
  academic_year='2024-2025'AND 
  semester=1;

-- SEARCH
-- Gets memeber's info and the org they belong to
-- Will show member even if they have no org record
SELECT
    m.student_number,
    m.first_name,
    m.middle_name,
    m.last_name,
    mem.organization_id AS `Organization ID`,
    so.org_name AS `Organization Name`
FROM member AS m
LEFT JOIN membership AS mem
    ON m.student_number=mem.student_number
LEFT JOIN student_organization AS so
    ON mem.organization_id=so.organization_id
WHERE m.student_number='202512345'
   OR m.last_name='Fanttico';

-- b. Track members' roles (e.g., President, Treasurer, Member)
-- Given these relational tables
CREATE TABLE member_committee(
    student_number char(10),
    committee_name varchar(30),
    academic_year varchar(10),
    semester varchar(20),
    membership_status varchar(10),
    committee_role varchar(30),
    CONSTRAINT mem_comm_pk PRIMARY KEY(student_number, committee_name,academic_year,semester)
);

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

-- Assuming that the committee member has already provided his/her role in the committee
SELECT  
    m.student_number AS `Student Number`,  
    m.first_name AS `First Name`,  
    m.last_name AS `Last Name`,  
    mcomm.committee_role AS `Role`,  
    mcomm.committee_name AS `Committee`,  
    mcomm.semester AS `Semester`,  
    mcomm.academic_year AS `Acad Year`  
FROM 
    member_committee AS mcomm  
JOIN 
    member AS m ON mcomm.student_number=m.student_number  
ORDER BY m.last_name, m.first_name, mcomm.academic_year DESC, mcomm.semester;

-- c. Track membership status (active, inactive, expelled, suspended, alumni)
-- Assuming that the committee member has already provided his/her status 
SELECT  
    mcomm.membership_status AS `Status`,  
    m.first_name AS `First Name`,  
    m.last_name AS `Last Name`,  
    mcomm.semester AS `Semester`,  
    mcomm.academic_year    AS `Academic Year`  
FROM 
    member_committee AS mcomm  
JOIN 
    member AS m ON mcomm.student_number=m.student_number  
ORDER BY mcomm.academic_year DESC, mcomm.semester , m.last_name, m.first_name;

-- 2. FEES MANAGEMENT
-- a. Manage membership fees and dues
-- Given the fee table
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

-- Will show the unpaid fees past deadline 
SELECT
    f.fee_id AS `Fee ID`,
    f.student_number AS `Student Number`,
    f.amount AS `Fees Amount `,
    f.due_date AS `Due Date`,
    DATEDIFF( CURDATE(), f.due_date) AS `Days Late`,
FROM fee AS f
WHERE 
   f.payment_status=FALSE AND (f.due_date < CURDATE())
ORDER BY f.due_date;

-- b. Generate reports on the organization's financial status
-- Reference table
CREATE TABLE student_organization(
    organization_id int PRIMARY KEY AUTO_INCREMENT NOT NULL, 
    org_name varchar(100) UNIQUE NOT NULL,
    org_type varchar(20) NOT NULL,
    semesters_active int NOT NULL,
    num_members int NOT NULL,
    year_established year NOT NULL,
    abbreviation varchar(10)
);

-- Report on org's total fees, paid and unpaid fees,
SELECT
  org.organization_id AS `Org ID`,
  org.org_name AS `Organization`,
  SUM(f.amount) AS `Total Fees`,
  SUM( CASE 
        WHEN f.payment_status=TRUE 
        THEN f.amount 
        ELSE 0 
      END) AS `Total Fees Paid`,
  SUM(CASE 
        WHEN f.payment_status=FALSE 
        THEN f.amount 
        ELSE 0 
      END) AS `Total Fees Unpaid`
FROM student_organization AS org
LEFT JOIN fee AS f ON org.organization_id= f.organization_id
GROUP BY org.org_name;
