import streamlit as st
import sqlite3
import pandas as pd
import os
from datetime import date


database = "gym_membership.db"
#Backend section
def get_connection():
    con = sqlite3.connect(database)
    con.execute("PRAGMA foreign_keys = ON;")
    return con

def init_db():
    #connect this file to the database
    con = get_connection()
    #create a cursor to run queries
    cur = con.cursor()


    #create the tables
    cur.execute("""
    CREATE TABLE IF NOT EXISTS Person( 
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        gender TEXT check (gender in ('M','F')),
        address TEXT,
        Bdate date,
        Email TEXT CHECK (Email LIKE '%_@_%._%'),
        phone TEXT
    );""")

    cur.execute("""
    CREATE TABLE IF NOT EXISTS Member(
        M_ID INTEGER PRIMARY KEY AUTOINCREMENT,
        id INTEGER UNIQUE,
        subscription_date DATE,
        subscription_type TEXT CHECK (subscription_type IN ('Monthly','Yearly')),
        rank TEXT CHECK (rank IN ('Classic','Silver','Gold')),
        FOREIGN KEY (id) REFERENCES Person(id) ON DELETE CASCADE
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS Staff(
        SSN TEXT PRIMARY KEY,
        id INTEGER UNIQUE,
        hire_date DATE,
        Salary REAL,
        FOREIGN KEY (id) REFERENCES Person(id) ON DELETE CASCADE
    );
    """)
    
    cur.execute("""
    CREATE TABLE IF NOT EXISTS Worker(
        SSN TEXT PRIMARY KEY,
        Type TEXT,
        FOREIGN KEY (SSN) REFERENCES STAFF(SSN) ON DELETE CASCADE
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS Coach(
        SSN TEXT PRIMARY KEY,
        Type TEXT,
        FOREIGN KEY (SSN) REFERENCES STAFF(SSN) ON DELETE CASCADE
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS Coached_by(
        SSN TEXT,
        M_ID INTEGER,
        price REAL,
        end_date DATE,
        PRIMARY KEY (SSN, M_ID),
        FOREIGN KEY (SSN) REFERENCES STAFF(SSN) ON DELETE CASCADE, 
        FOREIGN KEY (M_ID) REFERENCES MEMBER(M_ID) ON DELETE CASCADE
    );
    """)

    con.commit()
    con.close()

# -------ADDERS---------
#add members
def add_member(name, gender, address, Bdate, Email, phone, subscription_type, rank):
    con = get_connection()
    cur = con.cursor()
    now = date.today()

    cur.execute(
    "INSERT INTO Person (name, gender, address, Bdate, Email, phone) values (?, ?, ?, ?, ?, ?)", 
    (name, gender, address, Bdate, Email, phone)
    )

    person_id = cur.lastrowid
    

    cur.execute(
    "INSERT INTO Member (id, subscription_date, subscription_type, rank) values (? ,?, ?, ?)",
    (person_id, now, subscription_type, rank)
    )
    
    con.commit()
    con.close()

#add a staff
def add_staff(name, gender, address, Bdate, Email, phone, SSN, salary, is_coach, type):
    con = get_connection()
    cur = con.cursor()
    now = date.today()

    cur.execute(
    "INSERT INTO Person (name, gender, address, Bdate, Email, phone) values (?, ?, ?, ?, ?, ?)", 
    (name, gender, address, Bdate, Email, phone)
    )

    person_id = cur.lastrowid

    cur.execute(
    "INSERT INTO Staff (SSN, id, hire_date, salary) values (?,?,?,?)",
    (SSN, person_id, now, salary)
    )

    if(is_coach):
        cur.execute(
        "INSERT INTO Coach (SSN, type) values (?,?)",
        (SSN, type)
        )
    else:
        cur.execute(
        "INSERT INTO Worker (SSN, type) values (?, ?)",
        (SSN, type)   
        )

    con.commit()
    con.close()

# -------UPDATERS--------
#update member values
def update_member(M_ID, name, gender, address, Bdate, Email, phone, subscription_type, rank):
    con = get_connection()
    cur = con.cursor()

    cur.execute("SELECT id FROM Member WHERE M_ID=?",(M_ID.strip(),))

    row = cur.fetchone()
    if row:
        ID = row[0]
        cur.execute("""
        Update Person
        SET name = ?, gender = ?, address = ?, Bdate = ?, Email = ?, phone = ?
        where id = ?
        """,(name, gender, address, Bdate, Email, phone, ID))

        cur.execute("""
        UPDATE Member
        SET subscription_type =?,rank=?
        where id = ?
        """,(subscription_type,rank,ID))
        
        result =  "Member data changed successfully"
    else:
        result = "user does not exist or invalid input"
    con.commit()
    con.close()
    return result

