# 📋 Core Enums Module

This directory contains the fundamental enumerations that provide type-safe representations of all core concepts in the GMAT/GRE question generation system. These enums serve as the single source of truth for exam types, question classifications, section structures, and difficulty levels.

---

## 📄 Data Flow and Manipulation

**🎯 Purpose**: This module provides standardized enumerations that eliminate string-based configurations and provide type safety throughout the entire application. Data flows from string inputs (user prompts, configuration files) through enum conversion methods, and then throughout the system as strongly-typed enum values.

**Flow**: Raw string data → Enum conversion methods → Typed enum values → System-wide usage → String representations for output

---

## 📁 File Structure

### `exam_types.py` 🎓

**🎯 Purpose**: Defines supported examination types with conversion utilities and display formatting.

#### **Class: `ExamType`**
*   **🎯 Purpose**: Enum representing the two supported standardized exams
*   **Values**:
    *   `GMAT = "gmat"` - Graduate Management Admission Test
    *   `GRE = "gre"` - Graduate Record Examinations

#### **Method: `from_string`**
*   **🎯 Purpose**: Convert string representations to ExamType enum values with case-insensitive matching
*   **📥 Inputs**:
    *   `value: str` - String representation of exam type
    *   Example values: `"GMAT"`, `"gre"`, `"GRE"`, `"gmat"`
*   **↩️ Returns**:
    *   `ExamType` - Corresponding enum value
    *   Example: `ExamType.GMAT` for input `"gmat"`
    *   Example: `ExamType.GRE` for input `"GRE"`
*   **📲 Called By**:
    *   `core/utilities/validation_utils.py:validate_exam_type()`
    *   `config/exams/base_exam_config.py:BaseExamConfig.__init__()`
    *   `core/factories/question_generator_factory.py:QuestionGeneratorFactory.create_generator()`
*   **➡️ Calls**: No external function calls

#### **Method: `get_all_values`**
*   **🎯 Purpose**: Return all available exam type string values for validation and iteration
*   **📥 Inputs**: None (class method)
*   **↩️ Returns**:
    *   `List[str]` - List of all exam type values
    *   Example: `["gmat", "gre"]`
*   **📲 Called By**:
    *   `config/schemas/validation_schemas.py:get_exam_type_schema()`
    *   `testing/test_main_instructions.py:test_all_exam_types()`
*   **➡️ Calls**: No external function calls

#### **Property: `display_name`**
*   **🎯 Purpose**: Provide human-readable uppercase exam name for UI display
*   **📥 Inputs**: None (property)
*   **↩️ Returns**:
    *   `str` - Uppercase exam name
    *   Example: `"GMAT"` for `ExamType.GMAT`
    *   Example: `"GRE"` for `ExamType.GRE`
*   **📲 Called By**:
    *   `main.py:main()` - For logging paper generation
    *   `core/mock/unified_mock_generator.py:UnifiedMockGenerator.generate_mock_paper()`
*   **➡️ Calls**: No external function calls

---

### `section_types.py` 📚

**🎯 Purpose**: Defines examination section types with exam-specific support mapping.

#### **Class: `SectionType`**
*   **🎯 Purpose**: Enum representing different sections within standardized exams
*   **Values**:
    *   `QUANTITATIVE = "quantitative"` - Mathematical reasoning section
    *   `VERBAL = "verbal"` - Language and reading comprehension section  
    *   `INTEGRATED_REASONING = "integrated_reasoning"` - Multi-source data analysis (GMAT only)

#### **Method: `from_string`**
*   **🎯 Purpose**: Convert string representations to SectionType with abbreviation support
*   **📥 Inputs**:
    *   `value: str` - String representation of section
    *   Example values: `"quantitative"`, `"Quants"`, `"Q"`, `"verbal"`, `"V"`, `"IR"`, `"integrated_reasoning"`
*   **↩️ Returns**:
    *   `SectionType` - Corresponding enum value
    *   Example: `SectionType.QUANTITATIVE` for input `"Quants"`
    *   Example: `SectionType.VERBAL` for input `"V"`
    *   Example: `SectionType.INTEGRATED_REASONING` for input `"IR"`
*   **📲 Called By**:
    *   `core/prompts/prompt_generator_factory.py:PromptGeneratorFactory.create_generator()`
    *   `GMAT/Mock_prompts/Quantitative.py:generate_prompts()`
    *   `GMAT/Mock_prompts/Verbal.py:generate_prompts()`
    *   `GMAT/Mock_prompts/Integrated_Reasoning.py:generate_prompts()`
*   **➡️ Calls**: No external function calls

