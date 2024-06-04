import psycopg2
import json
from user import User2
from enums import Targets
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


# def get_users():
#     conn = psycopg2.connect(dbname=dbname, user=dbuser,
#                             password=password, host=host, port=port)
#     cursor = conn.cursor()
#     cursor.execute('SELECT * FROM users')
#     conn.commit()
#     pre_users = cursor.fetchall()
#     cursor.close()
#     conn.close()
#     users = {}
#     for usr in pre_users:
#         user = User(usr[0], usr[2], usr[1], usr[3], usr[4])
#         users[user.tg_id] = user
#     return users


def get_all_users():
    conn = psycopg2.connect(dbname=dbname, user=dbuser,
                            password=password, host=host, port=port)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users_backup')
    conn.commit()
    pre_users = cursor.fetchall()
    cursor.close()
    conn.close()
    users = dict()
    for usr in pre_users:
        user = User2(tg_id=usr[0], 
                     name=usr[1],
                     username=usr[2],             
                     tags=usr[3], 
                     targets=usr[4])
        users[user.tg_id] = user
    return users


# def get_one_user2(tg_id : int) -> User2:
#     conn = psycopg2.connect(dbname=dbname, user=dbuser,
#                             password=password, host=host, port=port)
#     cursor = conn.cursor()
#     cursor.execute('SELECT * FROM users_backup WHERE tg_id = %s', (tg_id,))
#     conn.commit()
#     pre_user = cursor.fetchone()
#     #print(pre_user)
#     if not pre_user:
#        return
#     user = User2(tg_id=pre_user[0], 
#                  name=pre_user[1],
#                  username=pre_user[2],             
#                  tags=pre_user[3], 
#                  targets=pre_user[4])
#     cursor.close()
#     conn.close()
#     return user
   

def create_user2(user: User2) -> None:
    conn = psycopg2.connect(dbname=dbname, user=dbuser,
                            password=password, host=host, port=port)
    cursor = conn.cursor()
    cursor.execute('INSERT INTO users_backup (tg_id, name, username, tags, targets) '
                   'VALUES (%s, %s, %s, %s, %s)',
                   (user.tg_id, user.name, user.username, json.dumps({}), json.dumps({})))
    conn.commit()
    cursor.close()
    conn.close()


def delete_user(user: User2):
    conn = psycopg2.connect(dbname=dbname, user=dbuser,
                            password=password, host=host, port=port)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM users_backup WHERE tg_id = %s ',
                   (user.tg_id,))
    conn.commit()
    cursor.close()
    conn.close()


def update_user_tags(user: User2):
    conn = psycopg2.connect(dbname=dbname, user=dbuser,
                            password=password, host=host, port=port)
    cursor = conn.cursor()
    cursor.execute('UPDATE users_backup SET tags = %s WHERE tg_id = %s ',
                   (json.dumps(user.tags), user.tg_id))
    conn.commit()
    cursor.close()
    conn.close()


def update_user_targets(user: User2):
    conn = psycopg2.connect(dbname=dbname, user=dbuser,
                            password=password, host=host, port=port)
    cursor = conn.cursor()
    cursor.execute('UPDATE users_backup SET targets = %s WHERE tg_id = %s ',
                   (json.dumps(user.targets), user.tg_id))
    conn.commit()
    cursor.close()
    conn.close()


def get_users_by_target(target_name: str) -> dict:
    conn = psycopg2.connect(dbname=dbname, user=dbuser,
                                password=password, host=host, port=port)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users_backup WHERE targets ?& array[%s];", 
                    (target_name,))
    conn.commit()
    pre_users = cursor.fetchall()
    users = dict()
    for usr in pre_users:
        user = User2(usr[0], usr[2], usr[1], usr[3], usr[4])
        users[user.tg_id] = user
    cursor.close()
    conn.close()
    return users


def get_statistic():
    conn = psycopg2.connect(dbname=dbname, user=dbuser,
                                password=password, host=host, port=port)
    cursor = conn.cursor()
    cursor.execute("SELECT count(*) FROM users_backup WHERE tags ->> 'SEX'='MALE';")
    male_count = cursor.fetchone()[0]
    cursor.execute("SELECT count(*) FROM users_backup WHERE tags ->> 'SEX'='FEMALE';")
    female_count = cursor.fetchone()[0]
    cursor.execute("SELECT count(*) FROM users_backup;")
    total_count = cursor.fetchone()[0]
    print('Всего пользователей:', total_count)
    print('Мужчин:', male_count)
    print('Женщин:', female_count)
    print('Не указали пол:', total_count - male_count - female_count)
    cursor.execute("SELECT tags['AGE'] FROM users_backup WHERE tags ->> 'SEX'='MALE';")
    age = cursor.fetchall()
    sum_age_male = 0
    count_male = 0
    none_male = 0
    for a in age:  
        if a[0]:
            sum_age_male += a[0]
            count_male +=1
        else:
            none_male += 1
    
    cursor.execute("SELECT tags['AGE'] FROM users_backup WHERE tags ->> 'SEX'='FEMALE';")
    age = cursor.fetchall()
    sum_age_female = 0
    count_female = 0
    none_female = 0
    for a in age:  
        if a[0]:
            sum_age_female += a[0]
            count_female +=1
        else:
            none_female += 1
    print()
    print('Средний возраст')
    print('Мужчин:', sum_age_male/count_male)
    print('Не указали:', none_male)
    print('Женщин:', sum_age_female/count_female)
    print('Не указали:', none_female)

    count_targets = {}
    for t in Targets:
        cursor.execute("SELECT count(1) FROM users_backup WHERE targets ?& array[%s];",
                       (t.name, ))
        count_targets[t.name] = cursor.fetchone()[0]
    sorted_targets = dict(sorted(count_targets.items(), key=lambda item: item[1], reverse=True))
    print()
    for t in sorted_targets:
        print(Targets[t].value, sorted_targets[t])

    conn.commit()
    cursor.close()
    conn.close()


# users = get_users()
# users2 = {}
# targets = get_targets()
# for usr in users:
#     user = users[usr]
#     users2[usr] = User2(user.tg_id, user.username, user.name, user.tags)
#     print(user.name)
#     for t in user.targets:
#         if usr in targets[t].users_hold:
#             a = targets[t].users_hold[usr]
#         else:
#             a = {}
#         print(t, a)
#         users2[usr].targets[t] = a
#     print(users2[usr].targets)
