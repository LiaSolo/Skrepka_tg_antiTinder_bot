from telebot import TeleBot
from telebot.types import LinkPreviewOptions, ReplyKeyboardRemove
from datetime import datetime
from config import token
from user import User2
from enums import Targets, State, Tags
from keyboards import get_keyboard_delete_profile, get_keyboard_tags, get_keyboard_targets, get_keyboard_for_tag, \
    get_static_keyboard, tags_with_keyboard, text_messages
from db_worker import create_user2, delete_user, update_user_tags, update_user_targets, \
    get_all_users, get_users_by_target


bot = TeleBot(token)

users2 = get_all_users()


def is_match_by_target(target_name: str, me: User2, target_user: User2) -> bool:
    my_tags_for_target = me.targets[target_name]
    target_user_tags = target_user.tags

    for tag in my_tags_for_target:
        if tag in target_user_tags:
            if tag == 'AGE':
                if len(my_tags_for_target['AGE']) == 2:
                    min_age = my_tags_for_target['AGE'][0]
                    max_age = my_tags_for_target['AGE'][1]
                    if target_user_tags['AGE'] < min_age or target_user_tags['AGE'] > max_age:
                        return False
                elif target_user.tags['AGE'] != my_tags_for_target['AGE'][0]:
                    return False

            elif my_tags_for_target[tag] != target_user_tags[tag]:
                return False
        else:
            return False
    return True



def find_people_by_target(target_name: str, user: User2) -> list[User2]:

    result_people = []
    people = get_users_by_target(target_name)
    del people[user.tg_id]

    for target_user in people.values():
        if is_match_by_target(target_name, user, target_user) and \
                is_match_by_target(target_name, target_user, user):
            result_people.append(target_user)

    return result_people


def print_user_info(user: User2):
    text = f'Имя: {user.name}\n'
    for tag in user.tags:
        if tag == 'AGE':
            text += f'{Tags[tag].value}: {user.tags[tag]}\n'
        else:
            text += f'{Tags[tag].value}: {tags_with_keyboard[Tags[tag]][user.tags[tag]].value}\n'
    text += 'Цели:\n\n'
    #targets = get_targets()
    for target in user.targets:
        tags_for_target = user.targets[target]
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


def print_results(target_name: str, people: list[User2], tags_for_target):
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


def delete_profile(user: User2):
    delete_user(user)
    del users2[user.tg_id]


@bot.message_handler(commands=['start'])
def start(message):
    log = ' || '
    from_user = message.from_user
    if from_user.id in users2:
        user = users2[from_user.id]
    else:
        user = User2(tg_id=from_user.id,
                    username=from_user.username, 
                    name=from_user.first_name, 
                    tags=dict(), 
                    targets=dict())
        create_user2(user)
        users2[user.tg_id] = user
        log += 'New user! '

    user.print_user()
    log += f'{user.print_user()}\n'
    now = str(datetime.now())

    with open('bot.logs', 'a') as log_file:
            log_file.write(now + log)
    
    bot.send_message(user.tg_id, f'Привет, {user.name}', reply_markup=get_static_keyboard())
    bot.send_message(user.tg_id,
                     "Расскажи что-нибудь о себе",
                     reply_markup=get_keyboard_tags('me', user.tags))
    