#### **Method: `get_supported_sections`**
*   **🎯 Purpose**: Return sections available for a specific exam type
*   **📥 Inputs**:
    *   `exam_type: ExamType` - The exam type to query
    *   Example values: `ExamType.GMAT`, `ExamType.GRE`
*   **↩️ Returns**:
    *   `List[SectionType]` - List of supported sections
    *   Example: `[SectionType.QUANTITATIVE, SectionType.VERBAL, SectionType.INTEGRATED_REASONING]` for `ExamType.GMAT`
    *   Example: `[SectionType.QUANTITATIVE, SectionType.VERBAL]` for `ExamType.GRE`
*   **📲 Called By**:
    *   `config/exams/gmat_config.py:GMATConfig.__init__()`
    *   `config/exams/gre_config.py:GREConfig.__init__()`
    *   `core/mock/paper_builder.py:PaperBuilder.build_sections()`
*   **➡️ Calls**: No external function calls

#### **Property: `short_name`**
*   **🎯 Purpose**: Provide abbreviated section names for compact display
*   **📥 Inputs**: None (property)
*   **↩️ Returns**:
    *   `str` - Abbreviated section name
    *   Example: `"Quants"` for `SectionType.QUANTITATIVE`
    *   Example: `"Verbal"` for `SectionType.VERBAL`
    *   Example: `"IR"` for `SectionType.INTEGRATED_REASONING`
*   **📲 Called By**:
    *   `core/mock/section_builder.py:SectionBuilder.build_section()`
    *   `terminal_logger.py:log_section_generation()`
*   **➡️ Calls**: No external function calls

---

### `question_types.py` ❓

**🎯 Purpose**: Comprehensive question type classification system with exam and section mapping capabilities.

#### **Class: `QuestionType`**
*   **🎯 Purpose**: Enum representing all supported question types across GMAT and GRE exams
*   **Values**:
    *   **Quantitative Types**:
        *   `DATA_SUFFICIENCY = "data_sufficiency"` - Two-statement sufficiency questions
        *   `PROBLEM_SOLVING = "problem_solving"` - Standard math word problems
        *   `NUMERIC_ENTRY = "numeric_entry"` - GRE numerical answer questions
        *   `QUANTITATIVE_COMPARISON = "quantitative_comparison"` - GRE comparison questions
    *   **Verbal Types**:
        *   `READING_COMPREHENSION = "reading_comprehension"` - Passage-based questions
        *   `CRITICAL_REASONING = "critical_reasoning"` - Logical argument analysis
        *   `SENTENCE_CORRECTION = "sentence_correction"` - Grammar and style correction
        *   `TEXT_COMPLETION = "text_completion"` - GRE fill-in-the-blank questions
        *   `SENTENCE_EQUIVALENCE = "sentence_equivalence"` - GRE equivalent meaning questions
    *   **Integrated Reasoning Types (GMAT Only)**:
        *   `GRAPHIC_INTERPRETATION = "graphic_interpretation"` - Chart and graph analysis
        *   `TABLE_ANALYSIS = "table_analysis"` - Data table analysis
        *   `TWO_PART_ANALYSIS = "two_part_analysis"` - Related question pairs
        *   `MULTI_SOURCE_REASONING = "multi_source_reasoning"` - Multiple data source questions
    *   **General Types**:
        *   `MULTIPLE_CHOICE_SINGLE = "multiple_choice_single"` - Single correct answer
        *   `MULTIPLE_CHOICE_MULTIPLE = "multiple_choice_multiple"` - Multiple correct answers

#### **Method: `from_string`**
*   **🎯 Purpose**: Convert string representations and common abbreviations to QuestionType enum values
*   **📥 Inputs**:
    *   `value: str` - String representation or abbreviation
    *   Example values: `"DS"`, `"data_sufficiency"`, `"PS"`, `"problem_solving"`, `"RC"`, `"rc-s"`, `"rc-m"`, `"rc-l"`, `"CR"`, `"GI"`, `"TA"`, `"TPA"`, `"MSR"`
*   **↩️ Returns**:
    *   `QuestionType` - Corresponding enum value
    *   Example: `QuestionType.DATA_SUFFICIENCY` for input `"DS"`
    *   Example: `QuestionType.READING_COMPREHENSION` for input `"rc-s"`
    *   Example: `QuestionType.GRAPHIC_INTERPRETATION` for input `"GI"`
*   **📲 Called By**:
    *   All 16 question generator files in `GMAT/` and `GRE/` subdirectories
    *   `core/factories/question_generator_factory.py:QuestionGeneratorFactory.create_generator()`
    *   `GMAT/Mock.py:GENERATOR_MAP` initialization
    *   `GRE/Mock.py:GENERATOR_MAP` initialization
