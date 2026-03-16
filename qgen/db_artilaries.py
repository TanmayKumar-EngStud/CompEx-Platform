"""
db_artilaries.py — JSON-backed config store (replaces the artilaries Postgres DB).

All data is read from flat JSON files inside json_files/.
The public async API is kept identical to the old Prisma-based implementation so
that prepare_prompts.py, difficulty_pool.py, question_manager.py and main.py
need zero changes.
"""

import json
import random
from pathlib import Path
from typing import Any, Dict, List, Optional

_JSON_DIR = Path(__file__).parent / "json_files"


class ArtilariesDB:
    """
    Singleton that serves config data from local JSON files.

    Async methods are preserved for API compatibility — they are simply
    synchronous reads wrapped in coroutines (no actual I/O awaiting needed).
    """

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._cache = {}
        return cls._instance

    # ------------------------------------------------------------------
    #  Internal helpers
    # ------------------------------------------------------------------

    def _load(self, key: str) -> Any:
        """Load and cache a JSON file by its base name (no extension)."""
        if key not in self._cache:
            path = _JSON_DIR / f"{key}.json"
            try:
                with open(path, "r", encoding="utf-8") as fh:
                    self._cache[key] = json.load(fh)
            except FileNotFoundError:
                print(f"\033[1;33mWarning:\033[0m json_files/{key}.json not found.")
                self._cache[key] = None
            except json.JSONDecodeError as exc:
                print(f"\033[1;31mError:\033[0m Invalid JSON in {key}.json: {exc}")
                self._cache[key] = None
        return self._cache[key]

    # ------------------------------------------------------------------
    #  Lifecycle (no-ops — kept for API compatibility)
    # ------------------------------------------------------------------

    async def connect(self) -> None:
        pass

    async def disconnect(self) -> None:
        pass

    # ------------------------------------------------------------------
    #  Public API
    # ------------------------------------------------------------------

    async def get_exam_definition(self) -> Dict[str, Any]:
        """Return the exam structure (exam_definition.json)."""
        return self._load("exam_definition") or {}

    async def get_question_type_info(self) -> Dict[str, Any]:
        """Return per-question-type metadata (question_type_info.json)."""
        return self._load("question_type_info") or {}

    async def get_prompt_components_for_type(self, question_type: str) -> Dict[str, Any]:
        """
        Return prompt_component_info entries filtered for the given question_type.
        Structure mirrors the old Prisma implementation so callers are unaffected.
        """
        data = self._load("prompt_component_info") or {}
        result = {}
        for comp_name, entries in data.items():
            if not isinstance(entries, list):
                # Skip scalar/dict keys like complexity_guidelines, graphTypes, etc.
                continue
            filtered = [
                e for e in entries
                if isinstance(e, dict)
                and "QuestionType" in e
                and question_type in e["QuestionType"]
            ]
            if filtered:
                result[comp_name] = filtered
        return result

    async def get_vocabulary(self, exam_name: str, level: int, count: int = 150) -> List[str]:
        """Return a sample of vocabulary words for the given exam and difficulty level."""
        vocab_data = self._load("vocabulary") or {}
        words = vocab_data.get(exam_name, {}).get(str(level), [])
        if count and len(words) > count:
            return random.sample(words, count)
        return list(words)

    async def get_system_template(self, name: str) -> Optional[str]:
        """
        Return None so async_get_Question_Template() falls back to the
        synchronous disk-based get_Question_Template() in io_utils.py.
        """
        return None

    async def get_component_template(self, category_name: str, template_name: str) -> Optional[str]:
        """
        Return None so async_get_Component_Template() falls back to the
        synchronous disk-based get_Component_Template() in io_utils.py.
        """
        return None

    async def get_component_schema(self, category_name: str, schema_name: str) -> Optional[str]:
        """Return None — callers have fallback logic."""
        return None

    async def get_question_component_mapping(self) -> Dict[str, Any]:
        """Return the full question component mapping (question_component_types.json)."""
        return self._load("question_component_types") or {}

    async def get_config(self, key: str) -> Any:
        """
        Generic config fetch by key name.
        Maps directly to json_files/{key}.json.
        """
        return self._load(key)

    async def get_difficulty_levels(self) -> Dict[str, Dict[str, str]]:
        """Return difficulty level descriptions (difficulty_levels.json)."""
        return self._load("difficulty_levels") or {}

    async def get_complexity_guidelines(self) -> Dict[str, List[str]]:
        """Return complexity guidelines extracted from prompt_component_info.json."""
        data = self._load("prompt_component_info") or {}
        return data.get("complexity_guidelines", {})

    async def get_dichotomous_pairs(self) -> List[Dict[str, Any]]:
        """Return dichotomous pairs from prompt_component_info.json."""
        data = self._load("prompt_component_info") or {}
        return data.get("dichotomousPairs", [])

    async def get_component_data(self, category_name: str, data_name: str) -> Optional[str]:
        """
        Return None — callers (e.g. MSR metadata handler) have explicit
        fallback logic when this returns None.
        """
        return None


# ---------------------------------------------------------------------------
# Module-level singleton — imported by all callers as:
#   from db_artilaries import artilaries
# ---------------------------------------------------------------------------
artilaries = ArtilariesDB()


async def get_all_configs():
    """Convenience helper kept for backward compatibility."""
    defs = await artilaries.get_exam_definition()
    qt_info = await artilaries.get_question_type_info()
    return defs, qt_info
