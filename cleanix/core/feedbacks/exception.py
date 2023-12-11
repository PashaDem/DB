from exceptions import ModelDoesNotExistError


class FeedbackDoesNotExist(ModelDoesNotExistError):
    detail = "Feedback does not exist."
