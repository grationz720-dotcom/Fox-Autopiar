from vkbottle import Keyboard, KeyboardButtonColor, Text, OpenLink
from dotenv import load_dotenv
import os

load_dotenv('src/config/.env')

menu_keyboard = (
    Keyboard(one_time=False)
    .add(Text('Подать заявку на пиар'), color=KeyboardButtonColor.SECONDARY)
    .row()
    .add(OpenLink(link=os.environ.get('superuser_url', 'http://www.google.com/404'), label=('Обратиться к создателю')), color=KeyboardButtonColor.SECONDARY)
).get_json()