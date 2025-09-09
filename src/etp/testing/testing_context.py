import subprocess
from dataclasses import dataclass
from typing import Protocol, Tuple, Any

from etp.common.solution_descriptor import SolutionDescriptor
from etp.common.test import Test
from etp.config.task_config import TaskConfig
from etp.testing.verdict import Verdict


class CheckerExecutor(Protocol):
    # TODO should checkers have time limits?
    def execute_checker(self, test: Test, output_path: str) -> Tuple[Verdict, str]:
        ...


class DiffChecker(CheckerExecutor):
    def execute_checker(self, test: Test, output_path: str) -> Tuple[Verdict, str]:
        exec_result = subprocess.run(["diff", "-q", "--ignore-trailing-space", "--strip-trailing-cr",
                                      test.output_path, output_path])
        if exec_result.returncode == 0:
            return 1.0, "exact match up to trailing whitespace"
        else:
            return 0.0, "wrong answer"


class TimeLimitProvider:
    def __init__(self, task_config: TaskConfig):
        self.task_config = task_config

    def get_time_limit_ms(self, test: Test, solution: SolutionDescriptor) -> int:
        if solution.language.is_interpreted and self.task_config.time_limit_interpreted is not None:
            return int(self.task_config.time_limit_interpreted * 1000)
        elif self.task_config.time_limit is not None:
            return int(self.task_config.time_limit * 1000)
        else:
            return 2000


@dataclass
class TestingContext:
    checker: CheckerExecutor
    time_limiter: TimeLimitProvider
    task_config: TaskConfig
    context_hash: Any
    use_cache: bool = False
    batchmanager_path: str = None
