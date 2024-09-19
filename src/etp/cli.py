import argparse
import os.path

import yaml

from etp.config.genfile import Genfile
from etp.config.parse_genfile import parse_genfile
from etp.config.task_config import TaskConfig
from etp.etp_exception import EtpException
from etp.generation.generate_inputs import generate_inputs
from etp.generation.generate_outputs import generate_outputs
from etp.print_utils import red_bold, green_bold, yellow_bold
from etp.testing.test_solutions import test_solutions
from etp.validation.run_validator import validate_all


def move_to_root_dir():
    while not os.path.isfile("task.yaml"):
        print(f"task.yaml not found in {os.getcwd()}, moving up...")
        try:
            olddir = os.getcwd()
            os.chdir("..")
            newdir = os.getcwd()

            if olddir == newdir:  # root
                raise EtpException("Could not find task root directory. Are you sure the task has a task.yaml file?")
        except OSError:
            raise EtpException("Could not find task root directory. Are you sure the task has a task.yaml file?")
    print(f"using {os.getcwd()} as task root directory")


def get_genfile() -> Genfile:
    with open("gen/GEN", "r") as f:
        return parse_genfile(f)


def get_task_config() -> TaskConfig:
    with open("task.yaml", "r") as f:
        return TaskConfig(**yaml.safe_load(f))


def generate(args):
    move_to_root_dir()
    genfile = get_genfile()
    task_config = get_task_config()

    if args.skip_input:
        print(yellow_bold("Skipping input generation."))
    else:
        generate_inputs(genfile)
        print(green_bold("Input generation complete."))

    if args.skip_validation:
        print(yellow_bold("Skipping input validation."))
    else:
        ok = validate_all(task_config, genfile)
        if not ok:
            return
        print(green_bold("Validation complete."))

    if args.skip_output:
        print(yellow_bold("Skipping output generation."))
    else:
        generate_outputs(task_config, genfile)

    gen_n_input = sum([len(group.tests) for group in genfile.groups])
    yaml_n_input = task_config.n_input
    if yaml_n_input is None:
        print(yellow_bold("WARN:"), f"n_input is not set in task.yaml, should be {gen_n_input}")
    elif yaml_n_input != gen_n_input:
        print(yellow_bold("WARN:"), f"n_input in task.yaml ({yaml_n_input}) doesn't match GEN, should be {gen_n_input}")
    else:
        print("n_input in GEN and task.yaml match.")


def validate(_):
    raise NotImplementedError()


def run(args):
    if args.solution:
        # store the absolute path of every solution
        args.solution = [os.path.abspath(sol) for sol in args.solution]

    move_to_root_dir()

    # and now back to relative paths again...
    if args.solution:
        args.solution = [os.path.relpath(sol) for sol in args.solution]

    genfile = get_genfile()
    task_config = get_task_config()

    if not args.solution and not task_config.solutions:
        print(red_bold("No solutions. Nothing to run"))
        return

    # TODO: correct relativizing of paths
    if args.solution:
        solutions = args.solution
    else:
        solutions = task_config.solutions

    test_solutions(task_config, genfile, solutions)


def main():
    parser = argparse.ArgumentParser(prog="etp")
    subparsers = parser.add_subparsers(required=True)

    validate_parser = subparsers.add_parser("validate", 
                                            help="validates that input files have the correct format")
    validate_parser.set_defaults(func=validate)
    validate_parser.add_argument("file", help="If specified, either the index of the test case "
                                              "or a path to an input file. If not specified, all input files "
                                              "will be validated.")

    generate_parser = subparsers.add_parser("generate",
                                            help="generates input and/or output files")
    generate_parser.add_argument("--skip-input", action="count", default=0, 
                                 help="If present, then input generation is skipped. Note that the other steps "
                                      "still expect an input file for each test.")
    generate_parser.add_argument("--skip-validation", action="count", default=0, 
                                 help="If present, then input validation is skipped.")
    generate_parser.add_argument("--skip-output", action="count", default=0,
                                 help="If present, then output generation is skipped.")
    generate_parser.set_defaults(func=generate)

    run_parser = subparsers.add_parser("run",
                                       help="runs the solutions")
    run_parser.add_argument("solution", nargs="*", help="The path of the solution to run. Any number of "
                                                        "solutions can be specified. If none are specified, all "
                                                        "solutions in task.yaml are run.")
    run_parser.set_defaults(func=run)

    args = parser.parse_args()

    try:
        args.func(args)
    except EtpException as ex:
        print(red_bold("FAILED:"), ex)


if __name__ == "__main__":
    main()
