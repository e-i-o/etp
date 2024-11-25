import os.path
import resource
import shutil
import subprocess
from dataclasses import dataclass

from etp.common.replace_command_tokens import replace_command_tokens
from etp.common.solution_descriptor import SolutionDescriptor
from etp.common.test import Test
from etp.config.task_config import TaskConfig


@dataclass
class RunResult:
    returncode: int
    elapsed_time_ms: int
    output: bytes


def run_solution(task_config: TaskConfig, cwd: str,
                 solution: SolutionDescriptor, executable_path: str,  # relative to cwd
                 test: Test, timeout_ms: int = None,
                 batchmanager_path=None) -> RunResult:
    if task_config.infile:
        shutil.copyfile(test.input_path, os.path.join(cwd, task_config.infile))
        in_bytes = None
    else:
        with open(test.input_path, "rb") as in_stream:
            in_bytes = in_stream.read()

    execute_command = replace_command_tokens(solution.language.execute_command,
                                             solution.path, executable_path)
    if batchmanager_path is not None:
        execute_command = [batchmanager_path, task_config.infile, task_config.outfile] + execute_command

    usage_start = resource.getrusage(resource.RUSAGE_CHILDREN)
    try:
        print(f"Running {execute_command} on {test.input_path}...")
        exec_result = subprocess.run(execute_command,
                                     capture_output=True,
                                     input=in_bytes,
                                     cwd=cwd,
                                     timeout=None if timeout_ms is None else timeout_ms / 1000)
    except subprocess.TimeoutExpired:
        print("Hard timeout exceeded.")
        return RunResult(-1, timeout_ms, b"")

    usage_end = resource.getrusage(resource.RUSAGE_CHILDREN)
    elapsed_time_ms = int(1000 * (usage_end.ru_utime - usage_start.ru_utime))

    if task_config.outfile:
        with open(os.path.join(cwd, task_config.outfile), "rb") as out_stream:
            out_bytes = out_stream.read()
    else:
        out_bytes = exec_result.stdout

    print(f"Return code: {exec_result.returncode}, elapsed time: {elapsed_time_ms}")
    return RunResult(exec_result.returncode, elapsed_time_ms, out_bytes)