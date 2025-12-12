import random
from collections import deque
from typing import List, Dict

from io_utils import get_json

_RAW_DIST = get_json('difficulty_distribution')[0]


_DIST: Dict[str, Dict[str, Dict[int, Dict[str, float]]]] = {}
# exam_name could be "GRE", "GMAT", ...
for exam_name, exam_list in _RAW_DIST.items():
    # each {"name":"Quants","Quants":{ ... }}
    for section_blob in exam_list:
        sec_name = section_blob["name"]
        _DIST.setdefault(exam_name, {})
        _DIST[exam_name][sec_name] = {
            int(lvl): ratios
            for lvl, ratios in section_blob[sec_name].items()
        }


def _split_counts(total: int, ratio: Dict[str, float]) -> List[int]:
    """Return [#easy, #medium, #hard] adding up to total."""
    easy = int(total * ratio["easy"])
    medium = int(total * ratio["medium"])
    hard = total - easy - medium
    return [easy, medium, hard]


def get_difficulty_pool(exam: str,
                        section: str,
                        n_items: int,
                        mock_level: int = 3) -> deque[int]:
    """
    Return a shuffled list of length n_items whose values are in {1..5}
    and whose distribution matches the global table for (exam, section, level).
    1 = easiest, 5 = hardest.

    Args:

        exam:
            name of the exam from the exam_definition.json file
        section:
            name of the section of that exam from exam_definition.json file
        mock_level:
            to set mock difficulty
        n_items:
            number of questions (to tell how big the pool is)
    """
    ratio = _DIST[exam][section][mock_level]
    easy, medium, hard = _split_counts(n_items, ratio)
    counts = {
        1: easy,
        2: 0,
        3: medium,
        4: 0,
        5: hard
    }

    one = random.randint(0, counts[1])
    three = random.randint(0, counts[3])
    five = random.randint(0, counts[5])
    two_three = random.randint(0, counts[3] - three)
    two = counts[1] - one + two_three
    four = counts[5] - five + counts[3] - three - two_three
    pool = (
        [1] * one +
        [2] * two +
        [3] * three +
        [4] * four +
        [5] * five
    )
    random.shuffle(pool)
    return deque(pool)
