from typing import List
from zipfile import ZipFile
from io import TextIOWrapper

from bs4 import BeautifulSoup

from stat_archivator.entity.exc import TemplateIsMissing
from stat_archivator.entity.slice_row import Slice, FirstTypeRow, SecondTypeRow


class WalkerArchive:
    """Класс для сбора данных по архиву"""

    chunk_archives: List[str]
    first_slice: Slice
    second_slice: Slice

    def __init__(self, chunk_archives: List[str]) -> None:
        """Инициализация класса

        Args:
            chunk_archives (List[str]): Чанк архивов для обработки, чанки распределяются между тредами в пуле.
        """
        self.chunk_archives = chunk_archives
        self.first_slice = Slice()
        self.second_slice = Slice()

    def parse_report_xml(self, xml_string: str) -> None:
        """Реализация парсинга по шаблону "report.xml"

        Args:
            xml_string (str): Строка с XML.
        """
        root = BeautifulSoup(xml_string, "lxml")
        id, level = root.find_all("var")

        self.first_slice.append(FirstTypeRow(id=id["value"], level=level["value"]))

        for object in root.find_all("object"):
            self.second_slice.append(
                SecondTypeRow(id=id["value"], object_name=object["name"])
            )

    def walk(self, template_name: str) -> None:
        """Проход по архивам для собра срезов

        Args:
            template_name (str): Имя шаблона, по которому рендерились данные.
        """        
        for archive in self.chunk_archives:
            with ZipFile(archive) as zip_archive:
                for item in zip_archive.filelist:
                    with TextIOWrapper(
                        zip_archive.open(item.filename), encoding="utf-8"
                    ) as file:
                        report_string = file.read()

                        match template_name:
                            case "report.xml":
                                self.parse_report_xml(report_string)
                            case _:
                                TemplateIsMissing(template_name)
