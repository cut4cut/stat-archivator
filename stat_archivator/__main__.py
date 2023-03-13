import csv
import logging
import multiprocessing
import concurrent.futures

from glob import glob
from pathlib import Path
from itertools import repeat
from typing import List

from stat_archivator.entity.slice_row import FirstTypeRow, SecondTypeRow
from stat_archivator.entity import ReportArchive, FileFormat, WalkerArchive


def make_archive(
    id: int, template_name: str, template_path: Path, data_dir: str = "data"
) -> None:
    """Создание архива

    Args:
        id (int): ID архива.
        template_name (str): Название шаблона для сохранения файлов.
        template_path (Path): Путь до шаблонов.
        data_dir (str, optional): Имя папки для хранения архивов. Defaults to "data".
    """
    archive_path = Path(f"{data_dir}/archive_{id}.zip")
    archive = ReportArchive(template_path=template_path)
    archive.make(template_name, FileFormat.xml)
    archive.save(archive_path)


def get_archive_chunk(size: int) -> List[str]:
    """Чанки архивов

    Args:
        size (int): Размера чанка.

    Returns:
        List[str]: Чанк архивов.

    Yields:
        Iterator[List[str]]: Чанк архивов.
    """
    archives = glob(f"{data_dir}/*.zip")
    for i in range(0, len(archives), size):
        yield archives[i : i + size]


def run_walker(archives: List[str], template_name: str) -> WalkerArchive:
    """Запуск прохождения по архиву

    Args:
        archives (List[str]): Чанк архивов.
        template_name (str): Название шаблона для парсинга файлов.

    Returns:
        WalkerArchive: Объект с необходимыми срезами.
    """
    walker = WalkerArchive(chunk_archives=archives)
    walker.walk(template_name=template_name)
    return walker


def save_to_csv(path: Path, cls: type, attr_row: str, walkers: WalkerArchive) -> None:
    """Сохранение срезов в CSV-файле

    Args:
        path (Path): Путь для сохранения.
        cls (type): Класс строки среза данных.
        attr_row (str): Название хранилища с нужным срезом.
        walkers (WalkerArchive): Объект со срезами.
    """
    with open(path, "w", newline="") as file:
        fieldnames = list(cls.__annotations__.keys())
        writer = csv.DictWriter(file, fieldnames=fieldnames)

        writer.writeheader()
        for walker in walkers:
            for row in getattr(walker, attr_row).rows:
                writer.writerow(row.__dict__)


if __name__ == "__main__":

    format = "%(asctime)s: %(message)s"
    logging.basicConfig(format=format, level=logging.INFO, datefmt="%H:%M:%S")

    data_dir = "data"
    archive_cnt = 50
    template_name = "report.xml"
    template_path = Path("./stat_archivator/template")

    cpu_count = multiprocessing.cpu_count()
    chunk_size = archive_cnt // cpu_count

    is_new_data = True
    is_multiprocessing = True

    if is_new_data:
        logging.info("Запуск генерации архивов с данными")
        for i in range(archive_cnt):
            make_archive(i, template_name, template_path, data_dir)
        logging.info("Завершение генерации архивов с данными")

    if is_multiprocessing:
        logging.info("Запуск среза данных в пуле потоков")
        with concurrent.futures.ThreadPoolExecutor(max_workers=cpu_count) as executor:
            walkers = list(
                executor.map(
                    run_walker, get_archive_chunk(chunk_size), repeat(template_name)
                )
            )
        logging.info("Завершение среза данных в пуле потоков")
    else:
        logging.info("Запуск среза данных в одном потоке")
        walkers = []
        for chunk in get_archive_chunk(chunk_size):
            walkers.append(run_walker(chunk, template_name))
        logging.info("Завершение среза данных в одном потоке")

    logging.info("Запуск сохранения среза данных в CSV-файлах")
    for path, cls, attr in (
        (Path(f"{data_dir}/first.csv"), FirstTypeRow, "first_slice"),
        (Path(f"{data_dir}/second.csv"), SecondTypeRow, "second_slice"),
    ):
        save_to_csv(path, cls, attr, walkers)
        logging.info(f"Срез сохранён в файле {path}")
    logging.info("Завершение сохранения среза данных в CSV-файлах")
