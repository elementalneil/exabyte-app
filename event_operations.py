import sqlite3
from datetime import date, time

class Events:
    __db_connection = None
    __db_cursor = None

    def __init__(self):
        self.__db_connection = sqlite3.connect("EventDB.sqlite")
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

    def view_events(self):
        query = 'SELECT * FROM Events'
        self.__db_cursor.execute(query)
        print(self.__db_cursor.fetchall())
        

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

    event_obj.view_events()

if __name__ == '__main__':
    main()