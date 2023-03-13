from typing import List
from dataclasses import dataclass


@dataclass
class FirstTypeRow:
    """Класс для записей в первй CSV-файл
    """    
    id: str
    level: int


@dataclass
class SecondTypeRow:
    """Класс для записей во второй CSV-файл
    """    
    id: str
    object_name: str


@dataclass
class Slice:
    """Класс для среза данных из файлов
    """    
    rows: List[FirstTypeRow | SecondTypeRow]

    def __init__(self) -> None:
        self.rows = []

    def append(self, row: FirstTypeRow | SecondTypeRow) -> None:
        self.rows.append(row)
