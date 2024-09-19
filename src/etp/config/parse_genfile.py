from typing import TextIO

from etp.config.genfile import Genfile, GenTestGroup
from etp.common.test import Test


def parse_genfile(genfile: TextIO) -> Genfile:
    parsed = Genfile()
    lines = genfile.readlines()

    last_was_group_start = False
    cur_index = 0
    for line in lines:
        line = line.strip()
        if len(line) == 0:
            continue

        is_group_start = False
        if line.startswith("#"):
            if line.startswith("# ST:"):
                tokens = line[1:].split()
                points = int(tokens[1].strip())
                parameters = list(map(lambda s: s.strip(), tokens[2:]))
                group = GenTestGroup(points, parameters=parameters)
                parsed.groups.append(group)
                is_group_start = True
            elif last_was_group_start:
                # name of the test group
                name = line[1:].strip().replace(" ", "-")
                parsed.groups[-1].name = name
            # otherwise, it is a true comment and should be ignored
        else:
            parsed.groups[-1].tests.append(Test(
                index=cur_index,
                input_path=f"input/input{cur_index}.txt",
                output_path=f"output/output{cur_index}.txt",
                command_template=line
            ))
            cur_index += 1

        last_was_group_start = is_group_start

    return parsed
