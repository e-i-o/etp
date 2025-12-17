import argparse
import os.path
import sys
from email.policy import default

import yaml

from etp.common.geninfo import print_geninfo
from etp.config.genfile import Genfile
from etp.config.parse_genfile import parse_genfile
from etp.config.task_config import TaskConfig
from etp.etp_exception import EtpException
from etp.generation.delete_extra import delete_extra_files, delete_extra_input_output
from etp.generation.generate_inputs import generate_inputs
from etp.generation.generate_outputs import generate_outputs
from etp.print_utils import red_bold, green_bold, yellow_bold
from etp.skeleton.skeleton import generate_skeleton
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
    if not os.path.isfile("gen/GEN"):
        raise EtpException("No gen/GEN file found.")

    with open("gen/GEN", "r") as f:
        return parse_genfile(f)


def get_task_config() -> TaskConfig:
    with open("task.yaml", "r") as f:
        conf = yaml.safe_load(f)
        if conf is None:
            return TaskConfig()
        else:
            return TaskConfig(**conf)


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
            print(red_bold("FAILED:"), "there were errors during validation. Terminating.")
            return
        print(green_bold("Validation complete."))

    if args.skip_output:
        print(yellow_bold("Skipping output generation."))
    else:
        ok = generate_outputs(task_config, genfile, bool(args.no_timeout))
        if not ok:
            print(red_bold("FAILED:"), "there were errors during output generation. Terminating.")
            return

    if not args.no_delete:
        delete_extra_input_output(genfile)

    gen_n_input = len(genfile.tests)
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

    if args.solution:
        solutions = args.solution
    else:
        solutions = task_config.solutions

    test_solutions(task_config, genfile, solutions, args.use_cache)


def geninfo(_):
    move_to_root_dir()
    genfile = get_genfile()
    task_config = get_task_config()

    print_geninfo(task_config, genfile)


def init(_):
    generate_skeleton()


def main():
    parser = argparse.ArgumentParser(prog="etp")
    subparsers = parser.add_subparsers(required=True)

    # TODO: uncomment when validate is implemented
    """
    validate_parser = subparsers.add_parser("validate", 
                                            help="validates that input files have the correct format")
    validate_parser.set_defaults(func=validate)
    validate_parser.add_argument("file", help="If specified, either the index of the test case "
                                              "or a path to an input file. If not specified, all input files "
                                              "will be validated.")
    """

    generate_parser = subparsers.add_parser("generate",
                                            help="generates input and/or output files")
    generate_parser.add_argument("--skip-input", action="count", default=0, 
                                 help="If present, then input generation is skipped. Note that the other steps "
                                      "still expect an input file for each test.")
    generate_parser.add_argument("--skip-validation", action="count", default=0, 
                                 help="If present, then input validation is skipped.")
    generate_parser.add_argument("--skip-output", action="count", default=0,
                                 help="If present, then output generation is skipped.")
    generate_parser.add_argument("--no-timeout", action="count", default=0,
                                 help="If present, no timeout is applied on output file generation.")
    generate_parser.add_argument("--no-delete", action="count", default=0,
                                 help="If present, extra files in input/ and output/ directories are not deleted")
    generate_parser.set_defaults(func=generate)

    run_parser = subparsers.add_parser("run",
                                       help="runs the solutions")
    run_parser.add_argument("solution", nargs="*", help="The path of the solution to run. Any number of "
                                                        "solutions can be specified. If none are specified, all "
                                                        "solutions in task.yaml are run.")
    run_parser.add_argument("-c", "--use-cache", action="count", default=0,
                            help="If present, then verdicts which 'should not have changed' "
                                 "are read from a cache.")
    run_parser.set_defaults(func=run)

    geninfo_parser = subparsers.add_parser("geninfo",
                                           help="prints an annotated table of GEN")
    geninfo_parser.set_defaults(func=geninfo)

    init_parser = subparsers.add_parser("init",
                                        help="generates default task.yaml and some other samples")
    init_parser.set_defaults(func=init)

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)
    args = parser.parse_args()

    try:
        args.func(args)
    except EtpException as ex:
        print(red_bold("FAILED:"), ex)


if __name__ == "__main__":
    main()
