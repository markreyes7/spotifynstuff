import psycopg2
import os
#connect to database START
try:
    connection = psycopg2.connect(user=os.environ['USER'],
                                  password=os.environ['PASSWORD'],
                                  host=os.environ['HOST'],
                                  port=os.environ['PORT'],
                                  database=os.environ['DATABASE'])
    cursor = connection.cursor()

    print("PostgreSQL server information")
    print(connection.get_dsn_parameters(), "\n")

    cursor.execute("SELECT version();")

    record = cursor.fetchone()
    print("You are connected to - ", record, "\n")

    print("Now reading person table")

    cursor.execute("SELECT * from person")
    people = cursor.fetchall()
    print("Print each row and it's columns values")
    for row in people:
        print("id = ", row[0], )
        print("gender = ", row[1])
        print("first_name  = ", row[2])
        print("last_name =", row[3], "\n")

except (Exception, psycopg2.Error) as error:
    print("failed to insert", error)


finally:

    if connection:
        cursor.close()
        connection.close()
        print("PostgreSQL connection is closed")
#end connection to DATABASE