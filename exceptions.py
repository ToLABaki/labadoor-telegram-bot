class LabadoorBotException(Exception):
    def __init__(self):
        self._string = ''
    
    def get_string(self):
        return self._string

class EditUsersException(LabadoorBotException):
    def __init__(self):
        self._string = 'Only admins can add and remove users.'

class ShowUsersException(LabadoorBotException):
    def __init__(self):
        self._string = 'Only admins can see all members.'

class EditTokensException(LabadoorBotException):
    def __init__(self):
        self._string = 'Only users can generate and invalidate tokens.'

class ShowTokensException(LabadoorBotException):
    def __init__(self):
        self._string = 'Only admins can see all tokens.'

