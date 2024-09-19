import os.path
import subprocess

from etp.etp_exception import EtpException
from etp.print_utils import red_bold


def make_all_gen():
    if not os.path.isfile("gen/Makefile"):
        print("Nothing to make.")
        return

    exec_result = subprocess.run(["make", "all"], cwd="gen")
    if exec_result.returncode != 0:
        raise EtpException("'make all' in gen/ failed")


def make_all_check():
    if not os.path.isfile("check/Makefile"):
        print("Nothing to make")
        return

    exec_result = subprocess.run(["make", "all"], cwd="check")
    if exec_result.returncode != 0:
        raise EtpException("'make all' in check/ failed")