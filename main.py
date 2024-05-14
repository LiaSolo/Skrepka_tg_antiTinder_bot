from telebot import TeleBot
from telebot.types import LinkPreviewOptions, ReplyKeyboardRemove
from config import token
from user import User
# from target import Target
from enums import Targets, State, Tags
from keyboards import get_keyboard_delete_profile, get_keyboard_tags, get_keyboard_targets, get_keyboard_for_tag, \
    get_static_keyboard, tags_with_keyboard, text_messages
from db_worker import create_user, delete_user, update_user_target_wishlist, update_user_tags, update_user_targets, \
    get_users, get_one_user, get_targets, get_one_target, get_target_options_for_user #, add_new_target


bot = TeleBot(token)
# TODO: нахуй убрать таблицу targets, заменить users на users_backup


messages_to_delete = {}
non_tags_targets = {}
temp_user_targets = {}
temp_user_tags_for_current_target = {}
temp_user_tags = {}
user_state = {}

def check_compatibility(target_name: str, me: User, target_user: User):
    targets = get_targets()
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
                    break
            elif my_tags_for_target[tag] != target_user.tags[tag]:
                is_match = False
                break
        else:
            is_match = False
            break
    return is_match


def find_people(target_name: str, user: User):
    targets = get_targets()
    people_ids = list(targets[target_name].users_hold.keys())
    result_people = []
    people_ids.remove(user.tg_id)
    users = get_users()

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
    targets = get_targets()
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
    delete_user(user)
    for tar in user.targets:
        target = get_one_target(tar)
        del target.users_hold[user.tg_id]
        update_user_target_wishlist(target)


@bot.message_handler(commands=['start'])
def start(message):
    from_user = message.from_user
    user = get_one_user(from_user.id)

    if not user:
        user = User(from_user.id, from_user.username, from_user.first_name)
        create_user(user)

    temp_user_tags[user.tg_id] = user.tags
    temp_user_targets[user.tg_id] = user.targets
    print('init', user.name, user.tags, user.targets)
    
    bot.send_message(user.tg_id, f'Привет, {user.name}', reply_markup=get_static_keyboard())
    bot.send_message(user.tg_id,
                     "Расскажи что-нибудь о себе",
                     reply_markup=get_keyboard_tags('me', user.tags))
    


