import sqlite3
from datetime import date, time

class Events:
    __db_connection = None
    __db_cursor = None

    def __init__(self):
        self.__db_connection = sqlite3.connect("main_server.sqlite")
        self.__db_cursor = self.__db_connection.cursor()

        initscript = '''
            CREATE TABLE IF NOT EXISTS Events (
                EventID integer NOT NULL UNIQUE PRIMARY KEY AUTOINCREMENT,
                EventName varchar2(255) NOT NULL,
                Venue varchar2(63),
                Description text,
                Date date NOT NULL,
                Time time,
                Contact_name varchar2(255),
                Contact_no varchar2(20)
            );
        '''
        
        self.__db_cursor.executescript(initscript)

    def create_event(self, event_args):     # event_args is a dictionary containing event attributes
        query = '''INSERT INTO 
                   Events(EventName, Venue, Description, Date, Time, Contact_name, Contact_no)
                   VALUES (?, ?, ?, ?, ?, ?, ?)'''
        self.__db_cursor.execute(query, (event_args['name'],
                                         event_args['venue'],
                                         event_args['description'],
                                         event_args['date'],
                                         event_args['time'],
                                         event_args['contact_name'],
                                         event_args['contact_num']) )
        self.__db_connection.commit()

    def modify_event(self, new_args, event_id):
        query = '''
            UPDATE Events
            SET EventName = ?, Venue = ?, Description = ?, Date = ?, Time = ?, Contact_name = ?, Contact_no = ?
            WHERE EventID = ?
        '''
        self.__db_cursor.execute(query, (new_args['name'],
                                         new_args['venue'],
                                         new_args['description'],
                                         new_args['date'],
                                         new_args['time'],
                                         new_args['contact_name'],
                                         new_args['contact_num'],
                                         event_id) )
        self.__db_connection.commit()

    def delete_event(self, event_id):
        self.__db_cursor.execute('DELETE FROM Events WHERE EventID = ?', (event_id))

    def view_events(self):
        query = 'SELECT * FROM Events'
        self.__db_cursor.execute(query)
        all_events = self.__db_cursor.fetchall()
        return all_events

    def event_details(self, event_id):
        self.__db_cursor.execute('SELECT * FROM Events WHERE EventID = ?', (event_id, ))
        return self.__db_cursor.fetchone()

    # Returns details of all students registered in a specific event
    def event_students(self, event_id):
        query = '''
            SELECT ID_Student.PID, Student.Roll_no, Student.Name, Student.Email
            FROM Participants, Participant_Type, ID_Student, Student
            WHERE Participants.PID = Participant_Type.PID
            AND Participants.EventID = ?
            AND Participant_Type.Ptype = 1
            AND ID_Student.PID = Participant_Type.PID
            AND Student.Roll_no = ID_Student.Roll_no
        '''
        
        rows = self.__db_cursor.execute(query, (event_id, ))
        return(rows)

    # Returns details of all faculty registered in a specific event
    def event_faculty(self, event_id):
        query = '''
            SELECT ID_Faculty.PID, Faculty.F_ID, Faculty.Name, Faculty.Contact_num
            FROM Participants, Participant_Type, ID_Faculty, Faculty
            WHERE Participants.PID = Participant_Type.PID
            AND Participants.EventID = ?
            AND Participant_Type.Ptype = 2
            AND ID_Faculty.PID = Participant_Type.PID
            AND Faculty.F_ID = ID_Faculty.F_ID
        '''

        rows = self.__db_cursor.execute(query, (event_id, ))
        return(rows)

    # Returns details of all outsiders registered in a specific event
    def event_outsider(self, event_id):
        query = '''
            SELECT ID_Outsider.PID, Outsider.Govt_ID, Outsider.Name, Outsider.College
            FROM Participants, Participant_Type, ID_Outsider, Outsider
            WHERE Participants.PID = Participant_Type.PID
            AND Participants.EventID = ?
            AND Participant_Type.Ptype = 3
            AND ID_Outsider.PID = Participant_Type.PID
            AND Outsider.Govt_ID = ID_Outsider.Govt_ID
        '''

        rows = self.__db_cursor.execute(query, (event_id, ))
        return(rows)


def main():
    event_obj = Events()

    # args = {}
    # args['name'] = 'Proshow1'
    # args['venue'] = 'Football Ground'
    # args['date'] = date(2022, 10, 25)
    # args['time'] = '07:30:00'
    # args['contact_name'] = 'John Doe'
    # args['contact_num'] = '+91 815 568 9973'

    # event_obj.create_event(args)

    for row in event_obj.event_students(2):
        print(row)
    for row in event_obj.event_faculty(2):
        print(row)
    for row in event_obj.event_outsider(2):
        print(row)
        

if __name__ == '__main__':
    main()