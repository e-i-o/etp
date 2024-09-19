from dataclasses import dataclass
from typing import List


@dataclass
class Evaluation:
    codename: int  # actually test index
    outcome: float
    execution_time: int
    execution_memory: int
    text: str  # checker comment?


@dataclass
class SubmissionResult:
    evaluations: List[Evaluation]