*   **➡️ Calls**: No external function calls

#### **Method: `get_section_questions`**
*   **🎯 Purpose**: Return supported question types for a specific section and exam combination
*   **📥 Inputs**:
    *   `section_type: SectionType` - The section to query
    *   `exam_type: ExamType` - The exam type to query
    *   Example combinations: `(SectionType.QUANTITATIVE, ExamType.GMAT)`, `(SectionType.VERBAL, ExamType.GRE)`, `(SectionType.INTEGRATED_REASONING, ExamType.GMAT)`
*   **↩️ Returns**:
    *   `List[QuestionType]` - List of supported question types
    *   Example: `[QuestionType.DATA_SUFFICIENCY, QuestionType.PROBLEM_SOLVING]` for `(SectionType.QUANTITATIVE, ExamType.GMAT)`
    *   Example: `[QuestionType.READING_COMPREHENSION, QuestionType.TEXT_COMPLETION, QuestionType.SENTENCE_EQUIVALENCE]` for `(SectionType.VERBAL, ExamType.GRE)`
    *   Example: `[QuestionType.GRAPHIC_INTERPRETATION, QuestionType.TABLE_ANALYSIS, QuestionType.TWO_PART_ANALYSIS, QuestionType.MULTI_SOURCE_REASONING]` for `(SectionType.INTEGRATED_REASONING, ExamType.GMAT)`
*   **📲 Called By**:
    *   `core/mock/section_builder.py:SectionBuilder.build_section()`
    *   `config/generators/gmat_generators.json` configuration loading
    *   `config/generators/gre_generators.json` configuration loading
*   **➡️ Calls**: No external function calls

#### **Method: `get_all_gmat_types`**
*   **🎯 Purpose**: Return all question types supported by GMAT exam
*   **📥 Inputs**: None (class method)
*   **↩️ Returns**:
    *   `List[QuestionType]` - All GMAT question types
    *   Example: `[QuestionType.DATA_SUFFICIENCY, QuestionType.PROBLEM_SOLVING, QuestionType.READING_COMPREHENSION, QuestionType.CRITICAL_REASONING, QuestionType.SENTENCE_CORRECTION, QuestionType.GRAPHIC_INTERPRETATION, QuestionType.TABLE_ANALYSIS, QuestionType.TWO_PART_ANALYSIS, QuestionType.MULTI_SOURCE_REASONING]`
*   **📲 Called By**:
    *   `config/exams/gmat_config.py:GMATConfig.__init__()`
    *   `testing/test_generator_integration.py:test_gmat_generators()`
*   **➡️ Calls**: No external function calls

#### **Method: `get_all_gre_types`**
*   **🎯 Purpose**: Return all question types supported by GRE exam
*   **📥 Inputs**: None (class method)
*   **↩️ Returns**:
    *   `List[QuestionType]` - All GRE question types
    *   Example: `[QuestionType.DATA_SUFFICIENCY, QuestionType.NUMERIC_ENTRY, QuestionType.PROBLEM_SOLVING, QuestionType.QUANTITATIVE_COMPARISON, QuestionType.READING_COMPREHENSION, QuestionType.TEXT_COMPLETION, QuestionType.SENTENCE_EQUIVALENCE]`
*   **📲 Called By**:
    *   `config/exams/gre_config.py:GREConfig.__init__()`
    *   `testing/test_generator_integration.py:test_gre_generators()`
*   **➡️ Calls**: No external function calls

#### **Property: `short_name`**
*   **🎯 Purpose**: Provide standard abbreviations for question types
*   **📥 Inputs**: None (property)
*   **↩️ Returns**:
    *   `str` - Standard abbreviation
    *   Example: `"DS"` for `QuestionType.DATA_SUFFICIENCY`
    *   Example: `"PS"` for `QuestionType.PROBLEM_SOLVING`
    *   Example: `"RC"` for `QuestionType.READING_COMPREHENSION`
    *   Example: `"GI"` for `QuestionType.GRAPHIC_INTERPRETATION`
    *   Example: `"MSR"` for `QuestionType.MULTI_SOURCE_REASONING`
*   **📲 Called By**:
    *   `core/mock/paper_builder.py:PaperBuilder.log_question_generation()`
    *   `terminal_logger.py:log_question_type()`
*   **➡️ Calls**: No external function calls

