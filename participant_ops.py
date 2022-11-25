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
        # 1 represents student exists, but is not currently participating in given event.
        # 2 represents student exists and is already registered in given event.
        
        self._db_cursor.execute('SELECT PID FROM ID_Student WHERE Roll_no = ?', (roll_no, ))

        pid = self._db_cursor.fetchone()
        if(pid == None):
            flag = 0
        else:
            self._db_cursor.execute('SELECT EventID FROM Participants WHERE PID = ?', (pid[0], ))
            rows = self._db_cursor.fetchall()
            if rows != None:
                for row in rows:
                    if row[0] == event_id:
                        flag = 2
                        break

        if flag == 2:
            return False

        elif flag == 0:
            query = 'INSERT INTO Participant_Type (Ptype) VALUES (1)'
            self._db_cursor.execute(query)
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
                                            student_args['contact_num'],
                                            student_args['email'],
                                            student_args['dept'],
                                            student_args['sem']))
            
            self._db_connection.commit()
            return True

        else:
            self._db_cursor.execute('SELECT PID FROM ID_Student WHERE Roll_no = ?', (student_args['roll_no'], ))
            pid = self._db_cursor.fetchone()[0]

            self._db_cursor.execute('INSERT INTO Participants (PID, EventID) VALUES (?, ?)', (pid, event_id, ))

            self._db_connection.commit()
            return True
        


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

    def register_faculty(self, faculty_args, event_id):
        fid = faculty_args['fid'].upper()

        flag = 1
        # 0 represents no faculty exists. 
        # 1 represents faculty exists, but is not currently participating in given event.
        # 2 represents faculty exists and is already registered in given event.
        
        self._db_cursor.execute('SELECT PID FROM ID_Faculty WHERE F_ID = ?', (fid, ))

        pid = self._db_cursor.fetchone()
        if(pid == None):
            flag = 0
        else:
            self._db_cursor.execute('SELECT EventID FROM Participants WHERE PID = ?', (pid[0], ))
            rows = self._db_cursor.fetchall()
            if rows != None:
                for row in rows:
                    if row[0] == event_id:
                        flag = 2
                        break

        if flag == 2:
            return False

        elif flag == 0:
            query = 'INSERT INTO Participant_Type (Ptype) VALUES (2)'
            self._db_cursor.execute(query)
            self._db_cursor.execute('SELECT MAX(PID) FROM Participant_Type')
            pid = self._db_cursor.fetchone()[0]

            self._db_cursor.execute('INSERT INTO Participants (PID, EventID) VALUES (?, ?)', (pid, event_id, ))

            self._db_cursor.execute('INSERT INTO ID_Faculty (PID, F_ID) VALUES (?, ?)', (pid, faculty_args['fid'], ))
            
            query = '''
                INSERT INTO Faculty (F_ID, Name, Contact_num, Department)
                VALUES (?, ?, ?, ?)
            '''
            self._db_cursor.execute(query, (faculty_args['fid'],
                                            faculty_args['name'],
                                            faculty_args['contact_no'],
                                            faculty_args['dept']))
            
            self._db_connection.commit()
            return True

        else:
            self._db_cursor.execute('SELECT PID FROM ID_Faculty WHERE F_ID = ?', (faculty_args['fid'], ))
            pid = self._db_cursor.fetchone()[0]

            self._db_cursor.execute('INSERT INTO Participants (PID, EventID) VALUES (?, ?)', (pid, event_id))

            self._db_connection.commit()
            return True


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

    def register_outsider(self, outsider_args, event_id):
        govt_id = outsider_args['govt_id'].upper()

        flag = 1
        # 0 represents no outsider exists with given data. 
        # 1 represents outsider exists, but is not currently participating in given event.
        # 2 represents outsider exists and is already registered in given event.
        
        self._db_cursor.execute('SELECT PID FROM ID_Outsider WHERE Govt_ID = ?', (govt_id, ))

        pid = self._db_cursor.fetchone()
        if(pid == None):
            flag = 0
        else:
            self._db_cursor.execute('SELECT EventID FROM Participants WHERE PID = ?', (pid[0], ))
            rows = self._db_cursor.fetchall()
            if rows != None:
                for row in rows:
                    if row[0] == event_id:
                        flag = 2
                        break

        if flag == 2:
            return False

        elif flag == 0:
            query = 'INSERT INTO Participant_Type (Ptype) VALUES (3)'
            self._db_cursor.execute(query)
            self._db_cursor.execute('SELECT MAX(PID) FROM Participant_Type')
            pid = self._db_cursor.fetchone()[0]

            self._db_cursor.execute('INSERT INTO Participants (PID, EventID) VALUES (?, ?)', (pid, event_id, ))

            self._db_cursor.execute('INSERT INTO ID_Outsider (PID, Govt_ID) VALUES (?, ?)', (pid, outsider_args['govt_id'], ))
            
            query = '''
                INSERT INTO Outsider (Govt_ID, Name, College, Contact_num, State)
                VALUES (?, ?, ?, ?, ?)
            '''
            self._db_cursor.execute(query, (outsider_args['govt_id'],
                                            outsider_args['name'],
                                            outsider_args['college'],
                                            outsider_args['contact_num'],
                                            outsider_args['state']))
            
            self._db_connection.commit()
            return True

        else:
            self._db_cursor.execute('SELECT PID FROM ID_Outsider WHERE Govt_ID = ?', (outsider_args['govt_id'], ))
            pid = self._db_cursor.fetchone()[0]

            self._db_cursor.execute('INSERT INTO Participants (PID, EventID) VALUES (?, ?)', (pid, event_id))

            self._db_connection.commit()
            return True


def main():
    std = Outsider()

    args = {}
    args['govt_id'] = '8978 5645 6654'
    args['name'] = 'Sourayan Das'
    args['college'] = 'Jadavpur University'
    args['contact_num'] = '+91 8695 654 235'
    args['state'] = 'West Bengal'

    flag = std.register_outsider(args, 1)
    if flag:
        print('Registered Successfully')
    else:
        print('You are already registered')

if __name__ == '__main__':
    main()