import sqlite3

class Participant:
    _db_connection = None
    _db_cursor = None

    def __init__(self):
        self._db_connection = sqlite3.connect("main_server.sqlite")
        self._db_cursor = self._db_connection.cursor()

        initscript = '''
            CREATE TABLE IF NOT EXISTS Participants (
                PID integer NOT NULL,
                EventID integer NOT NULL,
                PRIMARY KEY(PID, EventID)
            );

            CREATE TABLE IF NOT EXISTS Participant_Type (
                PID integer NOT NULL PRIMARY KEY AUTOINCREMENT,
                Ptype integer NOT NULL
            );
        '''
        # Note that in the participant type table Ptype 1 indicates students, 2 for faculty, else outsiders.

        self._db_cursor.executescript(initscript)


class Student(Participant):
    def __init__(self):
        super().__init__()

        initscript = '''
            CREATE TABLE IF NOT EXISTS Student (
                Roll_no VARCHAR2(9) NOT NULL PRIMARY KEY,
                Name VARCHAR2(256) NOT NULL,
                Contact_num VARCHAR2(20),
                Email VARCHAR2(100),
                Department VARCHAR2(50),
                Semester INTEGER
            );

            CREATE TABLE IF NOT EXISTS ID_Student (
                PID integer NOT NULL PRIMARY KEY, 
                Roll_no VARCHAR2(9) NOT NULL UNIQUE
            );
        '''

        self._db_cursor.executescript(initscript)

    def register_student(self, student_args, event_id):
        roll_no = student_args['roll_no'].upper()

        flag = 1  
        # 0 represents no student exists. 
        # 1 represents student exists, but no event. 
        # 2 represents student and event both exist
        
        self._db_cursor.execute('SELECT PID FROM ID_Student WHERE Roll_no = ?', (roll_no, ))

        pid = self._db_cursor.fetchone()
        if(pid == None):
            flag = 0
        else:
            self._db_cursor.execute('SELECT Event_ID FROM Participants WHERE PID = ?', (pid[0], ))
            for row in self._db_cursor.fetchall():
                if row[0] == event_id:
                    flag = 2
                    break

        if flag == 2:
            return False

        elif flag == 0:
            query = 'INSERT INTO Participant_Type (Ptype) VALUES (?)'
            self._db_cursor.execute(query, (1, ))
            self._db_cursor.execute('SELECT MAX(PID) FROM Participant_Type')
            pid = self._db_cursor.fetchone()[0]

            self._db_cursor.execute('INSERT INTO Participants (PID, EventID) VALUES (?, ?)', (pid, event_id, ))

            self._db_cursor.execute('INSERT INTO ID_Student (PID, Roll_no) VALUES (?, ?)', (pid, student_args['roll_no']))
            
            query = '''
                INSERT INTO Student (Roll_no, Name, Contact_num, Email, Department, Semester)
                VALUES (?, ?, ?, ?, ?, ?)
            '''
            self._db_cursor.execute(query, (student_args['roll_no'],
                                            student_args['name'],
                                            student_args['contact_no'],
                                            student_args['email'],
                                            student_args['dept'],
                                            student_args['sem']))
            
            self._db_connection.commit()

        else:
            self._db_cursor.execute('SELECT PID FROM ID_Student WHERE Roll_no = ?', (student_args['roll_no']))
            pid = self._db_cursor.fetchone()[0]

            self._db_cursor.execute('INSERT INTO Participants (PID, Event_ID) VALUES (?, ?)', pid, event_id)

            self._db_connection.commit()
        


class Faculty(Participant):
    def __init__(self):
        super().__init__()

        initscript = '''
            CREATE TABLE IF NOT EXISTS Faculty (
                F_ID VARCHAR2(9) NOT NULL PRIMARY KEY, 
                Name VARCHAR2(256) NOT NULL,
                Contact_num VARCHAR2(20),
                Department VARCHAR2(50)
            );

            CREATE TABLE IF NOT EXISTS ID_Faculty (
                PID integer NOT NULL PRIMARY KEY,
                F_ID VARCHAR2(9) NOT NULL UNIQUE
            );
        '''

        self._db_cursor.executescript(initscript)


class Outsider(Participant):
    def __init__(self):
        super().__init__()

        initscript = '''
            CREATE TABLE IF NOT EXISTS Outsider (
                Govt_ID VARCHAR2(12) NOT NULL PRIMARY KEY,
                Name VARCHAR2(256) NOT NULL,
                College VARCHAR2(256),
                Contact_num VARCHAR2(20),
                State VARCHAR2(50)
            );

            CREATE TABLE IF NOT EXISTS ID_Outsider (
                PID integer NOT NULL PRIMARY KEY,
                Govt_ID VARCHAR2(12) NOT NULL UNIQUE
            );
        '''

        self._db_cursor.executescript(initscript)


def main():
    std = Student()

    args = {}
    args['roll_no'] = 'M210708CA'
    args['name'] = 'Golu Singh'
    args['contact_no'] = '1235466878'
    args['email'] = 'golugolu@gmail.com'
    args['dept'] = "CSED"
    args['sem'] = 3

    std.register_student(args, 3)

if __name__ == '__main__':
    main()