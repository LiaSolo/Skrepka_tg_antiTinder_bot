from enums import State, Sex


class User:
    def __init__(self, tg_id: int, username: str, name: str, tags={}, targets=[]):
        self.tg_id = tg_id
        self.username = username
        self.name = name
        self.targets = targets
        self.tags = tags
        self.position = None

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


class User2:
    def __init__(self, tg_id: int, username: str, name: str, tags: dict, targets: dict):
        self.tg_id = tg_id
        self.username = username
        self.name = name
        self.targets = targets
        self.tags = tags
        self.position = None

# user = {
#     tg_id: 111,
#     name: Kim,
#     username: username,
#     tags: {
#         'SEX': 'FEMALE',
#         'AGE': 23
#     },
#     targets: {
#         'FRIENDS': {
#             'SEX': 'FEMALE',
#             'AGE': [20, 25]
#         },
#         'SPORT': {
#             'AGE': [15, 35]
#         }
#     }
# }


