from enum import Enum
from dataclasses import dataclass


@dataclass
class ValueRange:
    """Вспомогательный класс для типов с диапазоном"""

    min: float
    max: float


@dataclass(frozen=True)
class FileFormat(str, Enum):
    """Класс форматов сохранения отчёта"""

    xml = "xml"
