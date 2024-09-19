from dataclasses import dataclass
from typing import Optional

from etp.testing.verdict import Verdict


@dataclass
class TestResult:
    verdict: Verdict
    time_milliseconds: Optional[int] = None
    exact_match: Optional[bool] = None
