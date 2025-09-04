import os.path
import subprocess
from pathlib import Path
from typing import List

from etp.common.compile import compile_solution
from etp.common.run import run_solution
from etp.common.solution_descriptor import SolutionDescriptor
from etp.common.test import Test
from etp.testing.cache.cache import get_cached_test_result, cache_test_result
from etp.testing.cache.hashing import hash_file
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

    solution_hash = hash_file(os.path.join(working_dir, solution.name))

    for test in tests:
        io_hash = hash_file(test.input_path)
        io_hash = hash_file(test.output_path, io_hash)

        result = get_cached_test_result(solution.path, test.index,
                                        context.context_hash, solution_hash, io_hash)

        if context.use_cache and result is not None:
            print(f"Result of {solution.path} on test {test.index} is cached, using cache...")
            tracker.register_test_result(solution, test, result)
            continue

        time_limit_ms = context.time_limiter.get_time_limit_ms(test, solution)
        exec_result = run_solution(context.task_config, 
                                   working_dir,
                                   solution,
                                   solution.name,
                                   test,
                                   2 * time_limit_ms,
                                   batchmanager_path=context.batchmanager_path)

        if exec_result.returncode == -1:
            result = TestResult(FailedVerdict.HardTimeLimitExceeded, exec_result.elapsed_time_ms, False)
            cache_test_result(solution.path, test.index, context.context_hash, solution_hash, io_hash, result)
            tracker.register_test_result(solution, test, result)
            continue
        elif exec_result.returncode != 0:
            result = TestResult(FailedVerdict.RuntimeError, exec_result.elapsed_time_ms, False)
            cache_test_result(solution.path, test.index, context.context_hash, solution_hash, io_hash, result)
            tracker.register_test_result(solution, test, result)
            continue

        output_path = os.path.join(".etp", "output", "out")
        with open(output_path, "wb") as out_stream:
            out_stream.write(exec_result.output)

        with open(test.output_path, "rb") as ans_stream:
            ans_bytes = ans_stream.read()

        exact_match = ans_bytes == exec_result.output

        original_score = None
        verdict, message = context.checker.execute_checker(test, output_path)
        if isinstance(verdict, float):
            original_score = verdict
        if exec_result.elapsed_time_ms > time_limit_ms:
            verdict = FailedVerdict.TimeLimitExceeded

        print(f"Verdict: {verdict}, elapsed: {exec_result.elapsed_time_ms}, exact match: {exact_match}")
        result = TestResult(verdict, exec_result.elapsed_time_ms, exact_match, message, original_score)
        cache_test_result(solution.path, test.index, context.context_hash, solution_hash, io_hash, result)
        tracker.register_test_result(solution, test, result)
