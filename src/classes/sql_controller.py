import pymysql
import sys
import pandas as pd

def connect_to_database():
    try:
        connection = pymysql.connect(
            host='localhost',
            user='root',
            password=user_password,
            database='moviedb',
            cursorclass=pymysql.cursors.DictCursor
        )
        if connection:
            return connection
    except Exception as err:
        print(f"Error: {err}")
        return None

def tuple_connect_to_database():
    try:
        connection = pymysql.connect(
            host='localhost',
            user='root',
            password=user_password,
            database='moviedb',
        )
        if connection:
            return connection
    except Exception as err:
        print(f"Error: {err}")
        return None
    
def query_data(query, get_tuples=False, params=None):
        if get_tuples is False:
            connection = connect_to_database()
        else:
            connection = tuple_connect_to_database()
        try:
            with connection.cursor() as cursor:
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)
                data = cursor.fetchall()
                if data and len(data[0]) == 1:
                    print(data)
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
            connection.close()

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
        password = f.readline().strip('\n').strip()
    return password

def setPassword(s):
    with open('data/sql_password.txt', 'w') as f:
        f.write(s)
    user_password = s

def create_database(file_path):
    connection = connect_to_database()
    try:
        with connection.cursor() as cursor:
            for line in open(file_path):
                cursor.execute(line)
        connection.commit()

    except Warning as warn:
        print(warn)
        sys.exit()

# Function to insert data from CSV into MySQL table
def insert_data(csv_file, table_name):
    connection = connect_to_database()
    
    if connection is None:
        print("Failed to connect to the database.")
        return
    
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

    except Exception as e:
        print(f"Error inserting data: {e}")
    finally:
        # Close the cursor and connection
        cursor.close()
        connection.close()

def loop_csv(list_of_csv):
    for csv_file in list_of_csv:
        table_name = csv_file.rsplit('.', 1)[0]

        try:
            print(f"Processing file: {csv_file} into table: {table_name}")
            insert_data(csv_file, table_name)
            print(f"Successfully inserted data from {csv_file} into table {table_name}")
        except Exception as e:
            print(f"Failed to process {csv_file}: {e}")

user_password = fetchPassword()
order = ['Database Setup/actor.csv', 'Database Setup/production_company.csv', 'Database Setup/awards.csv', 'Database Setup/genre.csv', 'Database Setup/country.csv', 'Database Setup/director.csv', 'Database Setup/language.csv', 'Database Setup/movie.csv', 
         'Database Setup/movie_genre.csv', 'Database Setup/movie_awards.csv', 'Database Setup/movie_audio.csv', 'Database Setup/movie_cast.csv', 'Database Setup/movie_company.csv', 'Database Setup/movie_country.csv', 'Database Setup/movie_subtitle.csv']