import mysql.connector
import pandas as pd
from sqlalchemy import create_engine

db_user = ""
db_password = ""
db_host = ""
db_name = ""

myDB = {
    "user": db_user,
    "password": db_password,
    "host": db_host,
    "database": db_name
}
connect = mysql.connector.connect(**myDB)
cursor = connect.cursor()

# table for records
createTableRecords = """
CREATE TABLE employee_records (
ID INT(6) UNSIGNED ZEROFILL NOT NULL AUTO_INCREMENT PRIMARY KEY,
Given_Name VARCHAR(255) NOT NULL,
Surname VARCHAR(255) NOT NULL,
Age tinyINT NOT NULL,
Gender ENUM("Male", "Female") NOT NULL,
Job_Title ENUM ("Retail Banking", "Corporate Banking", "Marketing And Communication", "Investment Banking", "Credit Risk", "Information Technology") NOT NULL,
Status ENUM("Active", "On Leave", "Non Active") NOT NULL DEFAULT "Active"
)
"""
cursor.execute(createTableRecords)

queryInitialData = "INSERT INTO employee_records VALUES (%s, %s, %s, %s, %s, %s, %s)"
val = [
    ("000001", "Jordan", "Peterson", 34, "Male", "Retail Banking", "Active"),
    ("000002", "Samantha", "Cole", 29, "Female", "Corporate Banking", "Active"),
    ("000003", "Avery", "Clark", 27, "Male", "Marketing and Communication", "On Leave"),
    ("000004", "Alex", "Martinez", 42, "Male", "Investment Banking", "Active"),
    ("000005", "Riley", "Thompson", 37, "Female", "Credit Risk", "Active"),
    ("000006", "Drew", "Sullivan", 39, "Male", "Marketing and Communication", "Active"),
    ("000007", "Taylor", "Nguyen", 31, "Male", "Retail Banking", "Non Active"),
    ("000008", "Morgan", "Lee", 45, "Female", "Credit Risk", "Active"),
    ("000009", "Casey", "Patel", 33, "Female", "Information Technology", "On Leave"),
    ("000010", "Jamie", "Brooks", 28, "Male", "Marketing and Communication", "Active"),
]
cursor.executemany(queryInitialData, val)
connect.commit()

# table for user account
createTableLogin = """
CREATE TABLE user_account (
Username VARCHAR(255) NOT NULL PRIMARY KEY,
Password VARCHAR(255) NOT NULL
)
"""
cursor.execute(createTableLogin)



dictGender = {
    1: "Male",
    2: "Female"
}

dictJobTitle = {
    1: "Retail Banking",
    2: "Corporate Banking",
    3: "Marketing And Communication",
    4: "Investment Banking",
    5: "Credit Risk",
    6: "Information Technology" 
}

dictStatus = {
    1: "Active",
    2: "Non Active",
    3: "On Leave"
}

dictColumnName = {
    1: "ID",
    2: "Given_Name",
    3: "Surname",
    4: "Age",
    5: "Gender",
    6: "Job_Title",
    7: "Status"
}


# verify username
def validate_username(newUsername):
    if len(newUsername) < 6 or len(newUsername) > 20:
        print("Username must consist of 6-20 characters!")
        return False
    
    if not any(char.isdigit() for char in newUsername) or not any(char.isalpha() for char in newUsername):
        print("Username must be a combination of letters and numbers!")
        return False
    
    for char in newUsername:
        if not char.isalnum():
            print("Username may only contain letters and numbers!")
            return False
    
    queryUser = "SELECT Username FROM user_account WHERE Username = %s"
    cursor.execute(queryUser, [newUsername])
    result = cursor.fetchone()
    if result:
        print("Username is already registered!")
        return False
    
    return True

# verify password
def validate_password(newPassword):
    if len(newPassword) < 8:
        print("Password must be at least 8 characters!")
        return False
    
    has_upper = has_lower = has_digit = has_special = False
    for char in newPassword:
        if char.isupper():
            has_upper = True
        elif char.islower():
            has_lower = True
        elif char.isdigit():
            has_digit = True
        elif char in "!@#$%^&*()?":
            has_special = True

    if not has_upper:
        print("Password must contain uppercase letter!")
        return False
    if not has_lower:
        print("Password must contain lowercase letter!")
        return False
    if not has_digit:
        print("Password must contain number!")
        return False
    if not has_special:
        print("Password must contain special character!")
        return False
    
    return True


# read
def readMenu():
    while True:
        try:
            print("Options:\n1. Show all employee\n2. Find employee\n3. Back to Home")
            choice = int(input("Enter your choice: "))
            if choice == 1:
                readSubMenu_listAllEmployee()
            elif choice == 2:
                readSubMenu_searchEmployee()
            elif choice == 3:
                return
            else:
                print("No menu chosen!")
        except ValueError:
            print("Enter number only!")

