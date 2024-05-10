import psycopg2
import json
from user import User
from target import Target
from config import dbname, dbuser, password, host, port
# запуск бота:
# - подтягивает инфу из бд
# - создает объекты
# - хранит их в словариках/массивах
# обращение к бд, когда
# - пользователь впервые пришел
# - выбраны теги (я выбрал)
# - выбраны цели (я выбрал)
# - выбраны настройки для целей (я выбрал)


def get_users():
    conn = psycopg2.connect(dbname=dbname, user=dbuser,
                            password=password, host=host, port=port)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users')
    conn.commit()
    pre_users = cursor.fetchall()
    cursor.close()
    conn.close()
    users = {}
    for usr in pre_users:
        user = User(usr[0], usr[2], usr[1], usr[3], usr[4])
        users[user.tg_id] = user
    return users


def get_targets():
    conn = psycopg2.connect(dbname=dbname, user=dbuser,
                            password=password, host=host, port=port)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM targets')
    conn.commit()
    pre_users = cursor.fetchall()
    cursor.close()
    conn.close()
    conn = psycopg2.connect(dbname=dbname, user=dbuser,
                            password=password, host=host, port=port)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM targets')
    conn.commit()
    pre_targets = cursor.fetchall()
    cursor.close()
    conn.close()
    targets = {}
    for _target in pre_targets:
        usr_hold = {}
        for usr_key in _target[1]:
            usr_hold[int(usr_key)] = _target[1][usr_key]
        target = Target(_target[0], usr_hold)
        targets[target.name] = target
    return targets


def add_new_target(target: Target):
    conn = psycopg2.connect(dbname=dbname, user=dbuser,
                            password=password, host=host, port=port)
    cursor = conn.cursor()
    cursor.execute('INSERT INTO targets (target_name, users_hold)'
                   'VALUES (%s, %s)',
                   (target.name, json.dumps(target.users_hold)))
    conn.commit()
    cursor.close()
    conn.close()


def create_user(user: User):
    conn = psycopg2.connect(dbname=dbname, user=dbuser,
                            password=password, host=host, port=port)
    cursor = conn.cursor()
    cursor.execute('INSERT INTO users (tg_id, name, username, tags, targets) '
                   'VALUES (%s, %s, %s, %s, %s)',
                   (user.tg_id, user.name, user.username, json.dumps({}), []))
    conn.commit()
    cursor.close()
    conn.close()


def delete_user(user: User):
    conn = psycopg2.connect(dbname=dbname, user=dbuser,
                            password=password, host=host, port=port)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM users WHERE tg_id = %s ',
                   (user.tg_id,))
    conn.commit()
    cursor.close()
    conn.close()


def update_user_tags(user: User):
    conn = psycopg2.connect(dbname=dbname, user=dbuser,
                            password=password, host=host, port=port)
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET tags = %s WHERE tg_id = %s ',
                   (json.dumps(user.tags), user.tg_id))
    conn.commit()
    cursor.close()
    conn.close()


def update_user_targets(user: User):
    conn = psycopg2.connect(dbname=dbname, user=dbuser,
                            password=password, host=host, port=port)
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET targets = %s WHERE tg_id = %s ',
                   (user.targets, user.tg_id))
    conn.commit()
    cursor.close()
    conn.close()


def update_user_target_wishlist(target: Target):
    conn = psycopg2.connect(dbname=dbname, user=dbuser,
                            password=password, host=host, port=port)
    cursor = conn.cursor()
    cursor.execute('UPDATE targets SET users_hold = %s WHERE target_name = %s ',
                   (json.dumps(target.users_hold), target.name))
    conn.commit()
    cursor.close()
    conn.close()
