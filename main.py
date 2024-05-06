import random

from telebot import TeleBot
from telebot.types import LinkPreviewOptions, ReplyKeyboardRemove
from config import token
from user import User
from target import Target
from enums import Targets, State
from keyboards import get_keyboard_delete_profile, get_keyboard_tags, get_keyboard_targets, get_keyboard_for_tag, \
    get_static_keyboard, tags_with_keyboard, text_messages


bot = TeleBot(token)


def get_phantoms(targs):
    kim = User(111, 'username', 'Kim')
    kim.targets += [targs['CINEMA'].name, targs['RELATIONSHIP'].name, targs['FRIENDS'].name]
    kim.tags = {'SEX': 'FEMALE', 'AGE': random.randint(18, 35)}

    lola = User(222, 'username', 'Lola')
    lola.targets += [targs['RELATIONSHIP'].name, targs['FRIENDS'].name, targs['TRAVEL'].name]
    lola.tags = {'SEX': 'FEMALE', 'AGE': random.randint(18, 35)}

    tom = User(333, 'username', 'Tom')
    tom.targets += [targs['FRIENDS'].name, targs['TRAVEL'].name, targs['MENTORING'].name]
    tom.tags = {'SEX': 'MALE', 'AGE': random.randint(18, 35)}

    alex = User(444, 'username', 'Alex')
    alex.targets += [targs['TRAVEL'].name, targs['MENTORING'].name, targs['SPORT'].name]
    alex.tags = {'SEX': 'MALE', 'AGE': random.randint(18, 35)}

    oleg = User(555, 'username', 'Oleg')
    oleg.targets += [targs['MENTORING'].name, targs['SPORT'].name, targs['COWORKING'].name]
    oleg.tags = {'SEX': 'MALE', 'AGE': random.randint(18, 35)}

    sonya = User(666, 'username', 'Sonya')
    sonya.targets += [targs['SPORT'].name, targs['COWORKING'].name, targs['SHOPPING'].name]
    sonya.tags = {'SEX': 'FEMALE', 'AGE': random.randint(18, 35)}

    emma = User(777, 'username', 'Emma')
    emma.targets += [targs['COWORKING'].name, targs['SHOPPING'].name, targs['DOG_WALKING'].name]
    emma.tags = {'SEX': 'FEMALE', 'AGE': random.randint(18, 35)}

    mark = User(888, 'username', 'Mark')
    mark.targets += [targs['SHOPPING'].name, targs['DOG_WALKING'].name, targs['OUTDOOR_RECREATION'].name]
    mark.tags = {'SEX': 'MALE', 'AGE': random.randint(18, 35)}

    bob = User(999, 'username', 'Bob')
    bob.targets += [targs['WALKING'].name, targs['EVENTS'].name, targs['CONVERSATION'].name]
    bob.tags = {'SEX': 'MALE', 'AGE': random.randint(18, 35)}

    viktor = User(59278868, 'VitOK', 'Viktor')
    viktor.targets += [target for target in targs]
    viktor.tags = {'SEX': 'MALE', 'AGE': random.randint(18, 35)}

    init_users = {111: kim,
                 222: lola,
                 333: tom,
                 444: alex,
                 555: oleg,
                 666: sonya,
                 777: emma,
                 888: mark,
                 999: bob,
                 59278868: viktor}
    return init_users


targets = {target.name: Target(target) for target in Targets}
users = get_phantoms(targets)
messages_to_delete = {}
non_tags_targets = {}

for key in users:
    _usr = users[key]
    for _target in _usr.targets:
        if key % 2 == 0:
            targets[_target].users_hold[key] = {'SEX': 'MALE'}
        else:
            targets[_target].users_hold[key] = {'SEX': 'FEMALE'}
        targets[_target].users_hold[key]['AGE'] = [random.randint(18, 35), random.randint(36, 60)]


def check_compatibility(target_name: str, me: User, target_user: User):
    my_tags_for_target = targets[target_name].users_hold[me.tg_id]

    is_match = True
    for tag in my_tags_for_target:
        if tag in target_user.tags:
            if tag == 'AGE':
                temp_age_array = my_tags_for_target['AGE']
                if len(my_tags_for_target['AGE']) == 2:
                    temp_age_array = [i for i in range(my_tags_for_target['AGE'][0],
                                                       my_tags_for_target['AGE'][1] + 1)]
                if target_user.tags['AGE'] not in temp_age_array:
                    is_match = False
                    continue
            elif my_tags_for_target[tag] != target_user.tags[tag]:
                is_match = False
                continue
        is_match = False
        continue
    return is_match