#update coach and worker values
def update_staff(staff_SSN, name, gender, address, birthday, email, phone, salary ,type):
    con = get_connection()
    cur = con.cursor()

    cur.execute("""SELECT id FROM staff WHERE SSN=? """,(staff_SSN.strip(),))

    row = cur.fetchone()
    
    if row:
        staff_id = row[0]
        cur.execute("""
        UPDATE person
        SET name = ?, gender = ?, address = ?, Bdate = ?, Email = ?, phone = ?
        where id = ?            
        """,(name,gender,address,birthday,email,phone,staff_id))

        cur.execute("""
        UPDATE staff
        set salary = ?
        where id = ?
        """,(salary, staff_id))

        checker = staff_check_type(staff_SSN)

        if checker == "worker":
            cur.execute("""
            UPDATE worker
            set type = ?
            where SSN = ?
            """,(type, staff_SSN))
            result = "staff updated successfully"
        elif checker == "coach":
            cur.execute("""
            UPDATE coach
            set type = ?
            where SSN = ?
            """,(type, staff_SSN))
            result = "staff updated successfully"
    else:
        result = "staff input invalid or does not exist"
    con.commit()
    con.close()
    return result

#helper function to find staff type if its coach or worker      
def staff_check_type(SSN):
    con = get_connection()
    cur = con.cursor()
    
    cur.execute("""
    select * from worker where SSN = ?
    """,(SSN,))
        
    checker = cur.fetchone()

    if checker:
        con.commit()
        con.close()
        return "worker"
    else:
        cur.execute("""select * from coach where SSN=?""",(SSN,))
        checker = cur.fetchone()

        if checker:
            con.commit()
            con.close()
            return "coach"
    con.commit()
    con.close()
    return None

# -------GETTERS---------
#simply get a single person or the entire 
def get_worker(SSN=None):
    con = get_connection()
    cur = con.cursor()

    if SSN is None:
        cur.execute("""
        SELECT Worker.SSN, Person.name, Person.gender, Person.address, Person.Bdate, Person.Email, Person.phone, Staff.hire_date, Staff.salary, Worker.Type 
        FROM Worker
        INNER JOIN Staff ON Worker.SSN = Staff.SSN
        INNER JOIN Person ON Staff.ID = Person.id
        """)
        result = cur.fetchall()
    else:
        cur.execute("""
        SELECT Worker.SSN, Person.name, Person.gender, Person.address, Person.Bdate, Person.Email, Person.phone, Staff.hire_date, Staff.salary, Worker.Type 
        FROM Worker
        INNER JOIN Staff ON Worker.SSN = Staff.SSN
        INNER JOIN Person ON Staff.id = Person.id
        WHERE Worker.SSN = ?
        """, (SSN,))
        result = cur.fetchone()
    con.close()
    return result

#Coach getters
def get_coach(SSN=None):
    con = get_connection()
    cur = con.cursor()

    if SSN is None:
        cur.execute("""
        SELECT Coach.SSN, Person.name, Person.gender, Person.address, Person.Bdate, Person.Email, Person.phone, Staff.hire_date, Staff.salary, Coach.Type 
        FROM Coach
        INNER JOIN Staff ON Coach.SSN = Staff.SSN
        INNER JOIN Person ON Staff.id = Person.id
        """)
        result = cur.fetchall()
    else:
        cur.execute("""
        SELECT Coach.SSN, Person.name, Person.gender, Person.address, Person.Bdate, Person.Email, Person.phone, Staff.hire_date, Staff.salary, Coach.Type 
        FROM Coach
        INNER JOIN Staff ON Coach.SSN = Staff.SSN
        INNER JOIN Person ON Staff.id = Person.id
        WHERE Coach.SSN = ?
        """, (SSN,)
        )
        result = cur.fetchone()
    con.close()
    return result  


#member getters  
def get_member(M_ID=None):
    con = get_connection()
    cur = con.cursor()

    if M_ID is None:
        cur.execute("""
        SELECT Member.M_ID, Person.name, Person.gender, Person.address, Person.Bdate, Person.Email, Person.phone, Member.subscription_date, Member.subscription_type, Member.rank
        FROM Member
        INNER JOIN Person ON Member.id = Person.id
        """) 
        result = cur.fetchall()
    else:    
        cur.execute("""
        SELECT Member.M_ID, Person.name, Person.gender, Person.address, Person.Bdate, Person.Email, Person.phone, Member.subscription_date, Member.subscription_type, Member.rank
        FROM Member
        INNER JOIN Person ON Member.id = Person.id
        WHERE Member.M_ID  = ?
        """, (M_ID,)) 
        result = cur.fetchone()
    con.close()
    return result

