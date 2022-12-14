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

    def check_registration(self, pid, event_id):
        query = 'SELECT * FROM Participants WHERE PID = ? AND EventID = ?'
        self._db_cursor.execute(query, (pid, event_id, ))

        if self._db_cursor.fetchone() == None:
            return False
        else:
            return True

    def get_ptype(self, pid):
        query = 'SELECT Ptype FROM Participant_Type WHERE PID = ?'
        self._db_cursor.execute(query, (pid, ))

        return_s = self._db_cursor.fetchone();

        if return_s == None:
            return ''
        else:
            return return_s[0]

    def deregister(self, pid, event_id):
        if self.check_registration(pid, event_id) == True:
            query = 'DELETE FROM Participants WHERE PID = ? AND EventID = ?'
            self._db_cursor.execute(query, (pid, event_id, ))
            self._db_connection.commit()
            return True
        else:
            return False

    def delete_participant(self, pid):
        self._db_cursor.execute('DELETE FROM Participants WHERE PID = ?', (pid, ))
        ptype = self.get_ptype(pid)
        self._db_cursor.execute('DELETE FROM Participant_Type WHERE PID = ?', (pid, ))
        if ptype == 1:
            self._db_cursor.execute('SELECT Roll_no FROM ID_Student WHERE PID = ?', (pid, ))
            roll = self._db_cursor.fetchone()[0]
            self._db_cursor.execute('DELETE FROM ID_Student WHERE PID = ?', (pid, ))
            self._db_cursor.execute('DELETE FROM Student WHERE Roll_no = ?', (roll, ))
        elif ptype == 2:
            self._db_cursor.execute('SELECT F_ID FROM ID_Faculty WHERE PID = ?', (pid, ))
            fid = self._db_cursor.fetchone()[0]
            self._db_cursor.execute('DELETE FROM ID_Faculty WHERE PID = ?', (pid, ))
            self._db_cursor.execute('DELETE FROM Faculty WHERE F_ID = ?', (fid, ))
        else:
            self._db_cursor.execute('SELECT Govt_ID FROM ID_Outsider WHERE PID = ?', (pid, ))
            id = self._db_cursor.fetchone()[0]
            self._db_cursor.execute('DELETE FROM ID_Outsider WHERE PID = ?', (pid, ))
            self._db_cursor.execute('DELETE FROM Outsider WHERE Govt_ID = ?', (id, ))
        self._db_connection.commit()


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

    def get_by_pid(self, pid):
        query = '''
            SELECT S.Roll_no, S.Name, S.Contact_num, S.Email, S.Department, S.Semester 
            FROM Student as S, ID_Student as I
            WHERE S.Roll_no = I.Roll_no
            AND I.PID = ?
        '''
        
        self._db_cursor.execute(query, (pid, ))
        return self._db_cursor.fetchone()


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

    def get_by_pid(self, pid):
        query = '''
            SELECT F.F_ID, F.Name, F.Contact_num, F.Department 
            FROM Faculty as F, ID_Faculty as I
            WHERE F.F_ID = I.F_ID
            AND I.PID = ?
        '''
        
        self._db_cursor.execute(query, (pid, ))
        return self._db_cursor.fetchone()


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
        govt_id = outsider_args['govt_id'].upper().replace(" ", "")

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

    def get_by_pid(self, pid):
        query = '''
            SELECT O.Govt_ID, O.Name, O.College, O.Contact_num, O.State
            FROM Outsider as O, ID_Outsider as I
            WHERE O.Govt_ID = I.Govt_ID
            AND I.PID = ?
        '''
        
        self._db_cursor.execute(query, (pid, ))
        return self._db_cursor.fetchone()


# For testing this particular file
def main():
    p = Participant()
    p.delete_participant(9)

if __name__ == '__main__':
    main()