def find_people(target_name: str, user: User):
    people_ids = list(targets[target_name].users_hold.keys())
    result_people = []
    people_ids.remove(user.tg_id)

    # print('me', my_tags_for_target)
    for p in people_ids:
        target_user = users[p]
        # print(target_user.name, target_user.tags)
        if check_compatibility(target_name, user, target_user) and \
                check_compatibility(target_name, target_user, user):
            result_people.append(target_user)

    return result_people


def print_user_info(user: User):
    text = f'Имя: {user.name}\n'
    for tag in user.tags:
        if tag == 'AGE':
            text += f'{Tags[tag].value}: {user.tags[tag]}\n'
        else:
            text += f'{Tags[tag].value}: {tags_with_keyboard[Tags[tag]][user.tags[tag]].value}\n'
    text += 'Цели:\n\n'
    for target in user.targets:
        # text += str({Targets[target].value}) + '\n'
        # text += str(targets[target].users_hold[user.tg_id]) + '\n\n'

        tags_for_target = targets[target].users_hold[user.tg_id]
        text += f'*{Targets[target].value}*\n\n'
        if len(tags_for_target) > 0:
            text += 'Твои пожелания:\n'
        for tag in tags_for_target:
            if tag == 'AGE':
                if len(tags_for_target[tag]) == 2:
                    text += f'{Tags[tag].value}: от {tags_for_target[tag][0]} до {tags_for_target[tag][1]}\n'
                else:
                    text += f'{Tags[tag].value}: {tags_for_target[tag][0]}\n'
            else:
                text += f'{Tags[tag].value}: {tags_with_keyboard[Tags[tag]][tags_for_target[tag]].value}\n'
        text += '\n'

    return text


def print_results(target_name: str, people: list[User], tags_for_target):
    text = f'*{Targets[target_name].value}*\n\n'
    if len(tags_for_target) > 0:
        text += 'Твои пожелания:\n'
    for tag in tags_for_target:
        if tag == 'AGE':
            if len(tags_for_target[tag]) == 2:
                text += f'{Tags[tag].value}: от {tags_for_target[tag][0]} до {tags_for_target[tag][1]}\n'
            else:
                text += f'{Tags[tag].value}: {tags_for_target[tag][0]}\n'
        else:
            text += f'{Tags[tag].value}: {tags_with_keyboard[Tags[tag]][tags_for_target[tag]].value}\n'
    i = 1
    for p in people:
        link = p.username
        text += f'{i}\. [{p.name}](https://t.me/{link})'
        if 'AGE' in p.tags:
            text += f', {p.tags["AGE"]}'
        text += '\n'
        i += 1

    return text


def delete_profile(user: User):
    del users[user.tg_id]
    for target in user.targets:
        del targets[target].users_hold[user.tg_id]


@bot.message_handler(commands=['start'])
def start(message):
    from_user = message.from_user
    user = users.setdefault(from_user.id, User(from_user.id, from_user.username, from_user.first_name))

    bot.send_message(user.tg_id, f'Привет, {user.name}', reply_markup=get_static_keyboard())
    bot.send_message(user.tg_id,
                     "Расскажи что-нибудь о себе",
                     reply_markup=get_keyboard_tags(user, 'me'))


