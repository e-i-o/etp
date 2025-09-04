from typing import TextIO, List, Dict

from etp.config.genfile import Genfile, GenTestGroup
from etp.common.test import Test
from etp.print_utils import yellow_bold


def parse_known_parameters(params: List[str]) -> Dict:
    parsed = {}
    for kv in params:
        if ":" not in kv:
            continue

        key, value = kv.split(":", 1)
        if key == "deps":
            parsed[key] = value.split(",")
        else:
            parsed[key] = value

    return parsed


def parse_genfile(genfile: TextIO) -> Genfile:
    parsed = Genfile()
    lines = genfile.readlines()

    cur_index = 0
    for line in lines:
        line = line.strip()
        if len(line) == 0:
            continue

        if line.startswith("#"):
            if line.startswith("# ST:"):
                tokens = line[1:].split()
                points = int(tokens[1].strip())
                parameters = list(map(lambda s: s.strip(), tokens[2:]))
                named_parameters = parse_known_parameters(parameters)
                group = GenTestGroup(points, parameters=parameters, named_parameters=named_parameters)
                parsed.groups.append(group)
            # otherwise, it is a true comment and should be ignored
        else:
            test = Test(
                index=cur_index,
                input_path=f"input/input{cur_index}.txt",
                output_path=f"output/output{cur_index}.txt",
                command_template=line,
                original_group_name=parsed.groups[-1].name
            )
            parsed.groups[-1].tests.append(test)
            parsed.tests.append(test)
            cur_index += 1

    # resolve dependency list
    original_test_lists_by_name = {}
    for group in parsed.groups:
        if group.name is not None:
            original_test_lists_by_name[group.name] = group.tests.copy()

    for group in parsed.groups:
        for dep in group.deps:
            if dep not in original_test_lists_by_name:
                print(yellow_bold("WARN:"), f"group {group.name} refers to non-existent dependency {dep}")
                continue

            for test in original_test_lists_by_name[dep]:
                group.tests.append(test)
                group.shadow_tests.add(test.index)

        group.tests.sort(key=lambda t: t.index)

    return parsed
