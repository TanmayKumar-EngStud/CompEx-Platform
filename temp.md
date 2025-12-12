# Prompt Generator Modernization Guide

## Overview
This guide explains how to modernize prompt generator files to use the new nomenclature-based system with random selection instead of the old combination_number approach. It also includes enhanced topic-skill mapping for better contextual accuracy.

## Completed Updates
✅ **GMAT Customizations**: Updated `/system_instructions/gmat/customizations.json` quant sections  
✅ **GRE Customizations**: Updated `/system_instructions/gre/customizations.json` quant sections  
✅ **BasePromptGenerator**: Enhanced to handle dictionary format questionTopic  
✅ **GMAT IR Prompts**: Updated `/core/prompts/gmat/gmat_ir_prompts.py` to use nomenclature  
✅ **GRE Quants Prompts**: Updated `/core/prompts/gre/gre_quants_prompts.py` to use nomenclature  
✅ **GRE Verbal Prompts**: Updated `/core/prompts/gre/gre_verbal_prompts.py` to use nomenclature

## Enhanced Topic-Skill Mapping (Advanced Feature)

### Problem Statement
Currently, questionTopic and focused_skill are separate arrays, leading to random combinations that may not be contextually accurate. For example, selecting "Geometry" as topic and "interest_calculations" as skill doesn't make sense.

### Solution: Dictionary-Based Topic-Skill Mapping
Transform questionTopic from array to dictionary where each topic contains its specific skills. This change will only happen in some customization cases (like quants sections), while verbal sections will keep the existing array format. The BasePromptGenerator must handle both scenarios automatically.

#### Current Structure (Array Format):
```json
"questionTopic": [
  "Number Properties",
  "Fractions, Decimals, and Percentages", 
  "Ratios and Proportions",
  "Algebra"
],
"focused_skill": [
  "Estimation and Approximation",
  "Business Model Analysis", 
  "Financial Calculations"
]
```

#### Proposed Structure (Dictionary Format):
```json
"questionTopic": {
  "Number Properties": [
    "prime_numbers", "factors_and_multiples", "divisibility",
    "remainder_problems", "number_properties"
  ],
  "Fractions, Decimals, and Percentages": [
    "basic_operations", "percentages", "decimal_conversions", 
    "fraction_operations", "percentage_calculations"
  ],
  "Ratios and Proportions": [
    "ratio_calculations", "proportion_solving", "scale_problems",
    "unit_conversions", "rate_problems"
  ],
  "Algebra": [
    "linear_equations", "quadratic_equations", "inequalities",
    "functions", "sequences", "coordinate_geometry"
  ],
  "Geometry": [
    "triangles", "circles", "rectangles_and_squares",
    "coordinate_geometry", "area_and_perimeter", "volume"
  ],
  "Word Problems": [
    "work_and_time", "speed_distance_time", "age_problems",
    "mixture_problems", "investment_problems"
  ]
},
"focused_skill": [
  // Fallback skills if topic-specific skills not found
  "general_problem_solving", "mathematical_reasoning"
]
```

### Required BasePromptGenerator Enhancement

✅ **COMPLETED** - Enhanced logic has been implemented in `_substitute_nomenclature_variables` method:

```python
# Enhanced questionTopic handling
if var == "questionTopic":
    topic_values = question_config.get("questionTopic", [])
    if isinstance(topic_values, dict):
        # New: Dictionary format - select topic and store for skill mapping
        selected_topic = self.get_random_element(list(topic_values.keys()))
        substituted = substituted.replace(f"<{var}>", f"<{selected_topic}>")
        # Store selected topic for focused_skill selection
        self._selected_topic = selected_topic
        self._topic_skills = topic_values[selected_topic]
        continue
    elif isinstance(topic_values, list):
        # Existing: List format - works as before
        selected_topic = self.get_random_element(topic_values)
        substituted = substituted.replace(f"<{var}>", f"<{selected_topic}>")
        continue

# Enhanced focused_skill handling  
if var == "focused_skill":
    # First priority: Use skills from selected topic (if dictionary format)
    if hasattr(self, '_topic_skills') and self._topic_skills:
        selected_skill = self.get_random_element(self._topic_skills)
        substituted = substituted.replace(f"<{var}>", f"<{selected_skill}>")
        continue
    
    # Second priority: Use general focused_skill array
    skill_values = question_config.get("focused_skill", [])
    if skill_values:
        selected_skill = self.get_random_element(skill_values)
        substituted = substituted.replace(f"<{var}>", f"<{selected_skill}>")
        continue
    
    # Fallback
    substituted = substituted.replace(f"<{var}>", "<general>")
    continue
```

### Benefits of Enhanced Mapping
✅ **Contextual Accuracy**: "Geometry" → "area_calculations" instead of "interest_problems"  
✅ **Backward Compatibility**: Still works with existing array format  
✅ **Intelligent Selection**: Skills are contextually relevant to topics  
✅ **Maintainable**: Easy to add new topic-skill mappings  
✅ **Flexible**: Falls back gracefully when mappings don't exist