@bot.message_handler(content_types=['text'])
def text_worker(message):
    from_user = message.from_user
    user = users[from_user.id]

    if message.text == 'Удалить анкету':
        bot.send_message(chat_id=user.tg_id,
                         text="Уверен(а)?",
                         reply_markup=get_keyboard_delete_profile())

    elif message.text == 'Редактировать анкету':
        from_user = message.from_user
        user = users.setdefault(from_user.id, User(from_user.id, from_user.username, from_user.first_name))

        bot.send_message(chat_id=user.tg_id,
                         text="Расскажи что-нибудь о себе",
                         reply_markup=get_keyboard_tags(user, 'me'))

    elif message.text == 'Моя анкета':
        bot.send_message(chat_id=user.tg_id,
                         text=print_user_info(user),
                         parse_mode='MarkdownV2')

    elif user.position == State.ASK_AGE:
        messages_to_delete[user.tg_id].append(message.id)
        if message.text.isdigit():
            user.tags['AGE'] = int(message.text)

            bot.delete_messages(chat_id=user.tg_id,
                                message_ids=messages_to_delete[user.tg_id])
            del messages_to_delete[user.tg_id]
            bot.send_message(user.tg_id,
                             text='Расскажи что-нибудь о себе',
                             reply_markup=get_keyboard_tags(user, 'me'))
            user.position = None

        else:
            messages_to_delete[user.tg_id].append(message.id + 1)
            bot.send_message(user.tg_id,
                             text="Некорректный ввод.\n"
                                  "Введи свой возраст.")

    elif user.position == State.ASK_TARGETS_AGE:
        messages_to_delete[user.tg_id].append(message.id)
        current_target = non_tags_targets[user.tg_id][0]

        age = message.text.split()
        if len(age) == 1 and age[0].isdigit() or \
                len(age) == 2 and age[0].isdigit() and age[1].isdigit() and int(age[1]) > int(age[0]):
            targets[current_target].users_hold[user.tg_id]['AGE'] = list(map(int, age))

            bot.delete_messages(chat_id=user.tg_id,
                                message_ids=messages_to_delete[user.tg_id])
            del messages_to_delete[user.tg_id]

            user_options_for_target = targets[current_target].users_hold[user.tg_id]
            bot.send_message(user.tg_id,
                             text="Выбери, какие характеристики ты хочешь указать для цели"
                                  f"\n{Targets[current_target].value}.",
                             reply_markup=get_keyboard_tags(user, 'target', user_options_for_target))
            user.position = None

        else:
            mess = bot.send_message(user.tg_id,
                                    "Некорректный ввод.\n"
                                    "Введи корректный возраст.")
            messages_to_delete[user.tg_id].append(mess.message_id)

    else:
        bot.send_message(chat_id=user.tg_id,
                         text="Неопознанная команда!")


