# etp - tools for task preparation

**There is NO sandboxing! All solutions, generators, checkers etc. run with the 
same permissions as your user account. Don't run malicious solutions with these tools!**

## Usage:

`etp generate` generates the input tests and the correct outputs.  
`etp run` runs all solutions on all test cases.  
`etp run solution1.cpp solution2.cpp` to run solutions `solution1.cpp` and `solution2.cpp` on all test cases. 
The parameters `solution1.cpp` are, of course, relative to the current directory. If only one solution is specified,
the checker comments are also printed

## Installation

1. Install [pipx](https://pipx.pypa.io/latest/installation/)
2. Clone this repository
3. Navigate to the root directory
4. `pipx install .`

## Basic information

A task **must** contain the following two files:

- `/task.yaml`
- `/gen/GEN`

`/task.yaml` is a YAML configuration file. No fields are actually mandatory for 
the tools here. We make use of the following built-in CMS values: 

- `time_limit` -- time limit in seconds. 2 if absent.
- `time_limit_interpreted` -- time limit for interpreted languages in seconds. Equal to `time_limit` if abset.
- `infile` -- name of the input file. Standard input if empty or absent.
- `outfile` -- name of the output file. Standard output if empty or absent.
- `score_type` -- specifies the formula for calculating total score from subtask scores. We support the following:
`GroupSum`, `GroupSumCheck`, `GroupSumCond`, `GroupMin`, `GroupMul`. Other values (including `Sum`) are treated 
as if they were `GroupSum`.

Additionally, the following "custom" values are used.

- `dummy_outputs`: boolean. If set to true, empty output files are generated for all tests.
- `validator`: string. Path to executable file of the validator.
- `model_solution`: string. Path to the source code of the model solution.
- `solutions`: list. Paths to all solutions (wrong or correct).

All paths are relative to the task root directory (the one that contains `task.yaml`).

The number of test cases is as determined by `gen/GEN`. The `n_input` key in `task.yaml` is not considered **at all**.

Example `task.yaml` file:

```yaml
name: eki
title: Elukvaliteediindeks
time_limit: 1
time_limit_interpreted: 5
memory_limit: 256
n_input: 14
public_testcases: all
infile: ''
outfile: ''
score_type: GroupMin
score_mode: max

validator: bin/validator
model_solution: solution/sol.cpp
solutions:
 - solution/sol.cpp
 - solution/sol1.cpp
 - solution/sol2.cpp
 - solution/sol4.cpp
 - solution/sol.py
 - solution/sol_tahvend.py
```

There are two main commands: `etp generate` and `etp run`. These two are totally independent:
if you do not want to generate test cases using the tools here, you can still use `etp run`.
Both commands can be run from any subdirectory of the task. The tool will navigate up the tree
until it finds a directory containing `task.yaml`.

## Test generation and validation

`etp generate` consists of four phases. The `--skip-input`, `--skip-validation` and `--skip-output` 
flags can be used to skip the respective phases.

### Make

If the file `gen/Makefile` exists, `make` is run in `gen/`. You can put compilation
scripts for your generators and validators in there.

### Input generation

Inputs are generated by treating `gen/GEN` as a shell script. Example `gen/GEN` value:

```shell
# ST: 0
touch %i
# ST: 10
bin/geno -t=242 > %o; bin/genio < %o > %i  # generate output first, input from that
bin/geno -t=123 > %o; bin/genio < %o > %i
bin/genio < %o > %i  # in this case, output is manually generated; input from that
# ST: 15
bin/geni -a=2343 > %i  # more typical situation: input is generated here, output later
bin/geni -a=1 > %i
bin/geni5pp > %i
# ST: 15 
bin/geni -a=11 > %i
# ST: 20
bin/geni -a=1442 > %i
# ST: 40
bin/geni -a=141 > %i
bin/geni -a=1234 > %i
```

The tokens `%i` and `%o` are expanded to the file names of the input and output files for 
that particular test case. For example, the line `bin/geno -t=123 > %o; bin/genio < %o > %i` 
is expanded to
```shell
bin/geno -t=123 > output/output2.txt; bin/genio < output/output2.txt > input/input2.txt
```

The working directory in which `GEN` is run is the root directory of the task. **Generators must 
be relative to that directory.**

If your input files are generated another way (you don't want to put commands in `GEN` for some 
reason), put `touch %i` or `:` in every line of `GEN`.

### Input validation

A validator is a program that reads an input file from standard input and checks whether 
the input file satisfies all constraints in the task statement. If they are satisfied, the
validator exits with code 0, otherwise it exits with a nonzero exit code.

If `validator` is set in `task.yaml`, it is run for every input file described in `GEN`.
If not, this step is skipped. The working directory is the root directory of the task.

### Output generation

If `model_solution` is set in `task.yaml`, that solution file is used to generate the correct
output value for all test cases, except for test cases where `%o` is mentioned anywhere in
the `GEN` file (even in comments). The model solution receives a generous time limit of 10 
seconds for output generation.

If `dummy_outputs` was set in `task.yaml`, instead, all output files that do not yet exist 
are generated as empty files. Existing output files are not modified (as in `touch`).

### Deleting extra files in `input/` and `output/`

After test generation, if `input/` or `output/` contain files of the form `input%d.txt` or
`output%d.txt` with `%d` greater than or equal to the number of test cases listed in 
`GEN`, these files are moved to `.etp/trash/`. This behavior can be turned off with
the `--no-delete` flag, in which case no files are deleted or thrashed.

## Running solutions

`etp run` can be used to run all solutions on all test cases and see the results. Before 
running, each test case must have an input file and an output file (the number of test cases
is the number of non-comment lines in `GEN`).

If `check/Makefile` exists, then `make` is run in `check/`. You can put compilation scripts
for your checker or batchmanager there (if applicable).

Then, all solutions listed in `task.yaml` are run on all test cases. If `check/checker` exists,
that program is used to compare outputs. Otherwise, `diff -q --ignore-trailing-space --strip-trailing-cr` 
is used. After that, the toolset prints two tables: the results on each test and the results on 
each subtask.

Abbreviations used in the output table:
- CE: compilation error
- RE: runtime error
- TL: time limit exceeded
- ML: memory limit exceeded (not actually used)
- FL: judgement failed (checker crashed)
- UL: unsupported language

In other cases, a real number in 0...1 is printed. The `!` symbol after a verdict denotes that 
the output printed by the solution matches the correct output exactly.

### Programming languages

If the file `~/.etp/languages.json` exists, the compilation and execution commands for each language are
read from it. Example value:

```json
[
    {
        "extension": ".py",
        "compile_command": ["cp", "%s", "%e"],
        "execute_command": ["/bin/pypy3", "%e"],
        "is_interpreted": true
    },
    {
        "extension": ".cpp",
        "compile_command": ["g++", "-std=c++17", "-DONLINE_JUDGE", "-O2", "%s", "-o", "%e"],
        "execute_command": ["./%e"]
    }
]
```

Note that the commands are lists. If you modify the file, also write it in this format. Don't
use spaces to separate arguments. Be aware that batchmanagers only work with Python if the 
interpreter's path is absolute (`pypy3` being in PATH is not sufficient).