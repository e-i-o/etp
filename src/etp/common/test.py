from dataclasses import dataclass
from typing import Optional


@dataclass
class Test:
    index: int
    input_path: str
    output_path: str
    command_template: Optional[str] = None
    original_group_name: Optional[str] = None