#### **Property: `is_parent_child_type`**
*   **🎯 Purpose**: Determine if question type supports parent-child structure (shared content with multiple sub-questions)
*   **📥 Inputs**: None (property)
*   **↩️ Returns**:
    *   `bool` - True if parent-child type, False otherwise
    *   Example: `True` for `QuestionType.READING_COMPREHENSION`
    *   Example: `True` for `QuestionType.MULTI_SOURCE_REASONING`
    *   Example: `False` for `QuestionType.DATA_SUFFICIENCY`
*   **📲 Called By**:
    *   `core/components/question_components.py:BaseQuestionComponent.__init__()`
    *   `core/instructions/instruction_manager.py:InstructionManager._apply_question_type_optimizations()`
*   **➡️ Calls**: No external function calls

#### **Property: `section_type`**
*   **🎯 Purpose**: Map question type to its corresponding section
*   **📥 Inputs**: None (property)
*   **↩️ Returns**:
    *   `SectionType` - The section this question type belongs to
    *   Example: `SectionType.QUANTITATIVE` for `QuestionType.DATA_SUFFICIENCY`
    *   Example: `SectionType.VERBAL` for `QuestionType.READING_COMPREHENSION`
    *   Example: `SectionType.INTEGRATED_REASONING` for `QuestionType.GRAPHIC_INTERPRETATION`
*   **📲 Called By**:
    *   `core/factories/question_generator_factory.py:QuestionGeneratorFactory.create_generator()`
    *   `core/mock/section_builder.py:SectionBuilder.validate_question_placement()`
*   **➡️ Calls**: No external function calls

---

### `difficulty_levels.py` 🔥

**🎯 Purpose**: Standardized difficulty level system with conversion utilities and comparative operations.

#### **Class: `DifficultyLevel`**
*   **🎯 Purpose**: Enum representing question difficulty on a standardized 1-5 scale
*   **Values**:
    *   `VERY_EASY = 1` - Basic concepts, straightforward application (0-20th percentile)
    *   `EASY = 2` - Simple problem-solving, minimal complexity (20-40th percentile)
    *   `MEDIUM = 3` - Moderate complexity, multiple steps required (40-60th percentile)
    *   `HARD = 4` - Complex problem-solving, advanced concepts (60-80th percentile)
    *   `VERY_HARD = 5` - Expert level, highly complex reasoning (80-100th percentile)

#### **Method: `from_int`**
*   **🎯 Purpose**: Convert integer values to DifficultyLevel enum with validation
*   **📥 Inputs**:
    *   `value: int` - Integer difficulty level
    *   Example values: `1`, `2`, `3`, `4`, `5`
*   **↩️ Returns**:
    *   `DifficultyLevel` - Corresponding enum value
    *   Example: `DifficultyLevel.VERY_EASY` for input `1`
    *   Example: `DifficultyLevel.HARD` for input `4`
*   **📲 Called By**:
    *   `core/utilities/validation_utils.py:validate_difficulty()`
    *   `main.py:load_difficulty_from_pickle()`
    *   All generator files when parsing difficulty from prompts
*   **➡️ Calls**: No external function calls

#### **Method: `from_string`**
*   **🎯 Purpose**: Convert string representations and names to DifficultyLevel with flexible parsing
*   **📥 Inputs**:
    *   `value: str` - String representation of difficulty
    *   Example values: `"1"`, `"easy"`, `"medium"`, `"hard"`, `"very_easy"`, `"expert"`
*   **↩️ Returns**:
    *   `DifficultyLevel` - Corresponding enum value
    *   Example: `DifficultyLevel.EASY` for input `"easy"`
    *   Example: `DifficultyLevel.VERY_HARD` for input `"expert"`
*   **📲 Called By**:
    *   `core/utilities/validation_utils.py:parse_difficulty_from_prompt()`
    *   `config/schemas/validation_schemas.py:difficulty_schema_validator()`
*   **➡️ Calls**: 
    *   `DifficultyLevel.from_int()` for numeric string inputs

#### **Method: `get_all_levels`**
*   **🎯 Purpose**: Return all difficulty levels in ascending order for iteration and validation
*   **📥 Inputs**: None (class method)
*   **↩️ Returns**:
    *   `List[DifficultyLevel]` - All difficulty levels in order
    *   Example: `[DifficultyLevel.VERY_EASY, DifficultyLevel.EASY, DifficultyLevel.MEDIUM, DifficultyLevel.HARD, DifficultyLevel.VERY_HARD]`
*   **📲 Called By**:
    *   `config/schemas/validation_schemas.py:get_difficulty_choices()`
    *   `testing/test_difficulty_progression.py:test_all_levels()`
*   **➡️ Calls**: No external function calls

