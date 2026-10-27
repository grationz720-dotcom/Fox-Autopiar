from vkbottle import Keyboard, KeyboardButtonColor, Text

rules_keyboard = (
    Keyboard(one_time=True)
    .add(Text("Принять правила"), color=KeyboardButtonColor.PRIMARY)
).get_json()