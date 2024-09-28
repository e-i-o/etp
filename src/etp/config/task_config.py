from dataclasses import dataclass, fields
from typing import List


@dataclass
class TaskConfig:
    # cms fields
    name: str = None
    title: str = None
    time_limit: float = None
    time_limit_interpreted: float = None
    memory_limit: int = None
    n_input: int = None
    infile: str = None
    outfile: str = None
    score_type: str = None

    # extra etp fields
    dummy_outputs: bool = False
    validator: str = None
    model_solution: str = None
    solutions: List[str] = None

    def __init__(self, **kwargs):
        if kwargs is not None:
            names = set([f.name for f in fields(self)])
            for k, v in kwargs.items():
                if k in names:
                    setattr(self, k, v)
