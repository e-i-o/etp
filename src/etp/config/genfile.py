from dataclasses import dataclass, field
from typing import Optional, List, Dict, Set

from etp.common.test import Test


@dataclass
class GenTestGroup:
    points: int
    parameters: List[str] = field(default_factory=list)
    named_parameters: Dict = field(default_factory=list)
    tests: List[Test] = field(default_factory=list)
    shadow_tests: Set[int] = field(default_factory=set)  # set of test indices imported as dependencies

    @property
    def name(self) -> Optional[str]:
        if "name" in self.named_parameters:
            return self.named_parameters["name"]
        else:
            return None

    @property
    def deps(self) -> List[str]:
        if "deps" in self.named_parameters:
            return self.named_parameters["deps"]
        else:
            return []


@dataclass
class Genfile:
    tests: List[Test] = field(default_factory=list)
    groups: List[GenTestGroup] = field(default_factory=list)
