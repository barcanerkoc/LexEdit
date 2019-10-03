from src.user import User


class Annotator(User):

    def __init__(self, username):

        super().__init__(username)
        self.username = username
