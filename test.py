import language_tool_python

def check_text(text):
    tool = language_tool_python.LanguageTool('ru-RU')
    matches = tool.check(text)
    for match in matches:
        print(f"Ошибка: {match.ruleId}, Сообщение: {match.message}")
        print(f"Исправление: {match.replacements}")

check_text("Я пошол дамой нетрогай миня я хачу лидинец")
check_text("Здравствуйте, дорогие друзья, сегодня наш светский вечер будет ...")