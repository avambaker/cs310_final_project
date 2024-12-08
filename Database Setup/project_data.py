import pymysql
import pandas as pd

# Function to connect to the MySQL database
def connect_to_database():
    try:
        connection = pymysql.connect(
            host='localhost',
            user='root',
            password='',
            database='testmoviedb',
            cursorclass=pymysql.cursors.DictCursor
        )
        if connection:
            return connection
    except Exception as err:
        print(f"Error: {err}")
        return None

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

# Loop through all CSV files and insert them
def loop_csv(list_of_csv):
    for csv_file in list_of_csv:
        table_name = csv_file.rsplit('.', 1)[0]

        try:
            print(f"Processing file: {csv_file} into table: {table_name}")
            insert_data(csv_file, table_name)
            print(f"Successfully inserted data from {csv_file} into table {table_name}")
        except Exception as e:
            print(f"Failed to process {csv_file}: {e}")


# Order of insertion i.e. parent tables before dependent tables
order = ['actor.csv', 'production_company.csv', 'awards.csv', 'genre.csv', 'country.csv', 'director.csv', 'language.csv', 'movie.csv', 
         'movie_genre.csv', 'movie_awards.csv', 'movie_audio.csv', 'movie_cast.csv', 'movie_company.csv', 'movie_country.csv', 'movie_subtitle.csv']

# Insert data into movie database
loop_csv(order)


# # insert parent tables first
# insert_data('actor.csv', 'actor')
# insert_data('production_company.csv', 'production_company')      
# insert_data('awards.csv', 'awards')
# insert_data('genre.csv', 'genre')
# insert_data('country.csv', 'country')
# insert_data('director.csv', 'director')
# insert_data('language.csv', 'language')
# insert_data('movie.csv', 'movie')

# # insert dependent tables next
# insert_data('movie_genre.csv', 'movie_genre')
# insert_data('movie_audio.csv', 'movie_audio')
# insert_data('movie_awards.csv', 'movie_awards')
# insert_data('movie_cast.csv', 'movie_cast')
# insert_data('movie_company.csv', 'movie_company')
# insert_data('movie_country.csv', 'movie_country')
# insert_data('movie_subtitle.csv', 'movie_subtitle')




