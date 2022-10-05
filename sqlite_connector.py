import sqlite3

connection = sqlite3.connect("db.sqlite")
cursor = connection.cursor()

def get_telegram_ids():
    rows = cursor.execute("SELECT telegram_id FROM users").fetchall()
    return rows

def get_resources():
    rows = cursor.execute("SELECT name, logo FROM resources").fetchall()
    return rows