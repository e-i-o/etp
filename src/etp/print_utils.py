def red_bold(s: str) -> str:
    return f"\x1B[1;31m{s}\x1B[0m"


def green_bold(s: str) -> str:
    return f"\x1B[1;32m{s}\x1B[0m"


def yellow_bold(s: str) -> str:
    return f"\x1B[1;33m{s}\x1B[0m"