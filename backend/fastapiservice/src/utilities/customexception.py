class CustomException(Exception):

    def __init__(self, message, details):
        super().__init__(message)
        self.details = details
