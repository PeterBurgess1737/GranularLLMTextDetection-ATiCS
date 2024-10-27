import json
import pathlib
from typing import Literal

_set_names = Literal["fine-tuning", "evaluation"]


def load_working_set(set_name: _set_names) -> tuple[list[list[float]], list[bool]]:
    """
    :param set_name: Name of the working set to load, either "fine-tuning" or "evaluation".
    :return: A tuple containing two elements:
        - A list of lists of floats representing sentence evaluations.
        - A list of booleans indicating AI modification status for each sentence.
    """

    if set_name == "fine-tuning":
        set_dir = pathlib.Path("./data/working_set/fine_tuning_set")
    elif set_name == "evaluation":
        set_dir = pathlib.Path("./data/working_set/evaluation_set")
    else:
        raise ValueError(f"Unknown set name '{set_name}'")

    if not set_dir.exists():
        raise ValueError(f"Working set directory '{set_dir}' does not exist")

    sentence_evaluations: list[list[float]] = []
    sentence_realities: list[bool] = []

    for file in set_dir.iterdir():
        with file.open() as f:
            data = json.loads(f.read())

        sentence_evaluations.extend(data["sentence_evaluations"])
        sentence_realities.extend([bool(a) for a in data["ai_modified"]])

    return sentence_evaluations, sentence_realities
