import json
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import random
import asyncio

# Add Prisma client to path
sys.path.insert(0, str(Path(__file__).parent / "artilaries_prisma" / "generated"))
from prisma import Prisma

class ArtilariesDB:
    _instance = None
    _db = None
    _connected = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ArtilariesDB, cls).__new__(cls)
            cls._db = Prisma(
                datasource={
                    'url': 'postgresql://compexe_admin:QuiZA.0310!@localhost:5433/artilaries'
                }
            )
        return cls._instance

    async def connect(self):
        if not self._connected:
            await self._db.connect()
            self._connected = True

    async def disconnect(self):
        if self._connected:
            await self._db.disconnect()
            self._connected = False

    async def get_exam_definition(self) -> Dict[str, Any]:
        """Fetches exam structure for prompt generation."""
        await self.connect()
        exams = await self._db.exam.find_many(
            include={
                'stages': {
                    'include': {
                        'sections': {
                            'include': {
                                'typeCounts': {
                                    'include': {
                                        'questionType': True
                                    }
                                },
                                'category': True
                            }
                        }
                    }
                }
            }
        )
        
        result = {}
        for exam in exams:
            sections_dict = {}
            for stage in exam.stages:
                for section in stage.sections:
                    sec_data = {
                        'name': section.category.name,
                        'total': section.totalQuestions,
                        'question types': []
                    }
                    if hasattr(section, 'typeCounts'):
                        for qtc in section.typeCounts:
                            qtype_name = qtc.questionType.name
                            sec_data['question types'].append(qtype_name)
                            sec_data[qtype_name] = qtc.count
                    
                    sections_dict[str(section.id)] = sec_data
            result[exam.name] = sections_dict
        return result

    async def get_question_type_info(self) -> Dict[str, Any]:
        """Fetches metadata definitions for each question type from Config table."""
        return await self.get_config('question_type_info') or {}

    async def get_prompt_components_for_type(self, question_type: str) -> Dict[str, List[Dict[str, Any]]]:
        """
        Fetches all prompt components and their values relevant to a specific question type.
        Returns a dictionary mapping component name (e.g., 'questionTopic') to a list of options.
        """
        await self.connect()
        
        # This query fetches components that are linked to the specific question type
        links = await self._db.questiontypepromptcomponent.find_many(
            where={
                'questionType': {
                    'name': question_type
                }
            },
            include={
                'componentValue': {
                    'include': {
                        'component': True
                    }
                }
            }
        )
        
        # Reconstruct the prompt_component_info structure for this type
        structured_info = {}
        for link in links:
            comp_name = link.componentValue.component.name
            if comp_name not in structured_info:
                structured_info[comp_name] = []
            
            # Find or append to the appropriate entry (mimicking the JSON list of dicts with 'QuestionType' and 'list')
            # For simplicity, we can provide a single entry for this question type
            entry = next((e for e in structured_info[comp_name] if question_type in e['QuestionType']), None)
            if not entry:
                entry = {'QuestionType': [question_type], 'list': []}
                structured_info[comp_name].append(entry)
            
            val_raw = link.componentValue.value
            # Handle potential nested dicts if stored as specific format "key: value"
            if ": " in val_raw:
                try:
                    # Very simple parsing for "key: value" values injected during seeding
                    # This might need refinement for more complex structures
                    key, val = val_raw.split(": ", 1)
                    if isinstance(entry['list'], list):
                        entry['list'] = {} # Switch to dict if we see key-value pairs
                    if key not in entry['list']:
                        entry['list'][key] = []
                    entry['list'][key].append(val)
                except:
                    entry['list'].append(val_raw)
            else:
                entry['list'].append(val_raw)
                
        return structured_info

    async def get_vocabulary(self, exam_name: str, level: int, count: int = 150) -> List[str]:
        """Fetches words for vocabulary injection."""
        await self.connect()
        words = await self._db.vocabulary.find_many(
            where={
                'exam': {'name': exam_name},
                'difficultyLevel': {'level': level}
            },
            take=count
        )
        return [w.word for w in words]

    async def get_system_template(self, name: str) -> Optional[str]:
        """Fetches a system instruction template."""
        await self.connect()
        template = await self._db.systemtemplate.find_unique(where={'name': name})
        return template.content if template else None

    async def get_component_template(self, category_name: str, template_name: str) -> Optional[str]:
        """Fetches a component-specific template."""
        await self.connect()
        category = await self._db.componentcategory.find_unique(where={'name': category_name})
        if not category:
            return None
        template = await self._db.componenttemplate.find_unique(
            where={'categoryId_name': {'categoryId': category.id, 'name': template_name}}
        )
        return template.content if template else None

    async def get_component_schema(self, category_name: str, schema_name: str) -> Optional[str]:
        """Fetches a component validation schema."""
        await self.connect()
        category = await self._db.componentcategory.find_unique(where={'name': category_name})
        if not category:
            return None
        schema = await self._db.componentschema.find_unique(
            where={'categoryId_name': {'categoryId': category.id, 'name': schema_name}}
        )
        return schema.content if schema else None

    async def get_question_component_mapping(self) -> Dict[str, Any]:
        """Fetches the global question component mapping (legacy question_component_types.json)."""
        await self.connect()
        mapping = await self._db.questioncomponentmapping.find_first()
        return json.loads(mapping.content) if mapping else {}

    async def get_config(self, key: str) -> Any:
        """Fetches a generic JSON configuration by key."""
        await self.connect()
        config = await self._db.config.find_unique(where={'key': key})
        return json.loads(config.content) if config else None

    async def get_difficulty_levels(self) -> Dict[str, Dict[str, str]]:
        """Reconstructs the difficulty_levels.json structure from DB."""
        await self.connect()
        descs = await self._db.difficultydescription.find_many(
            include={'category': True, 'difficultyLevel': True}
        )
        result = {}
        for d in descs:
            cat = d.category.name
            level = str(d.difficultyLevel.level)
            if cat not in result:
                result[cat] = {}
            result[cat][level] = d.description
        return result

    async def get_complexity_guidelines(self) -> Dict[str, List[str]]:
        """Reconstructs complexity guidelines from DB."""
        await self.connect()
        guidelines = await self._db.complexityguideline.find_many(
            include={'category': True}
        )
        result = {}
        for g in guidelines:
            cat = g.category.name
            if cat not in result:
                result[cat] = []
            result[cat].append(g.guideline)
        return result

    async def get_dichotomous_pairs(self) -> List[Dict[str, Any]]:
        """Fetches dichotomous pairs relevant to question types."""
        config = await self.get_config('prompt_component_info')
        return config.get('dichotomousPairs', []) if config else []

    async def get_component_data(self, category_name: str, data_name: str) -> Optional[str]:
        """Fetches a component validation data file."""
        await self.connect()
        category = await self._db.componentcategory.find_unique(where={'name': category_name})
        if not category:
            return None
        data = await self._db.componentdata.find_unique(
            where={'categoryId_name': {'categoryId': category.id, 'name': data_name}}
        )
        return data.content if data else None

# Global instance for easy access
artilaries = ArtilariesDB()

async def get_all_configs():
    """Converts the relational tables back into the expected JSON-like dictionary structure for a seamless transition."""
    defs = await artilaries.get_exam_definition()
    qt_info = await artilaries.get_question_type_info()
    return defs, qt_info
