import bcrypt
import sqlite3

# The following class handles all database operations related to logging in and signing up
class LoginPage:
    # Data Members
    # Remember that Python data members are public by default
    # A single underscore before data member makes it protected
    # A double underscore makes it private
    __db_connection = None
    __db_cursor = None
    __logged_in = None

    # The constructor establishes connection to the database if it exists
    # Otherwise it creates the database
    def __init__(self):
        self.__db_connection = sqlite3.connect("LoginProject.sqlite")  # Establishes connection to database file
        self.__db_cursor = self.__db_connection.cursor()    # Cursor to connection object. Allows us to interact with db.

        self.__logged_in = False  # Flag that maintains if the user is logged in or not

        # SQL Queries to set up database if it does not exist
        init_script = '''
            CREATE TABLE IF NOT EXISTS Accounts (
                username VARCHAR2(50) NOT NULL UNIQUE PRIMARY KEY,
                password VARCHAR2(50) NOT NULL
            )
        '''

        # The executescript function takes a script, executes it, returns a new cursor object
        self.__db_cursor.executescript(init_script)       # Executes create table script

    # Creates a new account from given username and password
    # If username is already taken, returns false
    def create_account(self, username, password):
        # The execute function takes a single SQL statement, executes it, returns a new cursor object
        res = self.__db_cursor.execute('SELECT * FROM Accounts WHERE username = ?', (username, ))
        # cursor.fetchone() returns one tuple from the relation that the cursor contains
        row = res.fetchone()

        # Create account will only occur if username exists
        if(row == None):
            # The next two lines encrypt the given password
            password = bytes(password, 'utf-8')
            hashed_password = bcrypt.hashpw(password, bcrypt.gensalt())

            # The username and encrypted password are stored into the database.
            self.__db_cursor.execute('INSERT INTO Accounts VALUES(?, ?)', (username, hashed_password))
            self.__db_connection.commit()     # Remember to always commit the changes

            return True
        else:
            return False

    def login(self, username, password):
        res = self.__db_cursor.execute('SELECT * FROM Accounts WHERE username = ?', (username, ))
        row = res.fetchone()
        # row is a list where each element represents each attribute of the tuple

        status = 0   # status is 1 if login successful, 2 if username does not exist, 3 if incorrect password.
        # Login will only occur if the username exists
        if(row != None):
            # Now, we will check if the given password matches the password in the database
            password = bytes(password, 'utf-8')
            if(bcrypt.checkpw(password, row[1])):
                self.__logged_in = True
                status = 1
            else:
                status = 3
        else:
            status = 2
        
        return status

    def return_accounts(self):
        usernames = []
        rows = self.__db_cursor.execute("SELECT username FROM Accounts")
        for line in rows.fetchall():
            usernames.append(line[0])

        return usernames

    def logout(self):
        self.__logged_in = False

    def is_logged_in(self):
        return self.__logged_in


def main():
    login_obj = LoginPage()

    choice = input('Enter 1 for signup, 2 for login: ')
    
    if choice == '1':
        username = input('Username: ')
        password = input('Password: ')

        if login_obj.create_account(username, password):
            print('Account Created')
        else:
            print('Username is taken')
    
    else:
        username = input('Username: ')
        password = input('Password: ')

        status = login_obj.login(username, password)

        if status == 1:
            print('Logged In')
        elif status == 2:
            print('Account does not exist')
        else:
            print('Incorrect Password')

if __name__ == "__main__":
    main()