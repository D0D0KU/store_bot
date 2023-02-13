from mysql.connector import connect, Error
from config import mysql_name, mysql_pw


def insert(group, table_name):
    """
    Функция заполняет таблицу по переданному имени.
    :param group: переменная для заполнения.
    :param table_name: имя таблицы.
    """
    try:
        with connect(
                host="localhost",
                user=mysql_name,
                password=mysql_pw,
                database="store_bot"
        ) as connection:

            insert_into_table_name = f'''INSERT INTO {table_name} (group_name) 
                                         VALUES ("{group}")
            '''
            with connection.cursor() as cursor:
                cursor.execute(insert_into_table_name)
                connection.commit()
    except Error as e:
        print(e)

