import sqlite3

connection = sqlite3.connect("db.sqlite")
cursor = connection.cursor()

def get_telegram_ids():
    cursor = connection.cursor()
    rows = cursor.execute("SELECT tg_id FROM users").fetchall()
    cursor.close()
    if rows:
        result = []
        for row in rows:
            result.append(row[0])
        return result
    else:
        return rows

def get_user_id(tg_id):
    cursor = connection.cursor()
    result = cursor.execute("SELECT id FROM users WHERE tg_id=?", [tg_id]).fetchone()
    cursor.close()
    return result

def write_telegram_id(user_id):
    cursor = connection.cursor()
    query = "INSERT INTO users (tg_id) VALUES (%s)" % user_id
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

def write_title(res_id, url):
    cursor = connection.cursor()
    query = "INSERT INTO titles (res_id, url) VALUES (%s, '%s')" % (res_id, url)
    cursor.execute(query)
    connection.commit()
    inserted_id = cursor.lastrowid
    cursor.close()
    return inserted_id

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

def get_user_subs_formated(user_id):
    cursor = connection.cursor()
    rows = cursor.execute("SELECT 'Название: '||ifnull(t.name_rus,'?_?')||' | Name: '||ifnull(t.name_lat,'?_?')||char(10)||'Всего серий: '|| ifnull(t.ep_total,'?_?')||', ты посмотрел: '|| ifnull(t.ep_now,'?_?')||char(10)||'Время проверки: '|| ifnull(strftime('%d.%m.%Y %H:%M:%S',datetime(t.last_check_date, 'unixepoch')),'Не проверялось') name FROM subscriptions s, titles t WHERE t.id = s.title_id and s.user_id=?", [user_id]).fetchall()
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