## Pattern for Changes

### 1. Remove Imports
**Before:**
```python
import random
from typing import List
```

**After:**
```python
from typing import List
```

**Reason:** We now use `self.get_random_element()` from the base class instead of direct `random` calls.

### 2. Update Main Method Docstring
**Before:**
```python
def generate_question_prompts(self) -> List[str]:
    """Generate question prompts for [SECTION] section."""
```

**After:**
```python
def generate_question_prompts(self) -> List[str]:
    """
    Generate question prompts for [SECTION] section using nomenclature patterns.
    
    Returns:
        nomenclature:
        `[actual nomenclature pattern from customizations.json]`
    """
```

### 3. Replace Main Method Logic
**Before (Old Pattern):**
```python
def generate_question_prompts(self) -> List[str]:
    difficulty_pool = self.get_difficulty_pool()
    prompts = []
    
    # Get combination number for variety
    cn = self.component_allocation.get("combination_number", 0)
    
    # Hardcoded logic with _get_next_element(list, cn + i)
    for i in range(self.total_questions):
        style = self._get_next_element(question_styles, cn + i)
        topic = self._get_next_element(topics, cn + i)
        # ... more hardcoded selection
        prompt = self._create_prompt(style, topic, skill, difficulty)
        prompts.append(prompt)
    
    self._update_combination_counter()
    return prompts
```

**After (New Pattern):**
```python
def generate_question_prompts(self) -> List[str]:
    difficulty_pool = self.get_difficulty_pool()
    prompts = []
    
    # Get section configuration from customizations
    section_config = self.customizations.get("[section_key]", {})
    
    # Get question distribution (varies by exam/section)
    # Example for GMAT IR: MSR=6, TA=5, GI=5, TPA=4
    # Example for GRE: varies by section
    
    question_index = 0
    
    # For each question type, use nomenclature generation
    for _ in range(num_questions_of_type):
        difficulty = difficulty_pool[question_index] if question_index < len(difficulty_pool) else 3
        
        prompt = self.generate_nomenclature_based_prompt(
            "question_type_name",  # e.g., "graphic interpretation", "table analysis"
            difficulty
        )
        prompts.append(prompt)
        question_index += 1
    
    return prompts
```

### 4. Remove Unused Methods
**Delete these methods:**
- `_get_default_skills()` - No longer needed
- `_generate_[type]_prompts()` helper methods - No longer needed
- Any other helper methods that use combination_number

**Keep only:**
- `_get_default_component_allocation()` - But simplify it

### 5. Simplify Default Component Allocation
**Before:**
```python
def _get_default_component_allocation(self):
    return {
        "combination_number": 0,
        "question_style": [...],
        "options": [...],
        "topic1": {"focused_skill": [...]},
        "topic2": {"focused_skill": [...]},
        # ... lots of hardcoded values
    }
```

**After:**
```python
def _get_default_component_allocation(self):
    """
    Get [SECTION] specific component allocation.
    
    Note: This is now primarily loaded from customizations.json file.
    These are fallback defaults if customizations file is not available.
    """
    return {
        # Only essential fallback values from customizations.json
        "Question_Type_1": default_count,
        "Question_Type_2": default_count,
        # etc.
    }
```

## Section-Specific Information

### GMAT Integrated Reasoning
**Customizations path:** `system_instructions/gmat/customizations.json` → `"integrated reasoning"`
**Question types:** Multi_Source_Reasoning, Table_Analysis, Graphics_Interpretation, Two_Part_Analysis
**Distribution:** MSR=6, TA=5, GI=5, TPA=4 (from customizations.json)

### GRE Quantitative
**Customizations path:** `system_instructions/gre/customizations.json` → `"quants"`
**Check file for:** Question types, nomenclature patterns, distributions

### GRE Verbal  
**Customizations path:** `system_instructions/gre/customizations.json` → `"verbal"`
**Check file for:** Question types, nomenclature patterns, distributions

## Steps to Follow

1. **Read customizations.json** for the relevant section to understand:
   - Available question types
   - Nomenclature patterns
   - Question distributions
   - Variable options

2. **Update imports** - Remove `random`

3. **Update main method:**
   - Replace combination_number logic with random selection
   - Use `generate_nomenclature_based_prompt()` calls
   - Get distributions from customizations
   - Add proper nomenclature docstring

4. **Remove unused methods**

5. **Simplify default allocation**

## Key Benefits After Changes
- ✅ Uses exact nomenclature patterns from customizations.json
- ✅ Proper random selection without combination_number complexity  
- ✅ Much cleaner, shorter code
- ✅ Fully configurable via JSON files
- ✅ No hardcoded values scattered throughout

## Verification
After changes, the prompt generators should:
1. Generate prompts that exactly match nomenclature patterns
2. Use random selection for all variables
3. Pull all configurations from customizations.json
4. Have much cleaner, shorter code files