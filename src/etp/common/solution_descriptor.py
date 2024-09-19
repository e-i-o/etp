import os.path
from dataclasses import dataclass

from etp.common.solution_language import SolutionLanguage, get_supported_solution_languages
from etp.etp_exception import EtpException, UnsupportedLanguageException


@dataclass
class SolutionDescriptor:
    path: str
    name: str
    language: SolutionLanguage


def get_solution_descriptor(path: str) -> SolutionDescriptor:
    source_name = os.path.basename(path)
    name, ext = os.path.splitext(source_name)

    supported_languages = get_supported_solution_languages()
    if ext in supported_languages:
        return SolutionDescriptor(path, name, supported_languages[ext])
    else:
        raise UnsupportedLanguageException(f"No known run/execute command for {ext}")