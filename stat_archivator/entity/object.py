from uuid import uuid4
from dataclasses import dataclass


@dataclass
class Object:
    """Класс Объект"""

    name: str

    def __init__(self) -> None:
        self.name = uuid4()
