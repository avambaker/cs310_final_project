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

def tuple_connect_to_database():
    try:
        connection = pymysql.connect(
            host='localhost',
            user='root',
            password='r00tPassword#',
            database='testmoviedb',
        )
        if connection:
            return connection
    except Exception as err:
        print(f"Error: {err}")
        return None
    
def query_data(query, get_tuples=False):
        if get_tuples is False:
            connection = connect_to_database()
        else:
            connection = tuple_connect_to_database()
        try:
            with connection.cursor() as cursor:
                cursor.execute(query)
                data = cursor.fetchall()
                if data:
                    return data
        finally:
            connection.close()

attributes_and_datatypes = "SELECT COLUMN_NAME, DATA_TYPE FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA = 'testmoviedb' AND TABLE_NAME = '%s';"