#  -------REMOVERS---------

#remove member
def remove_member(M_ID):
    con = get_connection()
    cur = con.cursor()

    cur.execute("SELECT id FROM Member WHERE M_ID=?",(M_ID,))

    row = cur.fetchone()

    if row:
        ID=row[0]
        cur.execute("DELETE FROM Person WHERE id=?",(ID,))
        con.commit()
        con.close()
        return f'User {M_ID} has been deleted successfully'
    else:
        con.close()
        return f'User {M_ID} does not exist or invalid input'

#remove staff
def remove_staff(SSN):
    con = get_connection()
    cur = con.cursor()

    cur.execute("SELECT id from Staff WHERE SSN=?",(SSN,))

    row=cur.fetchone()

    if row:
        ID=row[0]
        cur.execute("DELETE FROM Person WHERE id=?",(ID,))
        con.commit()
        con.close()
        return f'Staff {SSN} has been deleted successfully'
    else:
        con.close()
        return f'Staff {SSN} does not exist or invalid input'

#delete database
def delete_database():
    if os.path.exists(database):
        os.remove(database)
        return "Database deleted successfully."
    else:
        return "Database file does not exist."    

#add examples
def add_example_database():
    add_member("Alice Johnson", "F", "123 Maple St", "1992-04-15", "alice.johnson@example.com", "555-1234", "Monthly", "Classic")
    add_member("Bob Smith", "M", "456 Oak Ave", "1988-09-30", "bob.smith@example.com", "555-5678", "Yearly", "Silver")
    add_member("Carol Lee", "F", "789 Pine Rd", "1995-01-22", "carol.lee@example.com", "555-9012", "Monthly", "Gold")
    add_member("David Brown", "M", "321 Cedar Blvd", "1990-07-10", "david.brown@example.com", "555-3456", "Yearly", "Classic")
    add_member("Eva Green", "F", "654 Birch Ln", "1993-12-05", "eva.green@example.com", "555-7890", "Monthly", "Silver")
    add_staff("John Carter", "M", "100 Elm St", "1980-03-12", "[john.carter@example.com](mailto:john.carter@example.com)", "555-2001", "SSN001", 3500, True, "Fitness")
    add_staff("Maria Lopez", "F", "200 Spruce Ave", "1985-06-25", "[maria.lopez@example.com](mailto:maria.lopez@example.com)", "555-2002", "SSN002", 3200, False, "Maintenance")
    add_staff("Steve Nguyen", "M", "300 Walnut Rd", "1990-11-18", "[steve.nguyen@example.com](mailto:steve.nguyen@example.com)", "555-2003", "SSN003", 3600, True, "Yoga")
    add_staff("Linda Kim", "F", "400 Cherry Blvd", "1982-01-09", "[linda.kim@example.com](mailto:linda.kim@example.com)", "555-2004", "SSN004", 3100, False, "Reception")
    add_staff("Mark Thompson", "M", "500 Poplar Ln", "1988-08-30", "[mark.thompson@example.com](mailto:mark.thompson@example.com)", "555-2005", "SSN005", 3700, True, "Strength Training")

    return "examples added successfully"

#Frontend section

#data base initalized
init_db()

#UI
with st.sidebar:
    choice_people = st.selectbox("select who to affect",["choose","Member","Staff"])
    st.write("developer commands")
    clicked_reset = st.button("reset database")
    if clicked_reset:
        st.write(delete_database())
    clicked_example = st.button("add example staff and members")
    if clicked_example:
        st.write(add_example_database())
    

