from typing import Protocol, Optional

from etp.common.solution_descriptor import SolutionDescriptor
from etp.common.test import Test
from etp.testing.test_result import TestResult


class TestResultTracker:
    def __init__(self):
        self.compile_time_fails = {}
        self.results = {}

    def register_test_result(self, solution: SolutionDescriptor, test: Test, result: TestResult):
        self.results[(solution.path, test.index)] = result

    def register_compile_time_fail(self, solution: SolutionDescriptor, result: TestResult):
        self.compile_time_fails[solution.path] = result

    def get_result(self, solution: SolutionDescriptor, test: Test) -> Optional[TestResult]:
        if solution.path in self.compile_time_fails:
            return self.compile_time_fails[solution.path]

        if (solution.path, test.index) in self.results:
            return self.results[(solution.path, test.index)]

        return None
