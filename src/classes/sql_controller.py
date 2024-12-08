import pymysql
import sys
import pandas as pd
import os
import re

def connect_to_database():
    connection_args = {
            "host": "localhost",
            "user": "root",
            "database": "moviedb",
            "cursorclass": pymysql.cursors.DictCursor
        }
    password = fetchPassword()
    if password:
        connection_args["password"] = password
    try:
        connection = pymysql.connect(**connection_args)
        if connection:
            return connection
    except Exception as err:
        print(f"Error: {err}")
        return None

def tuple_connect_to_database():
    try:
        connection_args = {
            "host": "localhost",
            "user": "root",
            "database": "moviedb",
        }
        password = fetchPassword()
        if password:
            connection_args["password"] = password
        connection = pymysql.connect(**connection_args)
        if connection:
            return connection
    except Exception as err:
        print(f"Error: {err}")
        return None
    
def query_data(query, get_tuples=False, params=None):
        if get_tuples is False:
            connection = connect_to_database()
            if not connection:
                print("CONNECTION FAILED")
                print(query)
                return
        else:
            connection = tuple_connect_to_database()
            if not connection:
                print("CONNECTION FAILED")
                print(query)
                return
        try:
            with connection.cursor() as cursor:
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)
                data = cursor.fetchall()
                if data and len(data[0]) == 1:
                    return [row[0] for row in data]
                elif data:
                    return data
                elif get_tuples:
                    return []
                else:
                    return {}
        finally:
            if query.strip().upper().startswith(("INSERT", "UPDATE", "DELETE")):
                connection.commit()
            if connection: connection.close()

def callProcedure(procedure_name, params=None):
    connection = connect_to_database()
    try:
        with connection.cursor() as cursor:
            if params:
                cursor.callproc(procedure_name, params)
            else:
                cursor.callproc(procedure_name)
            data = cursor.fetchall()
            if data and len(data[0]) == 1:
                return [row[0] for row in data]
            elif data:
                return data
            else:
                return {}
    finally:
        connection.close()

def fetchPassword():
    with open('data/sql_password.txt') as f:
        lines = f.readlines()
    if lines:
        return lines[0].strip("/n").strip()
    else:
        return ""

def setPassword(s):
    with open('data/sql_password.txt', 'w') as f:
        f.write(s)

def create_database(file_path):
    with open(file_path, "r") as file:
        sql_script = file.read()
    try:
        connection_args = {
            "host": "localhost",
            "user": "root",
            "database": "mysql",
            "cursorclass": pymysql.cursors.DictCursor
        }
        password = fetchPassword()
        if password:
            connection_args["password"] = password
        connection = pymysql.connect(**connection_args)
    except Exception as err:
        print(f"Error: {err}")
        return False
    try:
        # Connect to the database
        cursor = connection.cursor()

        # Split the script by `DELIMITER` statements
        statements = re.split(r"DELIMITER\s+(\S+)", sql_script)

        # Default delimiter
        current_delimiter = ";"

        # Execute each part of the script
        for i, statement in enumerate(statements):
            if i % 2 == 0:  # Normal SQL commands
                commands = statement.split(current_delimiter)
                for command in commands:
                    command = command.strip()
                    if command:  # Skip empty commands
                        cursor.execute(command)
                        print(f"Executed: {command[:30]}...")  # Log part of the statement
            else:  # Change delimiter
                current_delimiter = statement.strip()
                print(f"Changed delimiter to: {current_delimiter}")

        # Commit changes
        connection.commit()
        print("DDL schema successfully uploaded!")
        return True

    except pymysql.MySQLError as err:
        print(f"Error: {err}")
        return False

    finally:
        if connection:
            cursor.close()
            connection.close()

# Function to insert data from CSV into MySQL table
def insert_data(csv_file, table_name):
    connection = connect_to_database()
    
    if connection is None:
        print("Failed to connect to the database.")
        return False
    
    cursor = connection.cursor()

    try:
        # Load the CSV into a DataFrame
        df = pd.read_csv(csv_file)

        # Replace NaN values with None
        df = df.where(pd.notnull(df), None)

        # Prepare the columns and placeholders dynamically
        columns = ", ".join(df.columns)
        placeholders = ', '.join(['%s'] * len(df.columns))

        # Create the insert query
        insert_query = f"""
        INSERT INTO {table_name} ({columns})
        VALUES ({placeholders})
        """

        # Insert data row by row
        for index, row in df.iterrows():
            cursor.execute(insert_query, tuple(row))

        # Commit the changes
        connection.commit()
        print('Success! Data inserted.')
        return True

    except Exception as e:
        print(f"Error inserting data: {e}")
        return False
    finally:
        # Close the cursor and connection
        cursor.close()
        connection.close()

def loop_csv(csv_dir):
    for file_name in os.listdir(csv_dir):
        if file_name.endswith(".csv"):
            csv_path = os.path.join(csv_dir, file_name)
            table_name = os.path.splitext(os.path.basename(csv_path))[0]
        try:
            print(f"Processing file: {csv_path} into table: {table_name}")
            result = insert_data(csv_path, table_name)
            if result: print(f"Successfully inserted data from {csv_path} into table {table_name}")
            else: print("failed")
        except Exception as e:
            print(f"Failed to process {csv_path}: {e}")

order = ['actor.csv', 'production_company.csv', 'awards.csv', 'genre.csv', 'country.csv', 'director.csv', 'language.csv', 'movie.csv', 
         'movie_genre.csv', 'movie_awards.csv', 'movie_audio.csv', 'movie_cast.csv', 'movie_company.csv', 'movie_country.csv', 'movie_subtitle.csv']