@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    # print(call.data)
    parsed_data = call.data.split()
    user = users[call.from_user.id]

    if len(parsed_data) == 1:
        data = parsed_data[0]

        if data in Targets.__members__:
            if data not in user.targets:
                user.targets.append(data)
            else:
                user.targets.remove(data)

            bot.edit_message_reply_markup(chat_id=user.tg_id,
                                          message_id=call.message.id,
                                          reply_markup=get_keyboard_targets(user))

        elif data == 'chosen_targets':
            if len(user.targets) == 0:
                mess = bot.send_message(chat_id=user.tg_id,
                                        text='Нужно выбрать хотя бы одну цель! '
                                             'Иначе зачем это всё?')
                messages_to_delete.setdefault(user.tg_id, []).append(mess.message_id)
            else:
                if user.tg_id in messages_to_delete:
                    bot.delete_messages(chat_id=user.tg_id,
                                        message_ids=messages_to_delete[user.tg_id])
                    del messages_to_delete[user.tg_id]

                for target in user.targets:
                    targets[target].users_hold.setdefault(user.tg_id, {})
                current_target = non_tags_targets.setdefault(user.tg_id, user.targets.copy())[0]
                user_options_for_target = targets[current_target].users_hold.setdefault(user.tg_id, {})
                bot.delete_message(chat_id=user.tg_id,
                                   message_id=call.message.id)
                bot.send_message(chat_id=user.tg_id,
                                 text="Выбери, какие характеристики ты хочешь указать для цели"
                                      f"\n{Targets[current_target].value}.",
                                 reply_markup=get_keyboard_tags(user, 'target', user_options_for_target))

        elif data == 'delete_profile':
            bot.delete_message(chat_id=user.tg_id,
                                message_id=call.message.id)
            bot.send_message(chat_id=user.tg_id,
                             text="Надеюсь, ты нашел/нашла того, кого искал(а).\n"
                                  "До новых встреч!💕",
                             reply_markup=ReplyKeyboardRemove())
            delete_profile(user)
        else:
            bot.edit_message_text(chat_id=user.tg_id,
                                  message_id=call.message.id,
                                  text="Рад, что ты остаёшься!❤️")

    elif len(parsed_data) == 2:
        flag, data = parsed_data

        if flag == 'me':
            if data in Tags.__members__:
                if data not in user.tags:
                    user.tags[data] = None
                bot.edit_message_text(chat_id=user.tg_id,
                                      message_id=call.message.id,
                                      text=text_messages[f'{Tags[data].name}-me'])
                bot.edit_message_reply_markup(chat_id=user.tg_id,
                                              message_id=call.message.id,
                                              reply_markup=get_keyboard_for_tag(user, Tags[data], 'me'))
                if Tags[data] not in tags_with_keyboard:
                    user.position = State[f'ASK_{data}']
                    messages_to_delete[user.tg_id] = [call.message.id]

            elif data == 'chosen_tags':
                bot.edit_message_text(chat_id=user.tg_id,
                                      message_id=call.message.id,
                                      text='Выбери, для каких целей ты ищешь людей.')
                bot.edit_message_reply_markup(chat_id=user.tg_id,
                                              message_id=call.message.id,
                                              reply_markup=get_keyboard_targets(user))

        elif flag == 'target':
            if data in Tags.__members__:
                current_target = non_tags_targets[user.tg_id][0]
                targets[current_target].users_hold[user.tg_id].setdefault(data, None)
                user_options_for_tag = targets[current_target].users_hold[user.tg_id][data]
                bot.edit_message_text(chat_id=user.tg_id,
                                      message_id=call.message.id,
                                      text=text_messages[f'{Tags[data].name}-target'])
                bot.edit_message_reply_markup(chat_id=user.tg_id,
                                              message_id=call.message.id,
                                              reply_markup=get_keyboard_for_tag(user, Tags[data], 'target',
                                                                                user_options_for_tag))
                if Tags[data] not in tags_with_keyboard:
                    user.position = State[f'ASK_TARGETS_{data}']
                    messages_to_delete[user.tg_id] = [call.message.id]

            elif data == 'chosen_tags':
                non_tags_targets[user.tg_id].pop(0)
                if len(non_tags_targets[user.tg_id]) == 0:
                    del non_tags_targets[user.tg_id]

                    # for usr_id in users:
                    #     print(print_user_info(users[usr_id]))

                    preview_disabled = LinkPreviewOptions(True)
                    for target in user.targets:

                        bot.send_message(chat_id=user.tg_id,
                                         text=print_results(target, find_people(target, user),
                                                            targets[target].users_hold[user.tg_id]),
                                         parse_mode='MarkdownV2',
                                         link_preview_options=preview_disabled)
                    bot.delete_message(chat_id=user.tg_id,
                                       message_id=call.message.id)
                else:
                    current_target = non_tags_targets.setdefault(user.tg_id, user.targets)[0]
                    user_options_for_target = targets[current_target].users_hold.setdefault(user.tg_id, {})
                    bot.edit_message_text(chat_id=user.tg_id,
                                          message_id=call.message.id,
                                          text="Выбери, какие характеристики ты хочешь указать"
                                               f"для цели\n{Targets[current_target].value}.",
                                          reply_markup=get_keyboard_tags(user, 'target', user_options_for_target))

    elif len(parsed_data) == 3:
        flag, tag, value = parsed_data

        if flag == 'me':
            if value != 'None':
                user.tags[tag] = value
            else:
                del user.tags[tag]

            bot.edit_message_text(chat_id=user.tg_id,
                                  message_id=call.message.id,
                                  text='Расскажи что-нибудь о себе')
            bot.edit_message_reply_markup(chat_id=user.tg_id,
                                          message_id=call.message.id,
                                          reply_markup=get_keyboard_tags(user, 'me'))
        elif flag == 'target':
            current_target = non_tags_targets[user.tg_id][0]
            if value != 'None':
                targets[current_target].users_hold[user.tg_id][tag] = value
            else:
                del targets[current_target].users_hold[user.tg_id][tag]

            user_options_for_target = targets[current_target].users_hold[user.tg_id]
            bot.edit_message_text(chat_id=user.tg_id,
                                  message_id=call.message.id,
                                  text="Выбери, какие характеристики ты хочешь указать"
                                       f"для цели\n{Targets[current_target].value}.")
            bot.edit_message_reply_markup(chat_id=user.tg_id,
                                          message_id=call.message.id,
                                          reply_markup=get_keyboard_tags(user, 'target', user_options_for_target))


while True:
    try:
        bot.polling(none_stop=True, interval=0)
    except Exception as e:
        print(e)