#### **Method: `get_range`**
*   **🎯 Purpose**: Return difficulty levels within a specified range for progressive difficulty systems
*   **📥 Inputs**:
    *   `min_level: DifficultyLevel` - Minimum difficulty level
    *   `max_level: DifficultyLevel` - Maximum difficulty level
    *   Example combinations: `(DifficultyLevel.EASY, DifficultyLevel.HARD)`, `(DifficultyLevel.VERY_EASY, DifficultyLevel.MEDIUM)`
*   **↩️ Returns**:
    *   `List[DifficultyLevel]` - Levels within range (inclusive)
    *   Example: `[DifficultyLevel.EASY, DifficultyLevel.MEDIUM, DifficultyLevel.HARD]` for input `(DifficultyLevel.EASY, DifficultyLevel.HARD)`
*   **📲 Called By**:
    *   `core/mock/paper_builder.py:PaperBuilder.generate_progressive_difficulty()`
    *   `main.py:progressive_difficulty_generation()`
*   **➡️ Calls**: 
    *   `DifficultyLevel.get_all_levels()` to get base list for range extraction

#### **Property: `percentile_range`**
*   **🎯 Purpose**: Provide approximate percentile ranges for difficulty calibration
*   **📥 Inputs**: None (property)
*   **↩️ Returns**:
    *   `Tuple[int, int]` - Percentile range (min, max)
    *   Example: `(0, 20)` for `DifficultyLevel.VERY_EASY`
    *   Example: `(40, 60)` for `DifficultyLevel.MEDIUM`
    *   Example: `(80, 100)` for `DifficultyLevel.VERY_HARD`
*   **📲 Called By**:
    *   `core/mock/paper_builder.py:PaperBuilder.calibrate_difficulty_distribution()`
    *   `core/instructions/instruction_manager.py:InstructionManager._apply_difficulty_optimizations()`
*   **➡️ Calls**: No external function calls

#### **Method: `next_level`**
*   **🎯 Purpose**: Get the next higher difficulty level for progression systems
*   **📥 Inputs**: None (instance method)
*   **↩️ Returns**:
    *   `Optional[DifficultyLevel]` - Next higher level or None if already at maximum
    *   Example: `DifficultyLevel.MEDIUM` for `DifficultyLevel.EASY.next_level()`
    *   Example: `None` for `DifficultyLevel.VERY_HARD.next_level()`
*   **📲 Called By**:
    *   `main.py:increment_difficulty_after_paper()`
    *   `core/mock/paper_builder.py:PaperBuilder.adaptive_difficulty_progression()`
*   **➡️ Calls**: 
    *   `DifficultyLevel.from_int()` to create next level enum

#### **Method: `prev_level`**
*   **🎯 Purpose**: Get the next lower difficulty level for regression systems
*   **📥 Inputs**: None (instance method)
*   **↩️ Returns**:
    *   `Optional[DifficultyLevel]` - Next lower level or None if already at minimum
    *   Example: `DifficultyLevel.EASY` for `DifficultyLevel.MEDIUM.prev_level()`
    *   Example: `None` for `DifficultyLevel.VERY_EASY.prev_level()`
*   **📲 Called By**:
    *   `core/mock/paper_builder.py:PaperBuilder.fallback_difficulty()`
*   **➡️ Calls**: 
    *   `DifficultyLevel.from_int()` to create previous level enum

---

## 🔗 Inter-Enum Dependencies

**Data Relationships**:

1. **SectionType → ExamType**: `SectionType.get_supported_sections(exam_type)` maps which sections are available for each exam
2. **QuestionType → SectionType**: `QuestionType.section_type` property maps questions to sections
3. **QuestionType → ExamType + SectionType**: `QuestionType.get_section_questions(section_type, exam_type)` provides comprehensive mapping
4. **Factory Pattern Integration**: All enums are used together in `QuestionGeneratorFactory.create_generator(exam_type, question_type, section_type, difficulty_level)`

**Cross-References**:
- `section_types.py` imports `ExamType` from `exam_types.py`
- `question_types.py` imports both `ExamType` and `SectionType`
- Factory classes import all four enums for comprehensive type checking

---

## 🏗️ System Integration Points

**Configuration System**: All enums are used to define exam structures in `config/exams/`
**Factory Pattern**: All enums serve as parameters for question generator creation
**Validation System**: All enums provide conversion methods for input validation
**Legacy Compatibility**: All enums provide string conversion for backward compatibility with existing generators
**Template System**: Enums are used to select appropriate instruction templates
**Mock Generation**: Enums define paper structure and question distribution