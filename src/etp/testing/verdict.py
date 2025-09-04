from enum import Enum
from typing import Union


class FailedVerdict(Enum):
    CompilationError = 1
    RuntimeError = 2
    TimeLimitExceeded = 3  # TL exceeded, but finished in at most double time
    MemoryLimitExceeded = 4
    JudgementFailed = 5  # e.g. checker crash
    UnsupportedLanguage = 6
    HardTimeLimitExceeded = 7  # TL exceeded, terminated before finish


Verdict = Union[float, FailedVerdict]


def get_value(verdict: Verdict) -> float:
    if isinstance(verdict, FailedVerdict):
        return 0.0
    else:
        return verdict
