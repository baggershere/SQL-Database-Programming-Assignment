import psycopg2
import sys
from psycopg2 import OperationalError, errorcodes, errors
#from psycopg2 import __version__ as pv
from prettytable import PrettyTable
pt = PrettyTable()

def print_error(err):
    # get details about the exception
    err_type, err_obj, traceback = sys.exc_info()

    # get the line number when exception occured
    line_num = traceback.tb_lineno
    # print the connect() error
    
    error_list = f'''
    ERROR: {err} on line number:{line_num}\n
    pgErrorCode: {err.pgcode}
    '''
    
    errors = {
        'connectionError': f"psycopg2 ERROR: {err} on line number:{line_num}",
        #'diagnosticError': f"extensions.Diagnostics: {err.diag}",
        #'pgError': f"pgerror: {err.pgerror}\n",
        'pgErrorCode': f"pgcode: {err.pgcode}"
    }
    return error_list
    

def getConn():
    #function to retrieve the password, construct
    #the connection string, make a connection and return it.
    pwFile = open("pw.txt", "r")
    pw = pwFile.read()
    pwFile.close()
    connStr = "host='localhost' \
               user='postgres' dbname='pirean' password = " + pw
    #connStr=("dbname='studentdb' user='dbuser' password= 'dbPassword' " )
    conn=psycopg2.connect(connStr)      
    return  conn

def clearOutput():
    with open("output.txt", "w") as clearfile:
        clearfile.write('')
        
def writeOutput(output):
    with open("output.txt", "a") as myfile:
        myfile.write(output)
