import sqlite3

connection = sqlite3.connect("db.sqlite")
cursor = connection.cursor()

def get_telegram_ids():
    cursor = connection.cursor()
    rows = cursor.execute("SELECT telegram_id FROM users").fetchall()
    cursor.close()
    return rows[0]

def write_telegram_id(user_id):
    query = "INSERT INTO users (telegram_id) VALUES (%s)" % user_id
    cursor.execute(query)
    connection.commit()
    count = cursor.rowcount
    cursor.close()
    return count

def get_resources():
    cursor = connection.cursor()
    rows = cursor.execute("SELECT name, logo FROM resources").fetchall()
    cursor.close()
    return rows

def get_resources_names():
    cursor = connection.cursor()
    rows = cursor.execute("SELECT name FROM resources").fetchall()
    cursor.close()
    return rows

def write_title(url):
    pass