# read submenu 1
def readSubMenu_listAllEmployee():
    cursor.execute("SELECT * FROM employee_records")
    data_Karyawan = cursor.fetchall()
    if not data_Karyawan:
        print("No record found.")
        return
    else:
        queryReadAll = "SELECT * FROM employee_records"
        engine = create_engine(f"mysql+pymysql://{db_user}:{db_password}@{db_host}/{db_name}")
        df = pd.read_sql(queryReadAll, engine)
        df["ID"] = df["ID"].astype(str).str.zfill(6)
        print(df)
        return

# read submenu 2
def readSubMenu_searchEmployee():
    while True:
        try:
            print("Search by:\n1. Employee ID\t\t5. Gender\n2. Given Name\t\t6. Job Title\n3. Surname\t\t7. Status\n4. Age\t\t\t8. Back")
            choice = int(input("Enter your choice: "))

            # personalize search by
            def searchEmployee(searchBy):
                while True:
                    if searchBy == "Gender":
                        print("List of Gender:\n1. Male\n2. Female")
                    elif searchBy == "Job_Title":
                        print("List of Job Title:\n1. Retail Banking\t\t4. Investment Banking\n2. Corporate Banking\t\t5. Credit Risk\n3. Marketing And Communication\t6. Information Technology")
                    elif searchBy == "Status":
                        print("List of Status:\n1. Active\n2. Non Active\n3. On Leave")

                    userInput = input(f"Enter {searchBy}: (Q to quit) ")
                    if userInput.lower() == "q":
                        return
                    else:
                        if searchBy == "Gender":
                            userInputInt = int(userInput)
                            if userInputInt in dictGender:
                                userInput = dictGender[userInputInt]

                        elif searchBy == "Job_Title":
                            userInputInt = int(userInput)
                            if userInputInt in dictJobTitle:
                                userInput = dictJobTitle[userInputInt]

                        elif searchBy == "Status":
                            userInputInt = int(userInput)
                            if userInputInt in dictStatus:
                                userInput = dictStatus[userInputInt]
                        
                        queryFindEmployee = f"SELECT * FROM employee_records WHERE {searchBy} = %s"
                        cursor.execute(queryFindEmployee, (userInput,))
                        result = cursor.fetchall()
                        if result:
                            engine = create_engine("mysql+pymysql://{db_user}:{db_password}@{db_host}/{db_name}")
                            with engine.connect() as connection:
                                df = pd.read_sql(queryFindEmployee, connection, params=(userInput,))
                                df["ID"] = df["ID"].astype(str).str.zfill(6)
                                print(df)
                                return
                        else:
                            print("No record found!")
                            return

            if choice in dictColumnName:
                searchEmployee(dictColumnName[choice])
            elif choice == 8:
                return
            else:
                print("No input chosen!")
        
        except ValueError:
            print("Enter number only!")


# create
def createMenu():
    while True:
        try:
            print("Options:\n1. Add New Employee Information\n2. Back to Home")
            choice = int(input("Enter your choice: "))
            if choice == 1:
                createSubMenu_newEmployee()
            elif choice == 2:
                return
            else:
                print("No menu chosen!")
        except ValueError:
            print("Enter number only!")

# create submenu 1
def createSubMenu_newEmployee():
    newGivenName = input("Given Name: ").capitalize()
    newSurname = input("Surname: ").capitalize()
    
    while True:
        try:
            newAge = int(input("Age: "))
            break
        except ValueError:
            print("Enter number only!")

    while True:
        try:
            print("1. Male\n2. Female")
            newGender = int(input("Gender: "))
            break
        except ValueError:
            print("Enter number only!")

    while True:
        try:
            print("List of Job Title:\n1. Retail Banking\t\t4. Investment Banking\n2. Corporate Banking\t\t5. Credit Risk\n3. Marketing And Communication\t6. Information Technology")
            newJobTitle = int(input("Job Title: "))
            break
        except ValueError:
            print("Enter number only!")

    while True:
        try:
            print("List of Status:\n1. Active\n2. Non Active\n3. On Leave")
            newStatus = int(input("Status: "))
            break
        except ValueError:
            print("Enter number only!")

    # insert to table
    while True:
        choice = input("Save record? [Y/N] ").upper()
        if choice == "N":
            return
        elif choice == "Y":
            for key, val in dictGender.items():
                if key == newGender:
                    newGender = val
            for key, val in dictJobTitle.items():
                if key == newJobTitle:
                    newJobTitle = val
            for key, val in dictStatus.items():
                if key == newStatus:
                    newStatus = val

            insertNewData = "INSERT INTO employee_records (Given_Name, Surname, Age, Gender, Job_Title, Status) VALUES (%s, %s, %s, %s, %s, %s)"
            cursor.execute(insertNewData, [newGivenName, newSurname, newAge, newGender, newJobTitle, newStatus])
            connect.commit()
            print("Employee added successfully!")
            return
        else:
            print("Enter Y/N only!")


