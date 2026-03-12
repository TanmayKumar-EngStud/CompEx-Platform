import random
from collections import deque
from typing import List, Dict, Any

from db_artilaries import artilaries

_DIST: Dict[str, Dict[str, Dict[int, Dict[str, float]]]] = {}

async def initialize_difficulty_pool():
    """Fetches difficulty distribution from DB and populates _DIST."""
    global _DIST
    # Get raw data from DB config
    raw_dist = await artilaries.get_config('difficulty_distribution')
    if not raw_dist:
        raise ValueError("Could not load 'difficulty_distribution' from Artilaries DB.")
    
    # Process raw dictionary (it matches the structure provided in the prompt)
    # raw_dist is { "GRE": [ ... ], "GMAT": [ ... ] }
    for exam_name, exam_list in raw_dist.items():
        for section_blob in exam_list:
            sec_name = section_blob["name"]
            _DIST.setdefault(exam_name, {})
            
            # The structure is: { "name": "Quants", "Quants": { "1": {...} } }
            # So we access section_blob[sec_name]
            if sec_name in section_blob:
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
    if not _DIST:
        raise RuntimeError("Difficulty pool not initialized. Call initialize_difficulty_pool() first.")
        
    # Safety checks
    if exam not in _DIST:
        print(f"Warning: Exam '{exam}' not found in difficulty distribution. Using default/fallback.")
        # Return a simple balanced pool if exam not found
        return deque([3] * n_items)
        
    if section not in _DIST[exam]:
         print(f"Warning: Section '{section}' not found in difficulty distribution for '{exam}'. Using default/fallback.")
         return deque([3] * n_items)

    ratio = _DIST[exam][section].get(mock_level)
    if not ratio:
         # Fallback distribution
         ratio = {"easy": 0.33, "medium": 0.33, "hard": 0.34}

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