clearOutput()
try:
    conn=None   
    conn=getConn()
    cur = conn.cursor()

    f = open("test.txt", "r")
    lines = [line.strip() for line in f.readlines()]
    for x in lines:
        #print(f.read())
        #print(x[0])
        if(x[0] == 'A'):
            raw = x[2:]
            data = raw.split(",")
            #cur.execute("SET SEARCH_PATH to pirean;")
            sql_insert = f"INSERT INTO spectator (sno, sname, semail) VALUES ({data[0]}, '{data[1]}', '{data[2]}');"
            sql_return = f"SELECT * FROM spectator WHERE sno = {data[0]};"
            try:
                cur.execute(sql_insert)
                cur.execute(sql_return)
            except Exception as e:
                clearOutput()
                writeOutput(print_error(e)) 
       
            conn.commit()
            rows = cur.fetchall()
            clearOutput()
            pt.field_names = ['sno', 'sname', 'semail']
            for row in rows:
                pt.add_rows([row])
            print('TASK A Successful')
            writeOutput('A - INSERTED\n' + pt.get_string())
        elif(x[0] == 'B'):
            raw = x[2:]
            data = raw.split(",")
            sql_insert = f"INSERT INTO event (ecode, edesc, elocation, edate, etime, emax) VALUES ('{data[0]}', '{data[1]}', '{data[2]}', '{data[3]}', '{data[4]}', {data[5]});"
            sql_return = f"SELECT * FROM event WHERE ecode = '{data[0]}';"
            
            try:
                cur.execute(sql_insert)
                cur.execute(sql_return)
            except Exception as e:
                clearOutput()
                writeOutput(print_error(e))
                print(print_error(e))
            conn.commit()
            rows = cur.fetchall()
            clearOutput()
            pt.field_names = ['ecode', 'edesc', 'elocation', 'edate', 'etime', 'emax']
            for row in rows:
                pt.add_rows([row])
            print('TASK B Successful')
            writeOutput('TASK B PASS:\n' + pt.get_string())
        elif(x[0] == 'C'):
            raw = x[2:]
            
            #cur.execute("SET SEARCH_PATH to pirean;")
            sql_delete = f"DELETE FROM spectator WHERE sno = {raw};"
            sql_return = f"SELECT * FROM spectator WHERE sno = {raw}"
            try:
                cur.execute(sql_delete)
                cur.execute(sql_return)
            except Exception as e:
                clearOutput()
                error = print_error(e)
                writeOutput(error)   
                print(print_error(e))         
            conn.commit()
            pt.field_names = ['sno', 'sname', 'semail']
            rows = cur.fetchall()
            
            if cur.statusmessage != 'DELETE 0':
                for row in rows:
                    pt.add_rows([row[0], row[1], row[2]])
                writeOutput(f'User {raw} has been removed.\n' + pt.get_string())
                print('DELETE SUCCESS')
            
        elif(x[0] == 'D'):
            raw = x[2:]
            data = raw.split(",")
            #cur.execute("SET SEARCH_PATH to pirean;")
            sql_delete = f"DELETE FROM event WHERE event.ecode = '{data[0]}'"
            sql_return = f"SELECT * FROM event WHERE ecode = '{data[0]}'"
            try:
                cur.execute(sql_delete)
                cur.execute(sql_return)
            except Exception as e:
                clearOutput()
                writeOutput(print_error(e))             
            rows = cur.fetchall()
            conn.commit()
            pt.field_names = ['ecode', 'edesc', 'elocation', 'edate', 'etime', 'emax']
            clearOutput()
            if cur.statusmessage == 'DELETE 0':
                writeOutput(f'Event {data[0]} can not be removed as people have already purchased tickets')
            else:
                for row in rows:
                    pt.add_rows([row])
                print('TASK B Successful')
                writeOutput(f'Event {data[0]} was successfuly removed\n' + pt.get_string())
        
        elif(x[0] == 'E'):
            raw = x[2:]
            data = raw.split(",")
            #cur.execute("SET SEARCH_PATH to pirean;")
            sql_insert = f'''
            INSERT INTO ticket (tno, ecode, sno) 
            SELECT {data[0]}, '{data[1]}', {data[2]} '''
            # WHERE
            # '{data[1]}' IN (SELECT ecode FROM event)
            # AND 
            # NOT EXISTS (
	        # SELECT ecode, sno FROM ticket
        	# WHERE ecode = '{data[1]}' AND sno = {data[2]}
            # )
            # AND 
            # ((SELECT COUNT(ecode) FROM ticket WHERE ecode = '{data[1]}') < 
            # (SELECT emax FROM event WHERE event.ecode = '{data[1]}'));
            
            try:
                cur.execute(sql_insert)
            except Exception as e:
                clearOutput()
                print('Unable to complete' + print_error(e))
                writeOutput(print_error(e))   
                     
            conn.commit()
            
            # pt.field_names = ['tno','ecode','sno']
            
            # if cur.statusmessage == 'INSERT 0 0':
            #     print('TASK E FAIL')
            #     writeOutput(f'Ticket {data[0]} can not be inserted as the maximum number of tickets have been sold already\n')
            # else:
            #     print('TASK E PASS')
            #     writeOutput(f'Ticket {data[0]} was successfuly inserted\n')

        elif(x[0] == 'P'):
            raw = x[2:]
            data = raw.split(",")
            #cur.execute("SET SEARCH_PATH to pirean;")
            sql_query = f'''CREATE OR REPLACE VIEW viewp AS
                            SELECT edate, elocation, COUNT(ticket.ecode)
                            FROM event
                            LEFT JOIN ticket ON event.ecode = ticket.ecode
                            GROUP BY edate, elocation;
                            '''
            sql_return = f'SELECT * FROM viewp;'
            try:
                cur.execute(sql_query)
                cur.execute(sql_return)
            except Exception as e:
                clearOutput()
                writeOutput(print_error(e))             
            conn.commit()
            clearOutput()
            rows = cur.fetchall()
            pt.field_names = ['edate', 'elocation', 'amount']
            for row in rows:
                pt.add_row([row[0], row[1], row[2]])
            print('View successfuly created')
            writeOutput( 'P\n' + pt.get_string())
        elif(x[0] == 'Q'):
            raw = x[2:]
            data = raw.split(",")
            #cur.execute("SET SEARCH_PATH to pirean;")
            sql_query = f'''
            CREATE OR REPLACE VIEW viewq AS
            SELECT ticket.ecode, event.edesc, COUNT(tno) FROM ticket
            LEFT JOIN event ON ticket.ecode = event.ecode
            GROUP BY ticket.ecode, event.edesc
            ORDER BY edesc;
            '''
            sql_return = '''
            SELECT * FROM viewq
            '''
            try:
                cur.execute(sql_query)
                cur.execute(sql_return)
            except Exception as e:
                clearOutput()
                writeOutput(print_error(e))             
            conn.commit()
            clearOutput()
            rows = cur.fetchall()
            pt.field_names = ['ecode', 'edesc', 'amount']
            for row in rows:
                pt.add_row([row[0], row[1], row[2]]) 
                
            writeOutput('Q: \n' + pt.get_string())
            print('View generated')
        elif(x[0] == 'R'):
            raw = x[2:]
            data = raw.split(",")
            #cur.execute("SET SEARCH_PATH to pirean;")
            sql_query = f'''
            CREATE OR REPLACE VIEW viewr AS
            SELECT ticket.ecode, event.edesc, COUNT(tno) FROM ticket
            LEFT JOIN event ON ticket.ecode = event.ecode
            WHERE ticket.ecode = '{data[0]}'
            GROUP BY ticket.ecode, event.edesc;
            '''
            sql_return = '''
            SELECT * FROM viewr
            '''
            try:
                cur.execute(sql_query)
                cur.execute(sql_return)
            except Exception as e:
                clearOutput()
                writeOutput(print_error(e))             
            conn.commit()
            clearOutput()
            rows = cur.fetchall()
            pt.field_names = ['ecode', 'edesc', 'amount']
            for row in rows:
                pt.add_row([row[0], row[1], row[2]])
                
            writeOutput('Task R complete: \n ' + pt.get_string())
            print('Task R PASS')

        elif(x[0] == 'S'):
            raw = x[2:]
            data = raw.split(",")
            #cur.execute("SET SEARCH_PATH to pirean;")
            sql_drop = f"DROP TABLE sitinerary;" 
            sql_create = '''
            CREATE TABLE IF NOT EXISTS sitinerary (
	            sno integer NOT NULL REFERENCES spectator(sno),
	            sname VARCHAR(20) NOT NULL,
	            ecode VARCHAR(20),
	            edate DATE NOT NULL,
	            elocation VARCHAR(20) NOT NULL,
	            etime TIME NOT NULL,
	            edesc VARCHAR(20) NOT NULL
            );
            '''
            sql_insert = f'''
            INSERT INTO sitinerary (sno, sname, ecode, edate, elocation, etime, edesc)
            SELECT ticket.sno, spectator.sname, event.ecode, event.edate, event.elocation, event.etime, event.edesc 
            FROM ticket
            INNER JOIN event ON ticket.ecode = event.ecode
            INNER JOIN spectator ON ticket.sno = spectator.sno
            WHERE ticket.sno = {data[0]};
            '''
            sql_query = f'SELECT * FROM sitinerary'

            try:
                cur.execute(sql_drop)
                cur.execute(sql_create)
                cur.execute(sql_insert)
                cur.execute(sql_query)
            except Exception as e:
                clearOutput()
                writeOutput(print_error(e))             
            conn.commit()
            clearOutput()
            rows = cur.fetchall()
            pt.field_names = ['sno', 'sname', 'ecode', 'elocation', 'etime', 'edesc']
            for row in rows:
                pt.add_row([row[0],row[1],row[2],row[3],row[4],row[5]])
            writeOutput('TASK S: \n' + pt.get_string())
            print('TASK S PASS')
        elif(x[0] == 'T'):
            raw = x[2:]
            data = raw.split(",")
            #cur.execute("SET SEARCH_PATH to pirean;")
            sql_query = f'''
            SELECT sname, ecode, check_ticket_in_ticket as ticket_status FROM all_tickets_with_info WHERE tno = '{data[0]}';'''
            try:
                cur.execute(sql_query)
            except Exception as e:
                clearOutput()
                writeOutput(print_error(e))
            conn.commit()
            clearOutput()
            rows = cur.fetchall()
            pt.field_names = ['sname', 'ecode', 'ticket_status']
            for row in rows:
                pt.add_row([row[0],row[1],row[2]])
            writeOutput('TASK T: \n' + pt.get_string())
            print('TASK T PASS')
        elif(x[0] == 'V'):
            raw = x[2:]
            data = raw.split(",")
            #cur.execute("SET SEARCH_PATH to pirean;")
            sql_query = f'''SELECT tno, ecode, sno, check_ticket_in_ticket as ticket_status, sname FROM all_tickets_with_info WHERE ecode = '{data[0]}' AND check_ticket_in_ticket = false;'''
            try:
                cur.execute(sql_query)
            except Exception as e:
                clearOutput()
                writeOutput(print_error(e))
            conn.commit()
            clearOutput()
            rows = cur.fetchall()
            pt.field_names = ['tno', 'ecode', 'sno', 'ticket_status', 'sname']
            for row in rows:
                pt.add_row([row[0],row[1],row[2],row[3],row[4]])
            writeOutput('TASK V: \n' + pt.get_string())
            print('TASK V PASS')
        elif(x[0] == 'X'):
            cur.close()
            conn.close()
            clearOutput()
            writeOutput("You have exited the program!")
            print('You have exited the program')
        elif(x[0] == '3'):
            #cur.execute("SET SEARCH_PATH to pirean;")
            sql_query = f'''SELECT * FROM ticket'''
            try:
                cur.execute(sql_query)
            except Exception as e:
                clearOutput()
                writeOutput(print_error(e))
            conn.commit()
            clearOutput()
            rows = cur.fetchall()
            pt.field_names = ['tno', 'ecode', 'sno']
            for row in rows:
                pt.add_row([row[0],row[1],row[2]])
            writeOutput('QUESTION 3 EVIDENCE: \n' + pt.get_string())
            print('Evidence displayed')
        elif(x[0] == '9' and x[1] == 'A'):
            #cur.execute("SET SEARCH_PATH to pirean;")
            sql_query = f''' SELECT * FROM cancel WHERE ecode = 'A100'; '''
            try:
                cur.execute(sql_query)
            except Exception as e:
                clearOutput()
                writeOutput(print_error(e))
            conn.commit()
            clearOutput()
            rows = cur.fetchall()
            pt.field_names = ['tno', 'ecode', 'sno', 'cdate', 'cuser']
            for row in rows:
                pt.add_row([row[0],row[1],row[2],row[3], row[4]])
            writeOutput('QUESTION 9A EVIDENCE: \n' + pt.get_string())
            print('Evidence displayed')
        elif(x[0] == '9' and x[1] == 'D'):
            #cur.execute("SET SEARCH_PATH to pirean;")
            sql_query = f''' SELECT * FROM cancel; '''
            try:
                cur.execute(sql_query)
            except Exception as e:
                clearOutput()
                writeOutput(print_error(e))
            conn.commit()
            clearOutput()
            rows = cur.fetchall()
            pt.field_names = ['tno', 'ecode', 'sno', 'cdate', 'cuser']
            for row in rows:
                pt.add_row([row[0],row[1],row[2],row[3], row[4]])
            writeOutput('QUESTION 9D EVIDENCE: \n' + pt.get_string())
            print('Evidence displayed')
        elif(x[0] == '1' and x[1] == '0' and x[2] == 'D'):
            #cur.execute("SET SEARCH_PATH to pirean;")
            sql_query = f''' SELECT * FROM cancel WHERE tno = 20; '''
            try:
                cur.execute(sql_query)
            except Exception as e:
                clearOutput()
                writeOutput(print_error(e))
            conn.commit()
            clearOutput()
            rows = cur.fetchall()
            pt.field_names = ['tno', 'ecode', 'sno', 'cdate', 'cuser']
            for row in rows:
                pt.add_row([row[0],row[1],row[2],row[3], row[4]])
            writeOutput('QUESTION 10D EVIDENCE: \n' + pt.get_string())
            print('Evidence displayed')
        elif(x[0] == 'Z'):
            sql_query = f'''TRUNCATE event CASCADE;
                            TRUNCATE ticket CASCADE;
                            TRUNCATE cancel CASCADE;
                            TRUNCATE spectator CASCADE;
                            TRUNCATE sitinerary CASCADE;
                        '''
            try:
                cur.execute(sql_query)
            except Exception as e:
                clearOutput()
                writeOutput(print_error(e))
            conn.commit()
            clearOutput()
            print('Task Z: Tables cleared')
            writeOutput('Z. Tables cleared')
except Exception as e:
    print (e)


               