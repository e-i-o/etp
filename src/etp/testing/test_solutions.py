import itertools
import os.path
from typing import List, Tuple, Any

from tabulate import tabulate

from etp.common.solution_descriptor import get_solution_descriptor, SolutionDescriptor
from etp.common.test import Test
from etp.config.genfile import Genfile
from etp.config.make_all import make_all_check
from etp.config.task_config import TaskConfig
from etp.etp_exception import UnsupportedLanguageException
from etp.print_utils import yellow_bold
from etp.testing.cms_checker_executor import CmsCheckerExecutor
from etp.testing.format_result import format_result, format_subtask_result, format_total_result
from etp.testing.scoretypes.GroupMin import GroupMin
from etp.testing.scoretypes.GroupMul import GroupMul
from etp.testing.scoretypes.GroupSum import GroupSum
from etp.testing.scoretypes.GroupSumCheck import GroupSumCheck
from etp.testing.scoretypes.GroupSumCond import GroupSumCond
from etp.testing.scoretypes.ScoreType import ScoreType
from etp.testing.scoretypes.adapters import Evaluation, SubmissionResult
from etp.testing.test_result import TestResult
from etp.testing.test_result_tracker import TestResultTracker
from etp.testing.test_solution import test_solution
from etp.testing.testing_context import DiffChecker, TimeLimitProvider, TestingContext
from etp.testing.verdict import FailedVerdict, get_value


def create_table(tests: List[Test], solutions: List[SolutionDescriptor],
                 tracker: TestResultTracker) -> List[List[str]]:
    table = [[""] * (1 + len(solutions)) for _ in range(1 + len(tests))]

    for j, solution in enumerate(solutions):
        table[0][j + 1] = os.path.basename(solution.path)

    for i, test in enumerate(tests):
        table[i + 1][0] = str(test.index)
        for j, solution in enumerate(solutions):
            table[i + 1][j + 1] = format_result(tracker.get_result(solution, test))

    return table


def get_scorer(task_config: TaskConfig, genfile: Genfile) -> ScoreType:
    if task_config.score_type == "GroupSum":
        return GroupSum(genfile)
    elif task_config.score_type == "GroupSumCheck":
        return GroupSumCheck(genfile)
    elif task_config.score_type == "GroupSumCond":
        return GroupSumCond(genfile)
    elif task_config.score_type == "GroupMin":
        return GroupMin(genfile)
    elif task_config.score_type == "GroupMul":
        return GroupMul(genfile)
    elif task_config.score_type == "Sum":
        return GroupSum(genfile)
    elif not task_config.score_type:
        print(yellow_bold("WARN:"), "score_type not set, falling back to GroupSum")
        return GroupSum(genfile)
    else:
        print(yellow_bold("WARN:"), f"unknown score_type {task_config.score_type}, falling back to GroupSum")
        return GroupSum(genfile)


def calculate_score(tests: List[Test], solution: SolutionDescriptor,
                    tracker: TestResultTracker, scorer: ScoreType) -> Tuple[float, Any]:
    evaluations = []
    for test in tests:
        result = tracker.get_result(solution, test)
        evaluations.append(Evaluation(test.index, get_value(result.verdict), result.time_milliseconds, 0, ""))

    return scorer.compute_score(SubmissionResult(evaluations))


def create_subtask_table(tests: List[Test], solutions: List[SolutionDescriptor],
                         scorer: ScoreType, tracker: TestResultTracker, genfile: Genfile) -> List[List[str]]:
    scores = {}
    for solution in solutions:
        scores[solution.path] = calculate_score(tests, solution, tracker, scorer)

    table = [[""] * (1 + len(solutions)) for _ in range(2 + len(genfile.groups))]

    for j, solution in enumerate(solutions):
        table[0][j + 1] = os.path.basename(solution.path)

        max_score = 0
        score, subtasks = scores[solution.path]
        for i, subtask in enumerate(subtasks):
            table[i + 1][j + 1] = format_subtask_result(subtask)
            max_score += subtask["max_score"]

        table[-1][j + 1] = format_total_result(score, max_score)

    for i, group in enumerate(genfile.groups):
        table[i + 1][0] = group.name
    table[-1][0] = "Total"

    return table


def test_solutions(task_config: TaskConfig, genfile: Genfile, solutions: List[str]):
    make_all_check()
    if os.path.isfile(os.path.join("check", "checker")):
        checker = CmsCheckerExecutor(os.path.join("check", "checker"))
    else:
        checker = DiffChecker()

    time_limiter = TimeLimitProvider(task_config)
    testing_context = TestingContext(checker, time_limiter, task_config)
    if os.path.isfile(os.path.join("check", "batchmanager")):
        testing_context.batchmanager_path = os.path.abspath(os.path.join("check", "batchmanager"))

    tracker = TestResultTracker()

    tests = list(itertools.chain.from_iterable([group.tests for group in genfile.groups]))
    descriptors = []
    for solution in solutions:
        try:
            descriptor = get_solution_descriptor(solution)
            descriptors.append(descriptor)
        except UnsupportedLanguageException:
            print(f"Unsupported language in solution {solution}")
            descriptor = SolutionDescriptor(solution, None, None)
            descriptors.append(descriptor)
            tracker.register_compile_time_fail(descriptor, TestResult(FailedVerdict.UnsupportedLanguage))
            continue

        test_solution(descriptor, testing_context, tests, tracker)

    result_table = create_table(tests, descriptors, tracker)

    scorer = get_scorer(task_config, genfile)
    subtask_table = create_subtask_table(tests, descriptors, scorer, tracker, genfile)

    print(tabulate(result_table, headers="firstrow", tablefmt="simple_grid"))
    print(tabulate(subtask_table, headers="firstrow", tablefmt="simple_grid"))
