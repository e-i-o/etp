import os
import shutil
from pathlib import Path

from etp.config.genfile import Genfile
from etp.print_utils import yellow_bold


def delete_extra_input_output(genfile: Genfile):
    Path("input/").mkdir(parents=True, exist_ok=True)
    Path("output/").mkdir(parents=True, exist_ok=True)
    Path(".etp/trash/").mkdir(parents=True, exist_ok=True)

    n_input = sum(len(group.tests) for group in genfile.groups)
    delete_extra_files("input", "input", ".txt", n_input)
    delete_extra_files("output", "output", ".txt", n_input)


def delete_extra_files(directory: str, prefix: str, suffix: str, n_input: int):
    for filename in os.listdir(directory):
        test_index = filename

        if not test_index.startswith(prefix):
            continue  # something else, ignore
        test_index = test_index[len(prefix):]

        if not test_index.endswith(suffix):
            continue  # something else, ignore
        test_index = test_index[:-len(suffix)]

        if not test_index.isdigit():
            continue
        if test_index[0] == "0" and test_index != "0":
            continue

        # now we know that test_index is a non-negative integer with no leading zeros
        test_index_int = int(test_index)
        if test_index_int >= n_input:
            print(yellow_bold("WARN:"), f"extra file {filename} in {directory}, moving to trash")
            shutil.move(os.path.join(directory, filename), os.path.join(".etp", "trash", filename))
            print("It is now available at .etp/trash/")