from enum import Enum, auto


class State(Enum):
    ASK_AGE = auto()
    ASK_TARGETS_AGE = auto()


class Targets(Enum):
    RELATIONSHIP = 'Отношения'
    SERIOUS_RELATIONSHIP = 'Серьезные отношения'
    FRIENDS = 'Друзья'
    TRAVEL = 'Путешествовать вместе'
    MENTORING = 'Менторство'
    SPORT = 'Занятия спортом'
    COWORKING = 'Совместная учеба/работа'
    SHOPPING = 'Шоппинг'
    DOG_WALKING = 'Прогулка с собакой'
    OUTDOOR_RECREATION = 'Отдых на природе'
    CONVERSATION = 'Разговоры по душам'
    WALKING = 'Прогулки'
    CINEMA = 'Просмотр кино'
    EVENTS = 'Посещение мероприятий'


class Sex(Enum):
    MALE = 'Мужчина'
    FEMALE = 'Женщина'


class Tags(Enum):
    AGE = 'Возраст'
    SEX = 'Пол'