match choice_people:
    #default option
    case "choose":
        st.title("Gym Membership & Staff manager")
        st.write("Open the sidebar to get started")
    #all member options
    case "Member":
        choice_action_member = st.selectbox("what would you like to do",["choose","view members","add new member","update member data","delete a member"])
        match choice_action_member:
            #viewing a member(s)
            case "view members":
                st.write("Table of all members")
                columns = ["Member_ID","Name", "Gender", "Address", "Birthday","Email", "Phone","Subscription_date","Rank","Type"]
                data = get_member()
                members=pd.DataFrame(data, columns=columns)
                st.dataframe(members, width=1500)
                search=st.text_input("looking for a specific member? write their Membership ID")
                if search:
                    data = get_member(search)
                    if data:
                        member = pd.DataFrame(data ,index=columns, columns=["Found"])
                        st.table(member)
                    else:
                        st.write("User not found or input is invalid")
            #adding a new member
            case "add new member":
                with st.form("add member"):
                    st.write("Your info")
                    name = st.text_input("Name")
                    gender = st.radio("Gender",["Male","Female"])
                    address = st.text_input("Address")
                    birthday = st.date_input("Birthday")
                    email = st.text_input("Email")
                    phone = st.text_input("Phone number")
                    st.write("Your subscription preference")
                    rank = st.radio("Subscription rank",["Classic","Silver","Gold"])
                    type = st.radio("Subscription type",["Monthly","Yearly"])
                    st.write("Note that Yearly is a monthly payment for 12 months")
                    submitted = st.form_submit_button("submit")
                    
                    if submitted:
                        missing_fields = []
                        if not name.strip(): missing_fields.append("Name")
                        if not gender: missing_fields.append("Gender")
                        if not address.strip(): missing_fields.append("Address")
                        if not email.strip(): missing_fields.append("Email")
                        if not phone.strip(): missing_fields.append("Phone number")
                        if not rank: missing_fields.append("Subscription rank")
                        if not type: missing_fields.append("Subscription type")

                        if missing_fields:
                            st.error(f"Please fill all required fields: {', '.join(missing_fields)}")
                        else:
                            if gender == "Male":
                                gender = "M"
                            else:
                                gender = "F"
                            add_member(name, gender, address, birthday, email, phone, type, rank)
                            st.success("member added successfully")
            #updating a member
            case "update member data":
                with st.form("Update user value"):
                    member_ID = st.text_input("write the ID of the user you wish to modify")
                    member_ID = member_ID.strip()

                    st.write("New values below (keep the boxes you dont want to change empty or false)")
                    new_name = st.text_input("Name")
                    new_gender = st.radio("Gender",["no change","Male","Female"])
                    new_address = st.text_input("Address")
                    change_birthday = st.radio("change birthday?",["no","yes"])
                    new_birthday = st.date_input("Birthday")
                    new_email = st.text_input("Email")
                    new_phone = st.text_input("Phone number")
                    st.write("new subscription preference")
                    new_type = st.radio("Subscription type",["no change","Monthly","Yearly"])
                    new_rank = st.radio("Subscription rank",["no change","Classic","Silver","Gold"])
                    submitted = st.form_submit_button("submit")
                    if submitted:
                        member_data = get_member(member_ID)
                        if member_data:
                            old_name = member_data[1]
                            old_gender = member_data[2]
                            old_address = member_data[3]
                            old_birthday = member_data[4]
                            old_email = member_data[5]
                            old_phone = member_data[6]
                            old_type = member_data[8].strip()
                            old_rank = member_data[9].strip()
                            if new_name:
                                old_name = new_name
                            if new_gender != "no change":
                                if new_gender == "Male":
                                    old_gender = "M"
                                else:
                                    old_gender = "F"
                            if new_address:
                                old_address=new_address
                            if change_birthday == "yes":
                                old_birthday=new_birthday
                            if new_email:
                                old_email=new_email
                            if new_phone:
                                old_phone=new_phone
                            if new_type != "no change":
                                old_type=new_type
                            if new_rank != "no change":
                                old_rank = new_rank
                            st.write(update_member(member_ID, old_name, old_gender, old_address, old_birthday, old_email, old_phone, old_type ,old_rank))
            #deleting a member
            case "delete a member":
                st.write("once you press enter the user will be deleted so be sure you have the correct Member_ID")
                deleteMemberInput=st.text_input("write the Member_ID of the member you wish to delete")
                if deleteMemberInput:
                    st.write(remove_member(deleteMemberInput))
    #all staff options
    case "Staff":              
        choice_action_staff = st.selectbox("what would you like to do",["choose","view staff","add new staff","update staff data","delete a staff"])
        match choice_action_staff:
            #view a staff(s)
            case "view staff":
                columns = ["SSN","Name","Gender","Address","Birthdate","Email","Phone","HireDate","Salary","Type"]
                st.write("Table of all coaches")
                data_coach = get_coach()
                coaches=pd.DataFrame(data_coach,columns=columns)
                st.dataframe(coaches)

                st.write("Table of all workers")
                data_worker = get_worker()
                workers = pd.DataFrame(data_worker,columns=columns)
                st.dataframe(workers)

                st.write("looking for a certain staff?")
                search_staff_input = st.text_input("input the staff SSN")
                choice_search_staff = staff_check_type(search_staff_input)
                match choice_search_staff:
                    case "coach":
                        if search_staff_input:
                            coach_data = get_coach(search_staff_input)
                            coach = pd.DataFrame(coach_data,index=columns,columns=["Found"])
                            st.table(coach)
                    case "worker":
                        if search_staff_input:
                            worker_data = get_worker(search_staff_input)
                            worker = pd.DataFrame(worker_data,index=columns,columns=["Found"])
                            st.table(worker)
            #add a new staff
            case "add new staff":
                with st.form("add new staff"):
                    st.write("Your info")
                    name = st.text_input("Name")
                    gender = st.radio("Gender",["Male","Female"])
                    address = st.text_input("Address")
                    birthday = st.date_input("Birthday")
                    email = st.text_input("Email")
                    phone = st.text_input("Phone number")
                    st.write("work info")
                    SSN = st.text_input("SSN")
                    salary = st.text_input("salary")
                    work_type = st.radio("are you a coach or worker",["coach","worker"])
                    type = st.text_input("profession")

                    submitted = st.form_submit_button("submit")

                    if submitted:
                        missing_fields = []
                        if not name.strip(): missing_fields.append("Name")
                        if not gender: missing_fields.append("Gender")
                        if not address.strip(): missing_fields.append("Address")
                        if not email.strip(): missing_fields.append("Email")
                        if not phone.strip(): missing_fields.append("Phone number")
                        if not SSN.strip(): missing_fields.append("SSN")
                        if not salary.strip(): missing_fields.append("Salary")
                        if not work_type: missing_fields.append("Role type (coach/worker)")
                        if not type.strip(): missing_fields.append("Profession")

                        if missing_fields:
                            st.error(f"Please fill all required fields: {', '.join(missing_fields)}")
                        else:
                            if gender == "Male":
                                gender = "M"
                            else:
                                gender = "F"
                            try:
                                salary_val = float(salary)
                            except ValueError:
                                st.error("Salary must be a number.")
                            else:
                                is_coach = True if work_type.lower() == "coach" else False
                                add_staff(name, gender, address, birthday, email, phone, SSN, salary_val, is_coach, type)
                                st.success("Staff added successfully")
            #update staff data
            case "update staff data":
                with st.form("update staff info"):
                    staff_SSN = st.text_input("Input the SSN of the staff you want to change")
                    staff_SSN = staff_SSN.strip()

                    st.write("New values below (keep the boxes you dont want to change empty or false)")

                    new_staff_name = st.text_input("Name")
                    new_staff_gender = st.radio("Gender",["no change","Male","Female"])
                    new_staff_address = st.text_input("Address")
                    change_staff_birthday = st.radio("change birthday?",["no", "yes"])
                    new_staff_birthday = st.date_input("Birthday")
                    new_staff_email = st.text_input("Email")
                    new_staff_phone = st.text_input("Phone number")
                    st.write("work info")
                    new_staff_salary = st.text_input("salary")
                    new_staff_type = st.text_input("profession")

                    submitted_change = st.form_submit_button("submit")
                    if submitted_change:
                        checker = staff_check_type(staff_SSN)
                        if checker == "coach":
                            change_staff=get_coach(staff_SSN)
                        elif checker == "worker": 
                            change_staff=get_worker(staff_SSN)
                        else:
                            st.error("SSN input is invalid or user does not exist")  
                            st.stop()  
                        old_staff_name = change_staff[1]
                        old_staff_gender = change_staff[2]
                        old_staff_address = change_staff[3]
                        old_staff_birthday = change_staff[4]
                        old_staff_email = change_staff[5]
                        old_staff_phone = change_staff[6]
                        old_staff_salary = change_staff[8]
                        old_staff_type = change_staff[9]           
                        if new_staff_name:
                            old_staff_name = new_staff_name
                        if new_staff_gender != "no change":
                            if new_staff_gender == "Male":
                                old_staff_gender = "M"
                            else:
                                old_staff_gender = "F"
                        if new_staff_address:
                            old_staff_address=new_staff_address
                        if change_staff_birthday == "yes":
                            old_staff_birthday=new_staff_birthday
                        if new_staff_email:
                            old_staff_email=new_staff_email
                        if new_staff_phone:
                            old_staff_phone=new_staff_phone
                        if new_staff_salary:
                            old_staff_salary = new_staff_salary
                        if new_staff_type:
                            old_staff_type = new_staff_type
                        st.write(update_staff(staff_SSN, old_staff_name, old_staff_gender, old_staff_address, old_staff_birthday, old_staff_email, old_staff_phone, old_staff_salary ,old_staff_type))
            #delete staff from database
            case "delete a staff":
                st.write("once you press enter the staff will be deleted so be sure you have the correct SSN")
                deleteStaffInput=st.text_input("write the SSN of the member you wish to delete")
                if deleteStaffInput:
                    st.write(remove_staff(deleteStaffInput))
                