@bot.message_handler(content_types=['text'])
def text_worker(message):
    from_user = message.from_user
    user = get_one_user(from_user.id)

    if user:
        if message.text == 'Удалить анкету':
            bot.send_message(chat_id=user.tg_id,
                             text="Уверен(а)?",
                             reply_markup=get_keyboard_delete_profile())

        elif message.text == 'Редактировать анкету':
            temp_user_tags[user.tg_id] = user.tags
            temp_user_targets[user.tg_id] = user.targets
            bot.send_message(chat_id=user.tg_id,
                             text="Расскажи что-нибудь о себе",
                             reply_markup=get_keyboard_tags('me', user.tags))

        elif message.text == 'Моя анкета':
            bot.send_message(chat_id=user.tg_id,
                             text=print_user_info(user),
                             parse_mode='MarkdownV2')

        elif user_state[user.tg_id] == State.ASK_AGE:
            messages_to_delete[user.tg_id].append(message.id)
            if message.text.isdigit():
                temp_user_tags[user.tg_id]['AGE'] = int(message.text)

                bot.delete_messages(chat_id=user.tg_id,
                                    message_ids=messages_to_delete[user.tg_id])
                del messages_to_delete[user.tg_id]
                bot.send_message(user.tg_id,
                                 text='Расскажи что-нибудь о себе',
                                 reply_markup=get_keyboard_tags('me', temp_user_tags[user.tg_id]))
                del user_state[user.tg_id]

            else:
                messages_to_delete[user.tg_id].append(message.id + 1)
                bot.send_message(user.tg_id,
                                 text="Некорректный ввод.\n"
                                      "Введи свой возраст.")

        elif user_state[user.tg_id] == State.ASK_TARGETS_AGE:
            messages_to_delete[user.tg_id].append(message.id)
            current_target = non_tags_targets[user.tg_id][0]

            age = message.text.split()
            if len(age) == 1 and age[0].isdigit() or \
                    len(age) == 2 and age[0].isdigit() and age[1].isdigit() and int(age[1]) > int(age[0]):
                temp_user_tags_for_current_target[user.tg_id][1]['AGE'] = list(map(int, age))

                bot.delete_messages(chat_id=user.tg_id,
                                    message_ids=messages_to_delete[user.tg_id])
                del messages_to_delete[user.tg_id]

                bot.send_message(user.tg_id,
                                 text="Выбери, какие характеристики ты хочешь указать для цели"
                                      f"\n{Targets[current_target].value}.",
                                 reply_markup=get_keyboard_tags('target', temp_user_tags_for_current_target[user.tg_id][1]))
                del user_state[user.tg_id]

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
    parsed_data = call.data.split()
    user = get_one_user(call.message.chat.id)

    if len(parsed_data) == 1:
        data = parsed_data[0]

        if data in Targets.__members__:
            if data not in temp_user_targets[user.tg_id]:
                temp_user_targets[user.tg_id].append(data)
                #user_options_for_target[user.tg_id] = [data, {}]
                #targets[data].users_hold[user.tg_id] = {}
            else:
                temp_user_targets[user.tg_id].remove(data)
                #del targets[data].users_hold[user.tg_id]
                
            bot.edit_message_reply_markup(chat_id=user.tg_id,
                                          message_id=call.message.id,
                                          reply_markup=get_keyboard_targets(user, temp_user_targets[user.tg_id]))

        elif data == 'chosen_targets':
            if len(temp_user_targets[user.tg_id]) == 0:
                mess = bot.send_message(chat_id=user.tg_id,
                                        text='Нужно выбрать хотя бы одну цель! '
                                             'Иначе зачем это всё?')
                messages_to_delete.setdefault(user.tg_id, []).append(mess.message_id)
            else:
                if user.tg_id in messages_to_delete:
                    bot.delete_messages(chat_id=user.tg_id,
                                        message_ids=messages_to_delete[user.tg_id])
                    del messages_to_delete[user.tg_id]

                user.targets = temp_user_targets[user.tg_id]
                update_user_targets(user)
                non_tags_targets[user.tg_id] = temp_user_targets[user.tg_id]
                current_target = non_tags_targets[user.tg_id][0]

                user_options_for_target = get_target_options_for_user(current_target, user.tg_id)
                if not user_options_for_target:
                    user_options_for_target = [current_target, {}]
                temp_user_tags_for_current_target[user.tg_id] = user_options_for_target
                #user_options_for_target = targets[current_target].users_hold.setdefault(user.tg_id, {})
                
                del temp_user_targets[user.tg_id]
                
                bot.delete_message(chat_id=user.tg_id,
                                   message_id=call.message.id)
                bot.send_message(chat_id=user.tg_id,
                                 text="Выбери, какие характеристики ты хочешь указать для цели"
                                      f"\n{Targets[current_target].value}.",
                                 reply_markup=get_keyboard_tags('target', user_options_for_target[1]))

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
                temp_user_tags[user.tg_id].setdefault(data, None)
                user_options_for_tag = temp_user_tags[user.tg_id][data]

                bot.edit_message_text(chat_id=user.tg_id,
                                      message_id=call.message.id,
                                      text=text_messages[f'{data}-me'],
                                      reply_markup=get_keyboard_for_tag(user, Tags[data], 'me', user_options_for_tag))
                
                if Tags[data] not in tags_with_keyboard:
                    user_state[user.tg_id] = State[f'ASK_{data}']
                    messages_to_delete[user.tg_id] = [call.message.id]

            elif data == 'chosen_tags':
                user.tags = temp_user_tags[user.tg_id]
                update_user_tags(user)
                del temp_user_tags[user.tg_id]
                temp_user_targets[user.tg_id] = user.targets
                bot.edit_message_text(chat_id=user.tg_id,
                                      message_id=call.message.id,
                                      text='Выбери, для каких целей ты ищешь людей.',
                                      reply_markup=get_keyboard_targets(user, temp_user_targets[user.tg_id]))

        elif flag == 'target':
            if data in Tags.__members__:
                current_target = non_tags_targets[user.tg_id][0]

                user_options_for_tag = temp_user_tags_for_current_target[user.tg_id][1].setdefault(data, None)
                bot.edit_message_text(chat_id=user.tg_id,
                                      message_id=call.message.id,
                                      text=text_messages[f'{Tags[data].name}-target'],
                                      reply_markup=get_keyboard_for_tag(user, Tags[data], 'target',
                                                                                user_options_for_tag))

                if Tags[data] not in tags_with_keyboard:
                    user_state[user.tg_id] = State[f'ASK_TARGETS_{data}']
                    messages_to_delete[user.tg_id] = [call.message.id]

            elif data == 'chosen_tags':
                current_target = non_tags_targets[user.tg_id].pop(0)
                target = get_one_target(current_target)
                target.users_hold[user.tg_id] = temp_user_tags_for_current_target[user.tg_id][1]
                update_user_target_wishlist(target)
                del temp_user_tags_for_current_target[user.tg_id]

                if len(non_tags_targets[user.tg_id]) == 0:
                    del non_tags_targets[user.tg_id]

                    preview_disabled = LinkPreviewOptions(True)
                    print('temp_user_tags', temp_user_tags)
                    print('temp_user_targets', temp_user_targets)
                    print('temp_user_tags_for_current_target', temp_user_tags_for_current_target)
                    print('user_state', user_state)
                    print('non_tags_targets', non_tags_targets)
                    print('messages_to_delete', messages_to_delete)
                    for tar in user.targets:

                        bot.send_message(chat_id=user.tg_id,
                                         text=print_results(tar, find_people(tar, user),
                                                            target.users_hold[user.tg_id]),
                                         parse_mode='MarkdownV2',
                                         link_preview_options=preview_disabled)
                    bot.delete_message(chat_id=user.tg_id,
                                       message_id=call.message.id)
                else:
                    current_target = non_tags_targets.setdefault(user.tg_id, user.targets)[0]
                    user_options_for_target = get_target_options_for_user(current_target, user.tg_id)
                    if not user_options_for_target:
                        user_options_for_target = [current_target, {}]
                    temp_user_tags_for_current_target[user.tg_id] = user_options_for_target

                    bot.edit_message_text(chat_id=user.tg_id,
                                          message_id=call.message.id,
                                          text="Выбери, какие характеристики ты хочешь указать"
                                               f"для цели\n{Targets[current_target].value}.",
                                          reply_markup=get_keyboard_tags('target', user_options_for_target[1]))

    elif len(parsed_data) == 3:
        flag, tag, value = parsed_data

        if flag == 'me':
            if value != 'None':
                temp_user_tags[user.tg_id][tag] = value
            else:
                del temp_user_tags[user.tg_id][tag]

            bot.edit_message_text(chat_id=user.tg_id,
                                  message_id=call.message.id,
                                  text='Расскажи что-нибудь о себе',
                                  reply_markup=get_keyboard_tags('me', temp_user_tags[user.tg_id]))
        
        elif flag == 'target':
            current_target = non_tags_targets[user.tg_id][0]
            if value != 'None':
                temp_user_tags_for_current_target[user.tg_id][1][tag] = value
            else:
                del temp_user_tags_for_current_target[user.tg_id][1][tag]

            user_options_for_target = temp_user_tags_for_current_target[user.tg_id][1]

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
