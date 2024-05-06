from enums import State, Sex


class User:
    # bio??
    def __init__(self, tg_id: int, username: str, name: str):
        self.tg_id = tg_id
        self.username = username
        self.name = name
        self.targets = []
        self.tags = {
            # 'SEX': 'MALE',
            # 'AGE': 25,
        }
        self.position = State.ASK_TARGETS
