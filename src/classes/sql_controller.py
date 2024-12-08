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


attributes_and_datatypes = "SELECT COLUMN_NAME, DATA_TYPE FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA = 'testmoviedb' AND TABLE_NAME = '%s';"
attributes = "SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA = 'testmoviedb' AND TABLE_NAME = '%s';"