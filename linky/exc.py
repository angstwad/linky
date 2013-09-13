class UserNotFoundException(Exception):
    def __init__(self, message):
        self.message = message


class UserNotVerifiedException(Exception):
    def __init__(self, message):
        self.message = message


class OverEmailSentLimitException(Exception):
        def __init__(self, message):
            self.message = message


class FormDoesntLookRightException(Exception):
    def __init__(self, message):
        self.message = message
