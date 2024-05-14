from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, \
    KeyboardButton, ReplyKeyboardMarkup
from enums import Tags, Targets, Sex
from user import User


# тэг: какой класс определяет клавиатуру с единственным выбором
tags_with_keyboard = {Tags.SEX: Sex}

text_messages = {'SEX-me': 'Выбери пол',
                 'SEX-target': 'Выбери пол',
                 'AGE-me': 'Введи возраст.\n'
                           'Например: 18',
                 'AGE-target': 'Введи возраст. Это может быть одно число (конкретный возраст) '
                               'или два через пробел (диапазон возрастов).\n'
                               'Например: 20 25',
                 }


def get_static_keyboard():
    keyboard = ReplyKeyboardMarkup()
    button = KeyboardButton(text='Моя анкета')
    keyboard.add(button)
    button = KeyboardButton(text='Редактировать анкету')
    keyboard.add(button)
    button = KeyboardButton(text='Удалить анкету')
    keyboard.add(button)
    return keyboard


def get_keyboard_tags(flag: str, user_options):
    # flag: target | me
    keyboard = InlineKeyboardMarkup()
    for tag in Tags:
        # SEX in {'SEX': None} ?
        if flag == 'me' and tag.name in user_options:
            text_button = f'✅{tag.value}'
        else:
            text_button = tag.value
        button = InlineKeyboardButton(text=text_button, callback_data=f'{flag} {tag.name}')
        keyboard.add(button)
    button = InlineKeyboardButton(text='Я выбрал(а)', callback_data=f'{flag} chosen_tags')
    keyboard.add(button)
    return keyboard


def get_keyboard_for_tag(user: User, tag: Tags, flag: str, user_options_for_tag: dict):
    # flag: target | me
    keyboard = InlineKeyboardMarkup()
    # if is_one_choice:
    if tag in tags_with_keyboard:
        options = tags_with_keyboard[tag]
        for opt in options:
            if (opt.name == user_options_for_tag):
                text_button = f'✅{opt.value}'
            else:
                text_button = opt.value
            button = InlineKeyboardButton(text=text_button, callback_data=f'{flag} {tag.name} {opt.name}')
            keyboard.add(button)
    button = InlineKeyboardButton(text='Не указывать (любой)', callback_data=f'{flag} {tag.name} None')
    keyboard.add(button)
    return keyboard


def get_keyboard_targets(user: User, user_targets):
    keyboard = InlineKeyboardMarkup()
    for target in Targets:
        if target.name in user_targets:
            text_button = f'✅{target.value}'
        else:
            text_button = target.value
        button = InlineKeyboardButton(text=text_button, callback_data=target.name)
        keyboard.add(button)
    button = InlineKeyboardButton(text='Я выбрал(а)', callback_data='chosen_targets')
    keyboard.add(button)
    return keyboard


def get_keyboard_delete_profile():
    keyboard = InlineKeyboardMarkup()
    button = InlineKeyboardButton(text='Нет', callback_data='not_delete_profile')
    keyboard.add(button)
    button = InlineKeyboardButton(text='Да', callback_data='delete_profile')
    keyboard.add(button)
    return keyboard