@bot.message_handler(content_types=['text'])
def text_worker(message):
    from_user = message.from_user

    if from_user.id in users2:
        user = users2[from_user.id]
    else:
        bot.send_message(chat_id=from_user.id,
                         text='Сначала необходимо зарегистрироваться.\n' \
                              'Для этого нажмите /start')
        return
    
    user.print_user()
    log = f' || {user.tg_id}, message: {message.text}\n'
    now = str(datetime.now())
    with open('bot.logs', 'a') as log_file:
            log_file.write(now + log)


    if message.text == 'Удалить анкету':
        bot.send_message(chat_id=user.tg_id,
                            text="Уверен(а)?",
                            reply_markup=get_keyboard_delete_profile())

    elif message.text == 'Редактировать анкету':
        bot.send_message(chat_id=user.tg_id,
                            text="Расскажи что-нибудь о себе",
                            reply_markup=get_keyboard_tags('me', user.tags))

    elif message.text == 'Моя анкета':
        bot.send_message(chat_id=user.tg_id,
                            text=print_user_info(user),
                            parse_mode='MarkdownV2')

    elif user.state == State.ASK_AGE:
        user.update_messages_to_delete(message.id)
        if message.text.isdigit() and int(message.text) < 200:
            user.tags['AGE'] = int(message.text)

            bot.delete_messages(chat_id=user.tg_id,
                                message_ids=user.messages_to_delete)
            user.update_messages_to_delete(None)
            bot.send_message(user.tg_id,
                                text='Расскажи что-нибудь о себе',
                                reply_markup=get_keyboard_tags('me', user.tags))
            user.state = None

        else:
            user.update_messages_to_delete(message.id + 1)
            bot.send_message(user.tg_id,
                                text="Некорректный ввод.\n"
                                     "Введи свой возраст.")

    elif user.state == State.ASK_TARGETS_AGE:
        user.update_messages_to_delete(message.id)
        current_target = user.not_tagged_targets[0]

        age = message.text.split()
        if len(age) == 1 and age[0].isdigit() or \
                len(age) == 2 and age[0].isdigit() and age[1].isdigit() and int(age[1]) > int(age[0]) and int(age[1]) < 200:
            user.targets[current_target]['AGE'] = list(map(int, age))
            

            bot.delete_messages(chat_id=user.tg_id,
                                message_ids=user.messages_to_delete)
            user.update_messages_to_delete(None)

            bot.send_message(user.tg_id,
                                text="Выбери, какие характеристики ты хочешь указать для цели"
                                    f"\n{Targets[current_target].value}.",
                                reply_markup=get_keyboard_tags('target', user.targets[current_target]))
            user.state = None

        else:
            mess = bot.send_message(user.tg_id,
                                    "Некорректный ввод.\n"
                                    "Введи корректный возраст.")
            user.update_messages_to_delete(mess.message_id)

    else:
            bot.send_message(chat_id=user.tg_id,
                             text="Неопознанная команда!")


