from enums import State, Sex


class User:
    def __init__(self, tg_id: int, username: str, name: str, tags={}, targets=[]):
        self.tg_id = tg_id
        self.username = username
        self.name = name
        self.targets = targets
        self.tags = tags
        self.position = State.ASK_TARGETS

# users = {
#           111: {
#                   tg_id: 111
#                   name: Kim
#                   username: username
#                   targets: [FRIENDS, SPORT]
#                   tags: {
#                           SEX: FEMALE,
#                           AGE: 23
#                         }
#                }
#         }
