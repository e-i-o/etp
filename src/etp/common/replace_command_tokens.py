from typing import List


def replace_command_token(token: str, source_path: str, executable_path: str) -> str:
    return token.replace("%s", source_path).replace("%e", executable_path)


def replace_command_tokens(command: List[str], source_path: str, executable_path: str) -> List[str]:
    return list(map(lambda token: replace_command_token(token, source_path, executable_path), command))
