from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, List

from etp.common.test import Test


@dataclass
class GenTestGroup:
    points: int
    name: Optional[str] = None
    parameters: List[str] = field(default_factory=list)
    tests: List[Test] = field(default_factory=list)


@dataclass
class Genfile:
    groups: List[GenTestGroup] = field(default_factory=list)
