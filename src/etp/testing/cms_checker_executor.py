import subprocess

from etp.print_utils import red_bold
from etp.testing.testing_context import CheckerExecutor
from etp.common.test import Test
from etp.testing.verdict import Verdict, FailedVerdict


class CmsCheckerExecutor(CheckerExecutor):
    def __init__(self, path):
        self.path = path

    def execute_checker(self, test: Test, output_path: str) -> [Verdict, str]:
        cmd = [self.path, test.input_path, test.output_path, output_path]
        exec_result = subprocess.run(cmd, text=True, capture_output=True)

        if exec_result.returncode != 0:
            print(red_bold("FAILED:"), f"checker returned non-zero exit code {exec_result.returncode}")
            return FailedVerdict.JudgementFailed, "checker returned non-zero exit code"

        try:
            fraction = float(exec_result.stdout)
        except ValueError:
            print(red_bold("FAILED:"), f"checker returned {exec_result.stdout} which is not a float")
            return FailedVerdict.JudgementFailed, f"checker returned {exec_result.stdout} which is not a float"

        return fraction, exec_result.stderr
