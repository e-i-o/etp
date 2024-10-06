import itertools
import os.path
from typing import List, Tuple, Any, Union

from tabulate import tabulate, SEPARATING_LINE

from etp.common.solution_descriptor import get_solution_descriptor, SolutionDescriptor
from etp.common.test import Test
from etp.config.genfile import Genfile
from etp.config.make_all import make_all_check
from etp.config.task_config import TaskConfig
from etp.etp_exception import UnsupportedLanguageException
from etp.print_utils import yellow_bold
from etp.testing.cache.hashing import hash_string, hash_file
from etp.testing.cms_checker_executor import CmsCheckerExecutor
from etp.testing.format_result import format_result, format_subtask_result, format_total_result
from etp.testing.scoretypes.GroupMin import GroupMin
from etp.testing.scoretypes.GroupMinDeps import GroupMinDeps
from etp.testing.scoretypes.GroupMul import GroupMul
from etp.testing.scoretypes.GroupSum import GroupSum
from etp.testing.scoretypes.GroupSumCheck import GroupSumCheck
from etp.testing.scoretypes.GroupSumCond import GroupSumCond
from etp.testing.scoretypes.ScoreType import ScoreType
from etp.testing.scoretypes.adapters import Evaluation, SubmissionResult
from etp.common.tabulate_hack import monkey_patch_tabulate
from etp.testing.test_result import TestResult
from etp.testing.test_result_tracker import TestResultTracker
from etp.testing.test_solution import test_solution
from etp.testing.testing_context import DiffChecker, TimeLimitProvider, TestingContext
from etp.testing.verdict import FailedVerdict, get_value


def create_table(genfile: Genfile, solutions: List[SolutionDescriptor],
                 tracker: TestResultTracker) -> List[Union[str, List[str]]]:
    table : List[Union[str, List[str]]] = []

    first_row = [""] * (1 + len(solutions))
    for j, solution in enumerate(solutions):
        first_row[j + 1] = os.path.basename(solution.path)
    if len(solutions) == 1:
        first_row.append("Comment")
    table.append(first_row)

    for group in genfile.groups:
        for test in group.tests:
            row = [""] * (1 + len(solutions))
            row[0] = str(test.index)

            result = None
            for j, solution in enumerate(solutions):
                result = tracker.get_result(solution, test)
                row[j + 1] = format_result(result)
            if len(solutions) == 1:
                row.append(result.comment)
            table.append(row)
        table.append(SEPARATING_LINE)

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
    elif task_config.score_type == "GroupMinDeps":
        return GroupMinDeps(genfile)
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
                         scorer: ScoreType, tracker: TestResultTracker, genfile: Genfile) -> List[Union[str, List[str]]]:
    scores = {}
    for solution in solutions:
        scores[solution.path] = calculate_score(tests, solution, tracker, scorer)

    table : List[Union[str, List[str]]] = [[""] * (1 + len(solutions)) for _ in range(2 + len(genfile.groups))]

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

    table.insert(-1, SEPARATING_LINE)

    return table


def test_solutions(task_config: TaskConfig, genfile: Genfile, solutions: List[str], use_cache: bool = False):
    # context_hash should contain everything "global" that can change how solutions are tested:
    # this includes:
    # - infile, outfile, time_limit, time_limit_interpreted
    # - checker if exists
    # - batchmanager if exists
    context_hash = hash_string(f"infile: {task_config.infile}, "
                               f"outfile: {task_config.outfile}, "
                               f"time_limit: {task_config.time_limit}, "
                               f"time_limit_interpreted: {task_config.time_limit_interpreted}")

    make_all_check()
    if os.path.isfile(os.path.join("check", "checker")):
        checker = CmsCheckerExecutor(os.path.join("check", "checker"))
        context_hash = hash_file(os.path.join("check", "checker"), context_hash)
    else:
        checker = DiffChecker()

    batchmanager_path = None
    if os.path.isfile(os.path.join("check", "batchmanager")):
        batchmanager_path = os.path.abspath(os.path.join("check", "batchmanager"))
        context_hash = hash_file(os.path.join("check", "batchmanager"), context_hash)

    time_limiter = TimeLimitProvider(task_config)
    testing_context = TestingContext(checker, time_limiter, task_config, context_hash, 
                                     use_cache=use_cache, batchmanager_path=batchmanager_path)

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

    result_table = create_table(genfile, descriptors, tracker)

    scorer = get_scorer(task_config, genfile)
    subtask_table = create_subtask_table(tests, descriptors, scorer, tracker, genfile)

    monkey_patch_tabulate()
    print(tabulate(result_table, headers="firstrow", tablefmt="fancy_grid"))
    print(tabulate(subtask_table, headers="firstrow", tablefmt="fancy_grid"))
