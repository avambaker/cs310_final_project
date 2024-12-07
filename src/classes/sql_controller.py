import pymysql
def connect_to_database():
    try:
        connection = pymysql.connect(
            host='localhost',
            user='root',
            password='r00tPassword#',
            database='testmoviedb',
            cursorclass=pymysql.cursors.DictCursor
        )
        if connection:
            return connection
    except Exception as err:
        print(f"Error: {err}")
        return None
    
def query_data(query):
        connection = connect_to_database()
        try:
            with connection.cursor() as cursor:
                cursor.execute(query)
                data = cursor.fetchall()
                if data:
                    headers = data[0].keys()  # Extract column names
                    return data, list(headers)
        finally:
            connection.close()