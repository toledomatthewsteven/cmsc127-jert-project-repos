--JERT : CMSC 127 ST13L

-- REPORT 1:
-- View all members of the organization by role, status, gender, degree program, batch (year of
-- membership), and committee. (Note: we assume one committee membership only per organization per semester)

--User-interaction flow:
    --User picks View Organization Details
    --User enters organization name (case-sensitive, everything-sensitive):
        --Search for an organization with that id.
        --If found, we extract that id and store that for the rest of our interactions. 
        --If not found, we just send them back to the main menu

        SELECT organization_id FROM student_organization WHERE "Organization Name"=org_name;
        --should return a unique organization id
        --store that organization id into variable referenced_organization_id

    --Assuming we have extracted the organization ID...
    --User picks report 1 (or whatever report)
        --USER CHOICE: View by role: (this is by, given an acad year and semester)
            --so i guess also ask for acad year and semester in the terminal/whatever input method

            SELECT 
                m.student_number,
                CASE 
                    WHEN m.middle_name IS NULL THEN CONCAT(m.last_name, ', ', m.first_name)
                    ELSE CONCAT(m.last_name, ', ', m.first_name, ' ', m.middle_name)
                END AS member_name,
                c.committee_name,
                mpc.committee_role,
                m.degree_program,
                m.gender,
                mpc.academic_year,
                mpc.semester,
            FROM 
                member m
            JOIN 
                MEM_PART_OF_COMMITTEE mpc ON m.student_number = mpc.student_number
            JOIN 
                COMMITTEE c ON mpc.committee_name = c.committee_name
            JOIN 
                COMMITTEE_COMMITTEE_ROLE ccr ON c.committee_name = ccr.committee_name 
                                            AND mpc.committee_role = ccr.committee_role
            WHERE 
                c.organization_id = referenced_organization_id
                AND mpc.academic_year = referenced_academic_year
                AND mpc.semester = referenced_semester
            ORDER BY 
                c.committee_name,
                mpc.committee_role,
                m.last_name,
                m.first_name;

        --uhmmm 
        --USER CHOICE: View by degree program  
            SELECT 
                m.student_number,
                CASE 
                    WHEN m.middle_name IS NULL THEN CONCAT(m.last_name, ', ', m.first_name)
                    ELSE CONCAT(m.last_name, ', ', m.first_name, ' ', m.middle_name)
                END AS member_name,
                m.degree_program,
                m.gender,
                c.committee_name,
                mpc.committee_role,
                mpc.academic_year,
                mpc.semester,
            FROM 
                member m
            JOIN 
                MEM_PART_OF_COMMITTEE mpc ON m.student_number = mpc.student_number
            JOIN 
                COMMITTEE c ON mpc.committee_name = c.committee_name
            JOIN 
                COMMITTEE_COMMITTEE_ROLE ccr ON c.committee_name = ccr.committee_name 
                                            AND mpc.committee_role = ccr.committee_role
            WHERE 
                c.organization_id = referenced_organization_id
                AND mpc.academic_year = referenced_academic_year
                AND mpc.semester = referenced_semester
            ORDER BY 
                m.degree_program,
                m.last_name,
                m.first_name;

        --general thought pattern: the query depends on what its looking for and whether it has
        --necessary associations like a committee role is associated with a committee
        --also, the main thing we're changing is the Order By thing,,,

        --TBF: view by status, gender, batch (year of membership), and committee name alone, and others



--REPORT 2: View members for a given organization with unpaid membership fees or dues 
--for a given semester and academic year.

--this version just assumes the org id, acad year, and semester is a given...

    SELECT 
        m.student_number, 
        CASE 
            WHEN m.middle_name IS NULL THEN CONCAT(m.last_name, ', ', m.first_name)
            ELSE CONCAT(m.last_name, ', ', m.first_name, ' ', m.middle_name)
        END AS member_name,
        m.degree_program, 
    FROM
        member m 
    JOIN 
        fee f ON (m.student_number = f.student_number)  
    WHERE 
        f.payment_status = FALSE AND 
        f.academic_year = "2024-2025" AND
        f.semester = 1 AND 
        f.organization_id = 1
    GROUP BY
        m.student_number;


