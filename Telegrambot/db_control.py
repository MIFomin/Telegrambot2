import sqlite3

connection = sqlite3.connect("db.sqlite3", check_same_thread=False)
cursor = connection.cursor()


def execute(sql_string):
    try:
        cursor.execute(sql_string)
        connection.commit()
    except Exception as e:
        print("Произошла ошибка:", e)


def select(sql_string):
    try:
        cursor.execute(sql_string)
        result = cursor.fetchall()
        return result
    except Exception as e:
        print("Произошла ошибка:", e)
        return None
