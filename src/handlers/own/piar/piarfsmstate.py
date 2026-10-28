from vkbottle import BaseStateGroup

class AutoSendState(BaseStateGroup):
    WAITING_FOR_TEXT = 0
    WAITING_FOR_TIME = 1