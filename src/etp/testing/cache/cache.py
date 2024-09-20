import os.path
import sqlite3
from pathlib import Path
from sqlite3 import Connection, Cursor
from typing import Optional, Tuple

from etp.testing.test_result import TestResult
from etp.testing.verdict import FailedVerdict


def get_cached_test_result(solution_path: str, test_index: int,
                           context_hash, solution_hash, io_hash) -> Optional[TestResult]:
    conn, cursor = open_cache_db()
    cursor.execute("SELECT * FROM runs WHERE test_index = ? AND solution_path = ?",
                   (test_index, solution_path,))
    result = cursor.fetchone()
    if result is None:
        conn.close()
        return None

    (cached_index, cached_solution_path,
     cached_context_hash, cached_solution_hash, cached_io_hash,
     verdict_type, verdict_value, time_milliseconds, exact_match, comment) = result
    if context_hash.hexdigest() != cached_context_hash or \
            solution_hash.hexdigest() != cached_solution_hash or \
            io_hash.hexdigest() != cached_io_hash:
        conn.close()
        return None  # stale copy in cache

    if verdict_type == 0:
        verdict = float(verdict_value)
    else:
        verdict = FailedVerdict(verdict_type)

    if time_milliseconds < 0:
        time_milliseconds = None

    if exact_match == 0:
        exact_match = False
    elif exact_match == 1:
        exact_match = True
    else:
        exact_match = None

    conn.close()
    return TestResult(verdict, time_milliseconds, exact_match, comment)


def cache_test_result(solution_path: str, test_index: int,
                      context_hash, solution_hash, io_hash, result: TestResult):
    if isinstance(result.verdict, FailedVerdict):
        verdict_type = result.verdict.value
        verdict_value = 0
    else:
        verdict_type = 0
        verdict_value = result.verdict

    if result.time_milliseconds is None:
        time_milliseconds = -1
    else:
        time_milliseconds = result.time_milliseconds

    if result.exact_match is None:
        exact_match = -1
    else:
        exact_match = int(result.exact_match)

    data = (test_index, solution_path,
            context_hash.hexdigest(), solution_hash.hexdigest(), io_hash.hexdigest(),
            verdict_type, verdict_value, time_milliseconds, exact_match, result.comment)

    conn, cursor = open_cache_db()
    cursor.execute("DELETE FROM runs WHERE test_index = ? and solution_path = ?", 
                   (test_index, solution_path))
    cursor.execute("INSERT INTO runs VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", data)
    conn.commit()
    conn.close()


def open_cache_db() -> Tuple[Connection, Cursor]:
    Path(".etp", "cache").mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(os.path.join(".etp", "cache", "cache.db"))
    cursor = conn.cursor()
    cursor.execute("""
CREATE TABLE IF NOT EXISTS runs(
    test_index INTEGER,
    solution_path TEXT,
    context_hash TEXT,
    solution_hash TEXT,
    io_hash TEXT,
    verdict_type INTEGER,
    verdict_value REAL,
    time_milliseconds INTEGER,
    exact_match INTEGER,
    comment TEXT
)""")
    cursor.execute("""
CREATE UNIQUE INDEX IF NOT EXISTS
ix_index_path ON runs (test_index, solution_path)
""")

    return conn, cursor
