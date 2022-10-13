import sqlite3

connection = sqlite3.connect("db.sqlite")
cursor = connection.cursor()

def get_admin_id():
    cursor = connection.cursor()
    result = cursor.execute("SELECT telegram_id FROM users WHERE admin=1").fetchone()
    cursor.close()
    return result[0]

def get_telegram_ids():
    cursor = connection.cursor()
    rows = cursor.execute("SELECT telegram_id FROM users").fetchall()
    cursor.close()
    if rows:
        result = []
        for row in rows:
            result.append(row[0])
        return result
    else:
        return rows

def get_user_id(telegram_id):
    cursor = connection.cursor()
    result = cursor.execute("SELECT id FROM users WHERE telegram_id=?", [telegram_id]).fetchone()
    cursor.close()
    return result

def write_telegram_id(user_id):
    cursor = connection.cursor()
    query = "INSERT INTO users (telegram_id) VALUES (%s)" % user_id
    cursor.execute(query)
    connection.commit()
    inserted_id = cursor.lastrowid
    cursor.close()
    return inserted_id

def get_resources():
    cursor = connection.cursor()
    rows = cursor.execute("SELECT name, logo FROM resources").fetchall()
    cursor.close()
    return rows

def get_resource(id):
    cursor = connection.cursor()
    result = cursor.execute("SELECT * FROM resources WHERE id=?", [id]).fetchone()
    cursor.close()
    # res_id = "".join([str(item) for item in result])
    res = result
    return res

def get_resources_names():
    cursor = connection.cursor()
    rows = cursor.execute("SELECT name FROM resources").fetchall()
    cursor.close()
    return rows

def get_resource_id_by_name(name):
    cursor = connection.cursor()
    result = cursor.execute("SELECT id FROM resources WHERE name=?", [name]).fetchone()
    cursor.close()
    # res_id = "".join([str(item) for item in result])
    res_id = result[0]
    return res_id

def get_title_by_url(url):
    cursor = connection.cursor()
    result = cursor.execute("SELECT * FROM titles WHERE url=?", [url]).fetchone()
    cursor.close()
    return result

def write_title(from_resource, url):
    cursor = connection.cursor()
    query = "INSERT INTO titles (from_resource, url) VALUES (%s, '%s')" % (from_resource, url)
    cursor.execute(query)
    connection.commit()
    inserted_id = cursor.lastrowid
    cursor.close()
    return inserted_id

def get_subscriptions():
    cursor = connection.cursor()
    rows = cursor.execute("SELECT * FROM subscriptions").fetchall()
    cursor.close()
    # if rows:
    #     result = []
    #     for row in rows:
    #         result.append(row[0])
    #     return result
    # else:
    return rows

def get_user_subscriptions(user_id):
    cursor = connection.cursor()
    rows = cursor.execute("SELECT title_id FROM subscriptions WHERE user_id=?", [user_id]).fetchall()
    cursor.close()
    if rows:
        result = []
        for row in rows:
            result.append(row[0])
        return result
    else:
        return rows

def write_subscription(user, title):
    cursor = connection.cursor()
    query = "INSERT INTO subscriptions (user_id, title_id) VALUES (%s, '%s')" % (user, title)
    cursor.execute(query)
    connection.commit()
    inserted_id = cursor.lastrowid
    cursor.close()
    return inserted_id