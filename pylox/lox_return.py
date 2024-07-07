from dataclasses import dataclass
from typing import Any


@dataclass
class Return(Exception):
    value: Any
