import subprocess

from etp.common.replace_command_tokens import replace_command_tokens
from etp.common.solution_descriptor import SolutionDescriptor
from etp.print_utils import red_bold


def compile_solution(solution: SolutionDescriptor, executable_path: str):
    compile_command = replace_command_tokens(solution.language.compile_command, solution.path, executable_path)
    try:
        subprocess.run(compile_command, check=True, timeout=10)
    except Exception as e:
        print(red_bold("Compilation failed:"), e)
        raise e