@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    parsed_data = call.data.split() 

    if call.message.chat.id in users2:
        user = users2[call.message.chat.id]
    else:
        bot.send_message(chat_id=call.message.chat.id,
                         text='Сначала необходимо зарегистрироваться.\n' \
                              'Для этого нажмите /start')
        return

    user.print_user()
    log = f' || {user.tg_id}, message: {call.data}\n'
    now = str(datetime.now())
    with open('bot.logs', 'a') as log_file:
            log_file.write(now + log)

    if len(parsed_data) == 1:
        data = parsed_data[0]

        if data in Targets.__members__:
            if data not in user.targets:
                user.targets[data] = dict()
            else:
                del user.targets[data]
                
            bot.edit_message_reply_markup(chat_id=user.tg_id,
                                          message_id=call.message.id,
                                          reply_markup=get_keyboard_targets(user.targets))

        elif data == 'chosen_targets':
            if len(user.targets) == 0:
                mess = bot.send_message(chat_id=user.tg_id,
                                        text='Нужно выбрать хотя бы одну цель! '
                                             'Иначе зачем это всё?')
                user.update_messages_to_delete(mess.message_id)

            else:
                if user.messages_to_delete:
                    bot.delete_messages(chat_id=user.tg_id,
                                        message_ids=user.messages_to_delete)
                    user.update_messages_to_delete(None)

                update_user_targets(user)
                user.not_tagged_targets = list(user.targets)
                current_target = user.not_tagged_targets[0]

                user_options_for_target = user.targets[current_target]

                bot.edit_message_text(chat_id=user.tg_id,
                                      message_id=call.message.id,
                                      text="Выбери, какие характеристики ты хочешь указать для цели"
                                           f"\n{Targets[current_target].value}.",
                                           reply_markup=get_keyboard_tags('target', user_options_for_target))

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
                
                user_options_for_tag = user.tags.setdefault(data, None)

                bot.edit_message_text(chat_id=user.tg_id,
                                      message_id=call.message.id,
                                      text=text_messages[f'{data}-me'],
                                      reply_markup=get_keyboard_for_tag(Tags[data], 'me', user_options_for_tag))
                
                if Tags[data] not in tags_with_keyboard:
                    user.state = State[f'ASK_{data}']
                    user.update_messages_to_delete(call.message.id)

            elif data == 'chosen_tags':
                update_user_tags(user)
                bot.edit_message_text(chat_id=user.tg_id,
                                      message_id=call.message.id,
                                      text='Выбери, для каких целей ты ищешь людей.',
                                      reply_markup=get_keyboard_targets(user.targets))

        elif flag == 'target':
            if data in Tags.__members__:
                current_target = user.not_tagged_targets[0]

                user_options_for_tag = user.targets[current_target].setdefault(data, None)
                bot.edit_message_text(chat_id=user.tg_id,
                                      message_id=call.message.id,
                                      text=text_messages[f'{Tags[data].name}-target'],
                                      reply_markup=get_keyboard_for_tag(Tags[data], 'target',
                                                                                user_options_for_tag))

                if Tags[data] not in tags_with_keyboard:
                    user.state = State[f'ASK_TARGETS_{data}']
                    user.update_messages_to_delete(call.message.id)

            elif data == 'chosen_tags':
                current_target = user.not_tagged_targets.pop(0)
                update_user_targets(user)

                if len(user.not_tagged_targets) == 0:
                    user.not_tagged_targets = None

                    log = f' || Find people! {user.print_user()}\n'
                    now = str(datetime.now())
                    with open('bot.logs', 'a') as log_file:
                            log_file.write(now + log)

                    preview_disabled = LinkPreviewOptions(True)
                    for target in user.targets:

                        bot.send_message(chat_id=user.tg_id,
                                         text=print_results(target_name=target, 
                                                            people=find_people_by_target(target, user),
                                                            tags_for_target=user.targets[target]),
                                         parse_mode='MarkdownV2',
                                         link_preview_options=preview_disabled)
                    bot.delete_message(chat_id=user.tg_id,
                                       message_id=call.message.id)
                else:
                    user_options_for_target = user.targets[current_target]
                    bot.edit_message_text(chat_id=user.tg_id,
                                          message_id=call.message.id,
                                          text="Выбери, какие характеристики ты хочешь указать"
                                               f"для цели\n{Targets[current_target].value}.",
                                          reply_markup=get_keyboard_tags('target', user_options_for_target))

    elif len(parsed_data) == 3:
        flag, tag, value = parsed_data

        if flag == 'me':
            if value != 'None':
                user.tags[tag] = value
            else:
                del user.tags[tag]

            bot.edit_message_text(chat_id=user.tg_id,
                                  message_id=call.message.id,
                                  text='Расскажи что-нибудь о себе',
                                  reply_markup=get_keyboard_tags('me', user.tags))
        
        elif flag == 'target':
            current_target = user.not_tagged_targets[0]
            
            if value != 'None':
                user.targets[current_target][tag] = value
            else:
                del user.targets[current_target][tag]

            user_options_for_target = user.targets[current_target]
            bot.edit_message_text(chat_id=user.tg_id,
                                  message_id=call.message.id,
                                  text="Выбери, какие характеристики ты хочешь указать"
                                       f"для цели\n{Targets[current_target].value}.",
                                       reply_markup=get_keyboard_tags('target', user_options_for_target))


while True:
    try:
        bot.polling(none_stop=True, interval=0)
    except Exception as e:
        print(e)
        with open('errors.logs', 'a') as log_file:
            log_file.write(str(e) + '\n\n')
# bot.polling(none_stop=True, interval=0)
