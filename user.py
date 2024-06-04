
class User2:
    def __init__(self, tg_id: int, username: str, name: str, tags: dict, targets: dict):
        self.tg_id = tg_id
        self.username = username
        self.name = name
        self.targets = targets
        self.tags = tags
        self.not_tagged_targets = None
        self.messages_to_delete = None
        self.state = None


    def update_messages_to_delete(self, new_message_id: int | None) -> None:
        if not new_message_id:
            self.messages_to_delete = None
        elif self.messages_to_delete:
            self.messages_to_delete.append(new_message_id)
        else:
            self.messages_to_delete = [new_message_id]
            

    def print_user(self):
        text = f'tg_id: {self.tg_id}, username: {self.username}, ' \
               f'name: {self.name}, tags: {self.tags}, targets: {self.targets}'
        print(text)
        return text


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
