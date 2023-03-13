class FormatIsMissing(Exception):
    def __init__(self, *args):
        self.message = f"Формат '{args[0]}' не доступен для работы"

    def __str__(self):
        return f"FormatIsMissing, {self.message}"


class UnsuitableTemplateType(Exception):
    def __init__(self, *args):
        self.message = f"В конструктор класса передан некорректный тип данных {args[0]}, ожидается jinja2.Template"

    def __str__(self):
        return f"UnsuitableTemplateType, {self.message}"


class TemplateIsMissing(Exception):
    def __init__(self, *args):
        self.message = f"Шаблон '{args[0]}' не доступен для работы"

    def __str__(self):
        return f"TemplateIsMissing, {self.message}"
