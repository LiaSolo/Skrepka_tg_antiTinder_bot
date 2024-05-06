from enums import Targets


class Target:
    def __init__(self, name: Targets):
        self.name = name.name
        self.users_hold = {
            # user_id1: options1,
            # user_id2: options2,
            # ...
        }

        # options = {
        #     # sex: ['MALE'],
        #     # age: [20, 40] or 25 or None,
        #     # option3: value3,
        #     # option4: value4,
        #     # ...
        # }


# targets = [ Target.FRIENDS: {
#                               name = FRIENDS
#                               users_hold = {
#                                             111: {
#                                                   SEX: [MALE, FEMALE],
#                                                   AGE: [20, 40]
#                                                  }
#                                            }
#                              },
#            ...]

# users = {
#           111: {
#                   tg_id: 111
#                   name: Kim
#                   username: username
#                   targets: [FRIENDS, SPORT]
#                   tags: {SEX: FEMALE,
#                          AGE: 23
#                         }
#                }
#         }
