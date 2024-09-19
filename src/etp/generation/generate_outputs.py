import os.path
from pathlib import Path

from etp.common.compile import compile_solution
from etp.common.run import run_solution
from etp.common.solution_descriptor import get_solution_descriptor
from etp.config.genfile import Genfile
from etp.config.task_config import TaskConfig
from etp.print_utils import yellow_bold, red_bold


def generate_outputs(task_config: TaskConfig, genfile: Genfile):
    if task_config.model_solution is None:
        print(yellow_bold("No model solution set, skipping output generation..."))
        return

    Path("input/").mkdir(parents=True, exist_ok=True)
    Path("output/").mkdir(parents=True, exist_ok=True)
    Path(".etp/working").mkdir(parents=True, exist_ok=True)

    # TODO: we may need a flag for dummy output files or similar?
    # That is, what to do with output-only and interactive files is not clear
    # (If output files are "hints" or generated alongside input files, that's handled:
    # this script will not run the model solution on GEN lines that contain %o)

    descriptor = get_solution_descriptor(task_config.model_solution)
    compile_solution(descriptor, os.path.join(".etp", "working", descriptor.name))

    for group in genfile.groups:
        for test in group.tests:
            cmd = test.command_template
            if "%o" in cmd:
                print(f"Skipping generation of {test.output_path} as there is an '%o' token in the script line")
                continue

            print(f"Generating {test.output_path}...")
            result = run_solution(task_config, os.path.join(".etp", "working"), descriptor, 
                                  descriptor.name, test, 10_000)

            if result.returncode != 0:
                print(red_bold("FAILED:"), f"model solution got timeout or a runtime error "
                                           f"on test {test.input_path} (return code: {result.returncode}, "
                                           f"elapsed time: {result.elapsed_time_ms})")
                continue

            with open(test.output_path, "wb") as out_file:
                out_file.write(result.output)