# update
def updateMenu():
    while True:
        try:
            print("Options:\n1. Update Employee Information\n2. Back to Home")
            choice = int(input("Enter your choice: "))
            if choice == 1:
                updateSubMenu_updateInfo()
            elif choice == 2:
                return
            else:
                print("No menu chosen!")
        except ValueError:
            print("Enter number only!")

# update submenu 1
def updateSubMenu_updateInfo():
    while True:
        employeeID = input("Enter Employee ID to update: (Q to quit) ")
        if employeeID.lower() == "q":
            return
    
        # verify if employeeID exist
        queryFindEmployee = "SELECT * FROM employee_records WHERE ID = %s"
        cursor.execute(queryFindEmployee, (employeeID,))
        employee = cursor.fetchone()

        if employee:
            print(f"Employee Details:")
            print(f"Employee ID : {employee[0]:06d}")
            print(f"Full Name   : {employee[1]} {employee[2]}")
            print(f"Age         : {employee[3]}")
            print(f"Gender      : {employee[4]}")
            print(f"Job Title   : {employee[5]}")
            print(f"Status      : {employee[6]}")

            while True:
                confirmation = input("Do you want to update this record? [Y/N] ").lower()
                if confirmation == "y":
                    while True:
                        try:
                            print("List of Column:\n1. Given Name\t4. Gender\n2. Surname\t6. Job Title\n3. Age\t\t7. Status")
                            columnChoice = int(input("Enter number of designated column to update: "))
                        except ValueError:
                            print("Enter number only!")

                        # handle input to column
                        if columnChoice == 1:
                            while True:
                                newValue = input(f"Enter new value: ").capitalize()
                                if not newValue:
                                    print("Value cannot be empty!")
                                
                                columnChoice = "Given_Name"
                                break

                        elif columnChoice == 2:
                            while True:
                                newValue = input(f"Enter new value: ").capitalize()
                                if not newValue:
                                    print("Value cannot be empty!")

                                columnChoice = "Surname"
                                break

                        elif columnChoice == 3:
                            while True:
                                try:
                                    newValue = int(input("Enter new value: "))
                                    if newValue > 0:
                                        columnChoice = "Age"
                                        break
                                    else:
                                        print("Age must be positive!")
                                except ValueError:
                                    print("Invalid age!")

                        elif columnChoice == 4:
                            print("Select Gender:")
                            for key, val in dictGender.items():
                                print(f"{key}. {val}")
                            while True:
                                try:
                                    genderInput = int(input("Enter your choice: "))
                                    if genderInput in dictGender:
                                        newValue = dictGender[genderInput]
                                        columnChoice = "Gender"
                                        break
                                    else:
                                        print("No input chosen!")
                                except ValueError:
                                    print("Enter number only!")

                        elif columnChoice == 5:
                            print("Select Job Title:")
                            for key, val in dictJobTitle.items():
                                print(f"{key}. {val}")
                            while True:
                                try:
                                    jobInput = int(input("Enter your choice: "))
                                    if jobInput in dictJobTitle:
                                        newValue = dictJobTitle[jobInput]
                                        columnChoice = "Job_Title"
                                        break
                                    else:
                                        print("No input chosen!")
                                except ValueError:
                                    print("Enter number only!")

                        elif columnChoice == 6:
                            print("Select Status:")
                            for key, val in dictStatus.items():
                                print(f"{key}. {val}")
                            while True:
                                try:
                                    statusInput = int(input("Enter your choice: "))
                                    if statusInput in dictStatus:
                                        newValue = dictStatus[statusInput]
                                        columnChoice = "Status"
                                        break
                                    else:
                                        print("No input chosen!")
                                except ValueError:
                                    print("Enter number only!")

                        # confirm update
                        while True:
                            reconfirm = input("Save changes? [Y/N] ").lower()
                            if reconfirm == "y":
                                queryUpdate = f"UPDATE employee_records SET {columnChoice} = %s WHERE ID = %s"
                                cursor.execute(queryUpdate, (newValue, employeeID))
                                connect.commit()
                                print("Record has been updated.")
                                return
                            elif reconfirm == "n":
                                print("Undo changes...")
                                return
                            else:
                                print("Enter Y/N only!")
                
                elif confirmation == "n":
                    print("Update canceled.")
                    break
                else:
                    print("Enter Y/N only!")
                    
        else:
            print("No record found!")