--REPORT 3: View a member’s unpaid membership fees or dues for *ALL* their organizations 
--(Member’s POV).

--Assumptions, through the terminal/input, user provides their student-number
    SELECT 
        m.student_number,
        CASE 
            WHEN m.middle_name IS NULL THEN CONCAT(m.last_name, ', ', m.first_name)
            ELSE CONCAT(m.last_name, ', ', m.first_name, ' ', m.middle_name)
        END AS member_name,
        so.org_name,
        f.semester,
        f.academic_year,
        f.fee_id,
        f.amount,
        f.due_date,
        f.late_status
    FROM 
        member m
    JOIN 
        fee f ON m.student_number = f.student_number
    JOIN 
        student_organization so ON f.organization_id = so.organization_id
    WHERE 
        m.student_number = '202X-12345' 
        AND f.payment_status = FALSE  
    ORDER BY 
        so.org_name, 
        f.due_date;


--REPORT 4: View all executive committee members of a given organization for a given academic year.
    --Assuming org id is given and as well as acad year and semester

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
        member_committee memcom ON m.student_number = memcom.student_number
    JOIN
        commitee comm ON memcom.commitee_name = comm.commitee_name
    WHERE 
        referenced_organization_id = comm.organization_id AND
        memcom.academic_year = "2024-2025" AND
        memcom.semester = 1 AND  
        comm.commitee_name = "EXECUTIVE" ;



-- REPORT 5. View all Presidents (or any other role) of a given organization 
-- for every academic year in reverse chronological order (current to past).
    --Assuming org id is given 

    SELECT 
        m.student_number,
        CASE 
            WHEN m.middle_name IS NULL THEN CONCAT(m.last_name, ', ', m.first_name)
            ELSE CONCAT(m.last_name, ', ', m.first_name, ' ', m.middle_name)
        END AS member_name,
        m.degree_program, 
        m.gender,
        memcom.academic_year
    FROM 
        member m
    JOIN 
        member_committee memcom ON m.student_number = memcom.student_number
    JOIN 
        committee comm ON memcom.committee_name = comm.committee_name
    WHERE 
        memcom.committee_role = 'PRESIDENT' and
        comm.organization_id = referenced_organization_id
    ORDER BY
        memcom.academic_year DESC;


-- REPORT 6. View all late payments made by all members of a given organization 
-- for a given semester and academic year.

--Assuming organization id, academic year, and semester is given
--For a payment to be counted, it has to be:
    --PAID, LATE, UNDER THE ORG, IN THE ACAD YEAR & IN THE SEMESTER SPECIFIED

    SELECT 
        f.fee_id,
        f.amount,
        f.academic_year,
        f.semester,
        f.due_date,
        f.payment_date, 
        DATEDIFF(f.payment_date, f.due_date) as days_late,
        m.student_number, 
        CASE 
            WHEN m.middle_name IS NULL THEN CONCAT(m.last_name, ', ', m.first_name)
            ELSE CONCAT(m.last_name, ', ', m.first_name, ' ', m.middle_name)
        END AS member_name,
    FROM
        fee f
    JOIN 
        member m ON f.student_number = m.student_number
    WHERE 
        f.academic_year = '2024-2025' AND
        f.semester = 1 AND 
        f.organization_id = referenced_organization_id AND
        f.payment_status = true AND
        f.late_status = true AND 
        f.payment_date > f.due_date  
    ORDER BY
        f.payment_date;



--REPORT 7: View the percentage of active vs inactive members of a given organization for 
-- the last n semesters. (Note: n is a positive integer)

