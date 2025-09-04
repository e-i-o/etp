from typing import List, Union

from tabulate import tabulate

from etp.config.genfile import Genfile
from etp.config.task_config import TaskConfig


def grey(s: str):
    return f"\x1B[0;90m{s}\x1B[0m"


def print_geninfo(task_config: TaskConfig, genfile: Genfile):
    table : List[List[str]] = []
    header = ["#", "CMS #", "Expanded command"]
    table.append(header)

    total_points = 0
    group_index = 0  # 1-based
    for group in genfile.groups:
        group_index += 1
        in_group_index = 0  # 1-based

        table.append(["", "", f"Subtask {group_index} ({group.points} points)  {group.parameters}"])
        total_points += group.points

        for test in group.tests:
            in_group_index += 1
            cmd = test.command_template
            cmd = cmd.replace("%i", test.input_path)
            cmd = cmd.replace("%o", test.output_path)

            row = [str(test.index), str(in_group_index), cmd]
            if test.index in group.shadow_tests:
                row = list(map(grey, row))
            table.append(row)

    print(tabulate(table, headers="firstrow", tablefmt="fancy_grid"))
    print(f"Total points: {total_points}")