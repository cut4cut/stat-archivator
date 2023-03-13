from uuid import uuid4
from random import randint
from zipfile import ZipFile
from typing import Annotated, List

import jinja2

from stat_archivator.entity.object import Object
from stat_archivator.entity.common import ValueRange, FileFormat
from stat_archivator.entity.exc import FormatIsMissing, UnsuitableTemplateType


class Report:
    """Класс Отчёт

    Raises:
        UnsuitableTemplateType: Ошибка при не подходящем типе шаблона для сохранения отчёта.
        FormatIsMissing: Для перепадного формата нет реализации функционала.
    """

    id: str
    level: Annotated[int, ValueRange(1, 100)]
    objects: List[Object]
    objects_cnt: Annotated[int, ValueRange(1, 10)]
    xml_template: jinja2.Template
    xml_rendered: str
    available_formats: FileFormat = FileFormat

    def __init__(
        self,
        xml_template: jinja2.Template,
        min_lvl: int = 1,
        max_lvl: int = 100,
        min_cnt: int = 1,
        max_cnt: int = 10,
    ) -> None:
        """Инициализация класса Отчёта

        Args:
            xml_template (Template): Шаблон для сохранения отчета в формате XML.
            min_lvl (int, optional): Мин. значение уровня. Defaults to 1.
            max_lvl (int, optional): Макс. значение уровня. Defaults to 100.
            min_cnt (int, optional): Мин. значение кол-ва объектов. Defaults to 1.
            max_cnt (int, optional): Макс. значение кол-ва объектов. Defaults to 10.
        Raises:
            UnsuitableTemplateType: Ошибка при не подходящем типе шаблона для сохранения отчёта.
        """
        if not isinstance(xml_template, jinja2.Template):
            raise UnsuitableTemplateType(type(xml_template))

        self.id = uuid4()
        self.level = randint(min_lvl, max_lvl)
        self.objects_cnt = randint(min_cnt, max_cnt)
        self.objects = [Object() for _ in range(self.objects_cnt)]
        self.xml_template = xml_template
        self.xml_rendered = self.render(format=self.available_formats.xml)

    def render(self, format: FileFormat) -> str:
        """Ренедринг отчета по шаблону нужного формата

        Args:
            format (FileFormat): Формат шаблона для рендеринга отчёта.

        Raises:
            FormatIsMissing: Для перепадного формата нет реализации функционала.

        Returns:
            str: Отренедеренный отчёт в заданном формате.
        """
        match format:
            case self.available_formats.xml:
                return self.xml_template.render(
                    id=self.id, level=self.level, objects=self.objects
                )
            # case self.available_formats.html:
            # ...
            case _:
                raise FormatIsMissing(format)

    def save_to_archive(
        self, file_name: str, archive: ZipFile, format: FileFormat
    ) -> None:
        """Сохранение отчёта в архиве

        Args:
            file_name (str): Название архива для сохранения.
            archive (ZipFile): Архив в котором будет сохранен отчёт.
            format (FileFormat): Формат шаблона для сохранения отчёта.

        Raises:
            FormatIsMissing: Для перепадного формата нет реализации функционала.
        """
        with archive.open(f"{file_name}.{format}", "w") as file:
            match format:
                case self.available_formats.xml:
                    file.write(bytes(self.xml_rendered, encoding="UTF-8"))
                # case self.available_formats.html:
                # ...
                case _:
                    raise FormatIsMissing(format)
