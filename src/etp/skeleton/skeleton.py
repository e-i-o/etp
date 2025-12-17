from pathlib import Path

def generate_skeleton():
    task_name = input("Enter task name: ")
    with open("task.yaml", "w") as yaml_file:
        yaml_file.write(f"""\
name: {task_name}
title: {task_name}
time_limit: 1
time_limit_interpreted: 3
memory_limit: 256
public_testcases: all
infile: ''
outfile: ''
score_type: GroupMin
# also supported: GroupSum, GroupSumCond
score_mode: max_subtask
# score_precision: 2

# for output-only problems:
# output_only: True
# relative_scoring: True

# validator: gen/validator
# model_solution: solution/model_solution.cpp
# solutions:
# - solution/model_solution.cpp
# - solution/other_solution.cpp
""")

    Path("gen/").mkdir(parents=True, exist_ok=True)
    with open("gen/GEN", "w") as gen_file:
        gen_file.write("""\
## subtasks are defined like this (delete the first '#'):
## ST: 100 name:foo deps:bar,baz
## the subtask is named 'foo' and depends on subtasks named 'bar' and 'baz'
## this means that all tests of 'bar' and 'baz' are non-transitively "copied" to 'foo'

## tests are defined like this:
##   gen/generator -some=parameter -other=parameter > %i
## the %i token is expanded to `input/input<test id>.txt`
## you can also generate input from output, like so:
##   gen/generator -something < %o > %i
## each test corresponds to exactly one non-comment line, so if you need to run
## multiple scripts, put them on the same line and separate them with a semicolon:
##   gen/gen_output [params] > %o ; gen/gen_input [params] < %o > %i

# ST: 100
""")

    with open("gen/Makefile.sample", "w") as makefile_sample:
        makefile_sample.write("""\
CXXFLAGS+=-O2

all: validator some_generator other_generator
""")

    Path("solution/").mkdir(parents=True, exist_ok=True)
    Path("input/").mkdir(parents=True, exist_ok=True)
    Path("output/").mkdir(parents=True, exist_ok=True)
    Path("check/").mkdir(parents=True, exist_ok=True)
    Path("statement/").mkdir(parents=True, exist_ok=True)