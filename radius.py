import mysql.connector

from mysql.connector import Error

from getpass import getpass

from datetime import datetime

 

def connect_to_mysql():

    try:

        # Prompt for password securely

        password = getpass("Enter your MySQL password: ")

       

        # Establish connection

        connection = mysql.connector.connect(

            host="azure-homenet-isp-mysql-1.mysql.database.azure.com",

            database="freeradius",

            user="homenet",

            password=password

        )

       

        if connection.is_connected():

            print(f"Connected to MySQL server version {connection.get_server_info()}")

            return connection

           

    except Error as e:

        print(f"Error while connecting to MySQL: {e}")

        return None

 

def query_active_sessions(connection, username):

    try:

        cursor = connection.cursor(dictionary=True)

       

        # First query: Basic active session info

        print(f"\nActive session information for user: {username}")

        query1 = """

        SELECT framedipaddress, acctstarttime, acctupdatetime, nasipaddress

        FROM freeradius.radacct

        WHERE username = %s AND acctstoptime IS NULL

        """

        cursor.execute(query1, (username,))

        result1 = cursor.fetchall()

       

        if not result1:

            print(f"No active sessions found for user {username}")

            return

       

        # Print basic session info

        for session in result1:

            print("\nBasic Session Info:")

            print(f"IP Address: {session['framedipaddress']}")

            print(f"Login Time: {session['acctstarttime']}")

            print(f"Last Update: {session['acctupdatetime']}")

            print(f"NAS IP: {session['nasipaddress']}")

       

        # Second query: Detailed session verification

        print("\nDetailed Session Verification:")

        query2 = """

        SELECT

            ra.framedipaddress,

            ra.username as username_on_radacct,

            ra.nasipaddress as nasipaddress_on_radacct,

            ra.acctstarttime,

            ra.acctupdatetime,

            rp.username as username_on_radippool,

            rp.expiry_time,

            rp.pool_key,

            rp.nasipaddress as nasipaddress_on_radippool

        FROM

            freeradius.radacct ra

        LEFT JOIN

            freeradius.radippool rp

            ON ra.framedipaddress = rp.framedipaddress

        WHERE

            ra.acctstoptime IS NULL

            AND ra.username = %s

            AND ra.username = rp.username

            AND ra.nasipaddress = rp.nasipaddress

        """

        cursor.execute(query2, (username,))

        result2 = cursor.fetchall()

       

        if not result2:

            print("No matching records found in verification query - possible session inconsistency")

        else:

            print("Verified Session Details:")

            for row in result2:

                print(f"\nIP Address: {row['framedipaddress']}")

                print(f"RADIUS Username: {row['username_on_radacct']}")

                print(f"RADIUS NAS IP: {row['nasipaddress_on_radacct']}")

                print(f"Login Time: {row['acctstarttime']}")

                print(f"Last Update: {row['acctupdatetime']}")

                print(f"IP Pool Username: {row['username_on_radippool']}")

                print(f"Expiry Time: {row['expiry_time']}")

                print(f"Pool Key: {row['pool_key']}")

                print(f"IP Pool NAS IP: {row['nasipaddress_on_radippool']}")

               

                # Check for consistency

                if (row['username_on_radacct'] == row['username_on_radippool'] and

                    row['nasipaddress_on_radacct'] == row['nasipaddress_on_radippool']):

                    print("Status: Consistent session")

                else:

                    print("Status: Inconsistent session data")

       

    except Error as e:

        print(f"Error executing query: {e}")

    finally:

        if cursor:

            cursor.close()

 

def main():

    username = input("Enter the username to query: ")

   

    connection = connect_to_mysql()

    if connection:

        try:

            query_active_sessions(connection, username)

        finally:

            connection.close()

            print("\nMySQL connection closed")

 

if __name__ == "__main__":

    main()
