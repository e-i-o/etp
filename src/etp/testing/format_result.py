from etp.testing.test_result import TestResult
from etp.testing.verdict import FailedVerdict


def format_result(result: TestResult) -> str:
    abbrevs = {
        FailedVerdict.CompilationError: "CE",
        FailedVerdict.RuntimeError: "RE",
        FailedVerdict.TimeLimitExceeded: "TL",
        FailedVerdict.MemoryLimitExceeded: "ML",
        FailedVerdict.JudgementFailed: "FL",
        FailedVerdict.UnsupportedLanguage: "UL",
        FailedVerdict.HardTimeLimitExceeded: "TL"
    }

    ret = ""

    # color
    if isinstance(result.verdict, FailedVerdict):
        if result.verdict == FailedVerdict.JudgementFailed or \
                result.verdict == FailedVerdict.UnsupportedLanguage:
            ret += "\x1B[1;35m"  # bold magenta
        else:
            ret += "\x1B[0;31m"  # normal red
    else:
        if result.verdict <= 0.0:
            ret += "\x1B[0;31m"  # normal red
        elif result.verdict >= 1.0:
            ret += "\x1B[0;32m"  # normal green
        else:
            ret += "\x1B[0;33m"  # normal yellow

    # verdict
    if isinstance(result.verdict, FailedVerdict):
        ret += abbrevs[result.verdict]
    else:
        ret += f"{result.verdict:.3f}"

    if result.verdict == FailedVerdict.TimeLimitExceeded:
        if result.original_score >= 1:
            ret += "?"
        else:
            ret += "#"

    # exact match
    if result.exact_match:
        ret += "!"

    while len(ret) < 15:
        ret += " "

    # turn color off
    ret += "\x1B[0m"
    if result.verdict == FailedVerdict.HardTimeLimitExceeded:
        ret += ">"
    ret += f"{result.time_milliseconds} ms"
    return ret


def format_subtask_result(subtask) -> str:
    max_score = subtask["max_score"]
    score = subtask["score_fraction"] * max_score

    ret = ""
    if score >= max_score:
        ret += "\x1B[0;32m"  # normal green
    elif score <= 0:
        ret += "\x1B[0;31m"  # normal red
    else:
        ret += "\x1B[0;33m"  # normal yellow

    ret += f"{score:.3f}"

    if "score_ignore" in subtask and subtask["score_ignore"]:
        ret += "*"

    ret += "\x1B[0m"
    return ret


def format_total_result(score: float, max_score: float) -> str:
    ret = ""
    if score <= 0:
        ret += "\x1B[1;31m"  # bold red
    elif score >= max_score:
        ret += "\x1B[1;32m"  # bold green
    else:
        ret += "\x1B[1;33m"  # bold yellow

    ret += f"{score:.3f}"
    ret += "\x1B[0m"
    return ret