--Assuming the user provides the "n" number themselves and "n" passes validations
--Assuming organization ID is given via whatever extraction method

    WITH semester_loop () AS (
        SELECT DISTINCT academic_year, semester
        FROM member_committee
        WHERE organization_id = <referenced_organization_id>
        ORDER BY academic_year DESC, semester DESC
        LIMIT <n-variable> 
    )

    SELECT 
        sl.academic_year,
        sl.semester,
        COUNT(CASE WHEN m.active_status = "ACTIVE" THEN 1 END) AS active_members,
        COUNT(CASE WHEN m.active_status = 'INACTIVE' THEN 1 END) AS inactive_members,
        COUNT(*) AS total_members,
        ROUND(  (COUNT(CASE WHEN m.active_status = "ACTIVE" THEN 1 END) * 1.0 / COUNT(*))*100, 2  ) AS active_percentage,
        ROUND(  (COUNT(CASE WHEN m.active_status = "INACTIVE" THEN 1 END) * 1.0 / COUNT(*))*100, 2  ) AS inactive_percentage
    FROM 
        semester_loop sl
    JOIN 
        member_committee m ON sl.academic_year = m.academic_year 
        AND sl.semester = m.semester
        AND m.organization_id = <referenced_organization_id>
    GROUP BY 
        sl.academic_year,
        sl.semester
    ORDER BY 
        sl.academic_year DESC,
        sl.semester DESC;



--REPORT 8: View all alumni members of a given organization as of a given date.
    --assumed that a graduation_date is null until the member actually graduates college (when some1 can update the system for real)
    --assuming org id is given, assuming a date input is given (however that works)

    SELECT 
        m.student_number,
        CASE 
            WHEN m.middle_name IS NULL THEN CONCAT(m.last_name, ', ', m.first_name)
            ELSE CONCAT(m.last_name, ', ', m.first_name, ' ', m.middle_name)
        END AS member_name,
        m.degree_program, 
        m.gender,
        m.graduation_date, 
        mship.batch_year,
    FROM 
        member m  
    JOIN
        membership mship ON m.student_number = mship.student_number
    WHERE
        mship.organization_id = referenced_organization_id AND 
        m.graduation_date IS NOT NULL AND 
        m.graduation_date <= user_inputed_date_variable_here
    ORDER BY
        m.graduation_date, 
        m.last_name,
        m.first_name


--REPORT 9: View the total amount of unpaid and paid fees or 
--dues of a given organization as of a given date.

    --Exclude fees due AFTER that date given
    SELECT 
        so.org_name,
        SUM(CASE WHEN f.payment_status = TRUE THEN f.amount ELSE 0 END) AS paid,
        SUM(CASE WHEN f.payment_status = FALSE THEN f.amount ELSE 0 END) AS unpaid
    FROM 
        fee f
    JOIN 
        student_organization so ON f.organization_id = so.organization_id
    WHERE 
        f.organization_id = referenced_organization_id AND 
        f.due_date <= user_inputed_date_variable_here
    GROUP BY 
        so.org_name; 


--REPORT 10: View the member/s with the highest debt of a given organization for a given semester.
    --assuming org id, acad year, and semester will be given

    SELECT 
        m.student_number,
        CASE 
            WHEN m.middle_name IS NULL THEN CONCAT(m.last_name, ', ', m.first_name)
            ELSE CONCAT(m.last_name, ', ', m.first_name, ' ', m.middle_name)
        END AS member_name,
        m.degree_program, 
        m.gender,
        f.academic_year,
        f.semester,
        SUM(CASE WHEN (f.payment_status = false AND f.late_status = true) THEN f.amount ELSE 0 END) as `Debt this Semester`
    FROM 
        member m 
    JOIN 
        fee f ON m.student_number = f.student_number
    WHERE
        f.payment_status = false AND
        f.academic_year = '2024-2025' AND
        f.semester = 1 AND 
        f.organization_id = referenced_organization_id AND
    GROUP BY: 
        m.student_number
        f.academic_year,
        f.semester
    ORDER BY
        `Debt this Semester` DESC
    LIMIT 10;


