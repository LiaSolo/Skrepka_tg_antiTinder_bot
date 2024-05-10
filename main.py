from telebot import TeleBot
from telebot.types import LinkPreviewOptions, ReplyKeyboardRemove
from config import token
from user import User
from enums import Targets, State, Tags
from keyboards import get_keyboard_delete_profile, get_keyboard_tags, get_keyboard_targets, get_keyboard_for_tag, \
    get_static_keyboard, tags_with_keyboard, text_messages
from db_worker import create_user, delete_user, update_user_target_wishlist, update_user_tags, update_user_targets, \
    get_users, get_targets


bot = TeleBot(token)

targets = get_targets()
users = get_users()
messages_to_delete = {}
non_tags_targets = {}


def check_compatibility(target_name: str, me: User, target_user: User):
    my_tags_for_target = targets[target_name].users_hold[me.tg_id]

    is_match = True
    # print(target_name, me.name, target_user.name)
    for tag in my_tags_for_target:
        # print(tag, is_match)
        if tag in target_user.tags:
            if tag == 'AGE':
                temp_age_array = my_tags_for_target['AGE']
                if len(my_tags_for_target['AGE']) == 2:
                    temp_age_array = [i for i in range(my_tags_for_target['AGE'][0],
                                                       my_tags_for_target['AGE'][1] + 1)]
                if target_user.tags['AGE'] not in temp_age_array:
                    is_match = False
                    break
            elif my_tags_for_target[tag] != target_user.tags[tag]:
                is_match = False
                break
        else:
            is_match = False
            break
    return is_match


def find_people(target_name: str, user: User):
    people_ids = list(targets[target_name].users_hold.keys())
    print(targets[target_name].users_hold)
    print(people_ids)
    result_people = []
    people_ids.remove(user.tg_id)

    for p in people_ids:
        target_user = users[p]
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
    delete_user(user)
    for target in user.targets:
        del targets[target].users_hold[user.tg_id]
        update_user_target_wishlist(targets[target])


@bot.message_handler(commands=['start'])
def start(message):
    from_user = message.from_user
    if from_user.id not in users:
        users[from_user.id] = User(from_user.id, from_user.username, from_user.first_name)
        user = users[from_user.id]
        create_user(user)
    else:
        user = users[from_user.id]

    bot.send_message(user.tg_id, f'Привет, {user.name}', reply_markup=get_static_keyboard())
    bot.send_message(user.tg_id,
                     "Расскажи что-нибудь о себе",
                     reply_markup=get_keyboard_tags(user, 'me'))


@bot.message_handler(content_types=['text'])
def text_worker(message):
    from_user = message.from_user
    if from_user.id in users:
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
    else:
        bot.send_message(chat_id=from_user.id,
                         text="Напиши /start для начала работы с ботом")


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
                targets[data].users_hold[user.tg_id] = {}
            else:
                user.targets.remove(data)
                del targets[data].users_hold[user.tg_id]

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

                # for target in user.targets:
                #     targets[target].users_hold.setdefault(user.tg_id, {})
                update_user_targets(user)

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
        elif data == 'not_delete_profile':
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
                update_user_tags(user)
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
                current_target = non_tags_targets[user.tg_id].pop(0)
                update_user_target_wishlist(targets[current_target])

                if len(non_tags_targets[user.tg_id]) == 0:
                    del non_tags_targets[user.tg_id]

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


# while True:
#     try:
#         bot.polling(none_stop=True, interval=0)
#     except Exception as e:
#         print(e)
bot.polling(none_stop=True, interval=0)
