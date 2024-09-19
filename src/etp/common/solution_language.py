import json
import os.path
from dataclasses import dataclass
from typing import Dict, List


@dataclass
class SolutionLanguage:
    extension: str
    compile_command: List[str]
    execute_command: List[str]
    is_interpreted: bool = False


def get_supported_solution_languages() -> Dict[str, SolutionLanguage]:
    config_file = os.path.expanduser("~/.etp/languages.json")
    if os.path.exists(config_file):
        with open(config_file) as json_stream:
            langs = json.load(json_stream)

        lang_dict = {}
        for lang in langs:
            lang_dict[lang["extension"]] = SolutionLanguage(**lang)
        return lang_dict

    return {
        ".py": SolutionLanguage(".py", ["cp", "%s", "%e"], ["pypy3", "%e"], True),
        ".cpp": SolutionLanguage(".cpp", ["g++", "-std=c++17", "-DONLINE_JUDGE", "-O2", "%s", "-o", "%e"], ["./%e"]),
        ".c": SolutionLanguage(".c", ["gcc", "-DONLINE_JUDGE", "-O2", "%s", "-o", "%e"], ["./%e"])
    }