# delete
def deleteMenu():
    while True:
        try:
            print("Options:\n1. Remove Record\n2. Clear All Records\n3. Back to Home")
            choice = int(input("Enter your choice: "))
            if choice == 1:
                deleteSubMenu_removeRecord()
            elif choice == 2:
                deleteSubMenu_clearRecord()
            elif choice == 3:
                return
            else:
                print("No menu chosen!")
        except ValueError:
            print("Enter number only!")

# delete submenu 1
def deleteSubMenu_removeRecord():
    while True:
        try:
            employeeID = int(input("Enter Employee ID to delete: "))
            queryFindEmployee = "SELECT * FROM employee_records WHERE ID = %s"
            cursor.execute(queryFindEmployee, (employeeID,))
            employee = cursor.fetchone()
            
            if employee:
                print(f"Employee Details:")
                print(f"Employee ID : {employee[0]:06d}")
                print(f"Name        : {employee[1]} {employee[2]}")
                print(f"Age         : {employee[3]}")
                print(f"Gender      : {employee[4]}")
                print(f"Job Title   : {employee[5]}")
                print(f"Status      : {employee[6]}")
                
                while True:
                    confirm = input(f"Delete this record? [Y/N] ").lower()
                    if confirm == "y":
                        queryDelete = "DELETE FROM employee_records WHERE ID = %s"
                        cursor.execute(queryDelete, (employeeID,))
                        connect.commit()
                        print(f"Record has been deleted.")
                        return
                    elif confirm == "n":
                        print("Undo changes...")
                        return
                    else:
                        print("Enter Y/N only!")
            else:
                print(f"No employee found with ID {employeeID}!")
        
        except ValueError:
            print("Wrong ID format!")

# delete submenu 2
def deleteSubMenu_clearRecord():
    while True:
        confirm = input("Delete all records? [Y/N] ").lower()
        if confirm == "y":
            queryDeleteAll = "DELETE FROM employee_records"
            cursor.execute(queryDeleteAll)
            connect.commit()
            print("Deleting all records...")
            return
        elif confirm == "n":
            print("Deletion canceled.")
            return
        else:
            print("Enter Y/N only!")


# menu after login
def home():
    while True:
        try:
            print("Home:\n1. Explore Employee\n2. New Records\n3. Modify Records\n4. Delete Records\n5. Log Out")
            choice = int(input("Enter your choice: "))
            if choice == 1:
                readMenu()
            elif choice == 2:
                createMenu()
            elif choice == 3:
                updateMenu()
            elif choice == 4:
                deleteMenu()
            elif choice == 5:
                print("Bye~")
                startProgram()
            else:
                print("No menu chosen!")
        except ValueError:
            print("Enter number only!")

# login
def Login():
    while True:
        username = input("Username: (Q to quit) ")
        if username.lower() == "q":
            return
        else:
            queryUsername = "SELECT Username FROM user_account WHERE Username = %s"
            cursor.execute(queryUsername, [username])
            result = cursor.fetchone()
            
            # verify user existence
            if not result:
                print("Username not found!")
            else:
                while True:
                    password = input("Password: (Q to quit) ")
                    if password.lower() == "q":
                        return
                    else:
                        queryLogin = "SELECT * FROM user_account WHERE Username = %s AND Password = %s"
                        cursor.execute(queryLogin, (username, password))
                        result = cursor.fetchone()
                        if result:
                            print("WELCOME!")
                            home()
                        else:
                            print("Wrong password!")

# register account
def SignUp():
    while True:
        newUsername = input("Create username: ")
        if validate_username(newUsername):
            break

    while True:
        newPassword = input("Create password: ")
        if validate_password(newPassword):
            break

    while True:
        save = input("Sign Up? [Y/N] ").lower()
        if save == "n":
            print("Sign up cancelled.")
            return
        elif save == "y":
            querySignUp = "INSERT INTO user_account VALUES (%s, %s)"
            cursor.execute(querySignUp, [newUsername, newPassword])
            connect.commit()
            print("Sign up successful!")
            return
        else:
            print("Enter Y/N only!")

# start program
def startProgram():
    while True:
        try:
            print("--WELCOME TO PURWADHIKA BANK EMPLOYEES' DATABASE--\nHome:\n1. Log In \n2. Sign Up\n3. Exit")
            choice = int(input("Enter your choice: "))
            if choice == 1:
                Login()
            elif choice == 2:
                SignUp()
            elif choice == 3:
                print("Thank you, bye!")
                exit()
            else:
                print("No menu chosen!")
        except ValueError:
            print("Enter number only!")

startProgram()