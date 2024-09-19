import os.path
import subprocess
from pathlib import Path
from typing import List

from etp.common.compile import compile_solution
from etp.common.run import run_solution
from etp.common.solution_descriptor import SolutionDescriptor
from etp.common.test import Test
from etp.testing.test_result import TestResult
from etp.testing.test_result_tracker import TestResultTracker
from etp.testing.testing_context import TestingContext
from etp.testing.verdict import FailedVerdict


def test_solution(solution: SolutionDescriptor,
                  context: TestingContext,
                  tests: List[Test],
                  tracker: TestResultTracker):
    print(f"Testing solution at {solution.path}...")

    working_dir = os.path.join(".etp", "working")
    Path(working_dir).mkdir(parents=True, exist_ok=True)
    Path(".etp", "output").mkdir(parents=True, exist_ok=True)

    try:
        compile_solution(solution, os.path.join(working_dir, solution.name))
    except (subprocess.TimeoutExpired, subprocess.CalledProcessError):
        tracker.register_compile_time_fail(solution, TestResult(FailedVerdict.CompilationError))
        return

    for test in tests:
        time_limit_ms = context.time_limiter.get_time_limit_ms(test, solution)
        exec_result = run_solution(context.task_config, 
                                   working_dir,
                                   solution,
                                   solution.name,
                                   test,
                                   2 * time_limit_ms)

        if exec_result.returncode == -1:
            tracker.register_test_result(solution, test, TestResult(FailedVerdict.TimeLimitExceeded, 
                                                                    exec_result.elapsed_time_ms, False))
            continue
        elif exec_result.returncode != 0:
            tracker.register_test_result(solution, test, TestResult(FailedVerdict.RuntimeError, 
                                                                    exec_result.elapsed_time_ms, False))
            continue

        output_path = os.path.join(".etp", "output", "out")
        with open(output_path, "wb") as out_stream:
            out_stream.write(exec_result.output)

        with open(test.output_path, "rb") as ans_stream:
            ans_bytes = ans_stream.read()

        exact_match = ans_bytes == exec_result.output

        verdict, message = context.checker.execute_checker(test, output_path)
        if exec_result.elapsed_time_ms > time_limit_ms:
            verdict = FailedVerdict.TimeLimitExceeded

        print(f"Verdict: {verdict}, elapsed: {exec_result.elapsed_time_ms}, exact match: {exact_match}")
        tracker.register_test_result(solution, test, TestResult(verdict, exec_result.elapsed_time_ms, exact_match))
