from io import BytesIO
from zipfile import ZipFile
from pathlib import Path

import jinja2

from stat_archivator.entity.common import FileFormat
from stat_archivator.entity.report import Report
from stat_archivator.entity.exc import FormatIsMissing


class ReportArchive:
    """Класс Архива с Отчётами

    Raises:
        FormatIsMissing: Для перепадного формата нет реализации функционала.
    """

    archive: BytesIO
    template_loader: jinja2.FileSystemLoader
    template_env: jinja2.Environment
    report_cnt: int
    available_formats: FileFormat = FileFormat

    def __init__(self, template_path: str, report_cnt: int = 100) -> None:
        """Инициализация класса Архива

        Args:
            template_path (str): Путь к папке с jinja2 шаблонами.
            report_cnt (int, optional): Кол-во отчётов в архиве. Defaults to 100.
        """        
        self.archive = BytesIO()
        self.template_loader = jinja2.FileSystemLoader(searchpath=template_path)
        self.template_env = jinja2.Environment(loader=self.template_loader)
        self.report_cnt = report_cnt

    def make(self, template_name: str, format: FileFormat) -> None:
        """Создание и запись отчётов в нужном формате в архив

        Args:
            template_name (str): Название шаблона по которому будут рендериться отчёт.
            format (FileFormat): Формат для рендеринга.

        Raises:
            FormatIsMissing: Для перепадного формата нет реализации функционала.
        """        
        template = self.template_env.get_template(template_name)

        with ZipFile(self.archive, "w") as zip_archive:
            match format:
                case self.available_formats.xml:
                    for i in range(self.report_cnt):
                        report = Report(xml_template=template)
                        report.save_to_archive(
                            file_name=f"report_{i}", archive=zip_archive, format=format
                        )
                case _:
                    raise FormatIsMissing(format)

    def save(self, archive_name: Path) -> None:
        """Сохранение архива на диске

        Args:
            archive_name (Path): Имя архива.
        """        
        with open(archive_name, "wb") as archive_file:
            archive_file.write(self.archive.getbuffer())
        self.archive.close()