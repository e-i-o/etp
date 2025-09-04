import subprocess
from pathlib import Path

from etp.config.genfile import Genfile
from etp.config.make_all import make_all_gen
from etp.etp_exception import EtpException


def generate_inputs(genfile: Genfile):
    make_all_gen()

    Path("input/").mkdir(parents=True, exist_ok=True)
    Path("output/").mkdir(parents=True, exist_ok=True)

    print("Generating inputs...")
    for test in genfile.tests:
        cmd = test.command_template
        cmd = cmd.replace("%i", test.input_path)
        cmd = cmd.replace("%o", test.output_path)

        if test.command_template.isdigit():
            print(f"Command template for {test.input_path} is just a digit, skipping...")
            continue

        print(cmd)
        try:
            subprocess.run([cmd], shell=True, check=True)
        except subprocess.CalledProcessError:
            raise EtpException("generator raised error, terminating...")
