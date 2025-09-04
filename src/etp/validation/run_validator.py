import subprocess

from etp.config.genfile import Genfile
from etp.config.make_all import make_all_gen
from etp.config.task_config import TaskConfig
from etp.print_utils import red_bold, yellow_bold


def validate_all(task_config: TaskConfig, genfile: Genfile) -> bool:
    if not task_config.validator:
        print(yellow_bold("No validator set, skipping test case validation..."))
        return True

    make_all_gen()

    # tests are validated with the name of the group they are originally in
    # problemsetters should ensure that conditions of a subtask imply the conditions of its dependencies
    is_ok = True
    for test in genfile.tests:
        print(f"Validating test {test.index}...")
        ok = validate_core(task_config.validator, test.input_path, test.original_group_name)
        if not ok:
            is_ok = False

    return is_ok


def validate_test_with_index(index: int, task_config: TaskConfig, genfile: Genfile) -> bool:
    if task_config.validator is None:
        print(yellow_bold("No validator set, nothing to validate."))
        return False

    make_all_gen()

    test = None
    for t in genfile.tests:
        if t.index == index:
            test = t

    if test is None:
        raise IndexError(f"no test with index {index}")

    return validate_core(task_config.validator, test.input_path, test.original_group_name)


def validate_test_in_file(input_path: str, task_config: TaskConfig) -> bool:
    if task_config.validator is None:
        print(yellow_bold("No validator set, nothing to validate."))
        return False

    make_all_gen()

    return validate_core(task_config.validator, input_path)


def validate_core(validator_path: str, input_path: str, group_name: str = None) -> bool:
    command = [validator_path]
    if group_name is not None and group_name != "":
        command.append("--group")
        command.append(group_name)

    with open(input_path, "r") as input_text:
        print(" ".join(command))
        exec_result = subprocess.run(command,
                                     text=True,
                                     capture_output=True,
                                     input=input_text.read())
        if exec_result.returncode != 0:
            print(red_bold("FAILED:"), exec_result.stderr)
            return False
        else:
            print(exec_result.stderr)
            return True
