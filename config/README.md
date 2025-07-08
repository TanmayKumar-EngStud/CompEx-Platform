# Configuration Management

This directory contains all configuration files and schemas for the QGen question generation system, providing a centralized approach to managing exam-specific settings, generator configurations, and validation schemas.

## Directory Structure

### `/exams/`
Contains exam-specific configuration classes that define the core parameters and requirements for each standardized test.

- **`base_exam_config.py`**: Abstract base class defining the common interface for all exam configurations
- **`gmat_config.py`**: GMAT-specific configuration implementation  
- **`gre_config.py`**: GRE-specific configuration implementation

### `/generators/`
JSON configuration files that define the available question generators for each exam type.

- **`gmat_generators.json`**: Complete GMAT generator registry with section mappings and metadata
- **`gre_generators.json`**: Complete GRE generator registry with section mappings and metadata

### `/schemas/`
Schema definitions for validation and structure enforcement across the system.

- **`instruction_schemas.py`**: Schemas for system instruction validation and structure
- **`question_schemas.py`**: Comprehensive question type schemas and validation rules
- **`validation_schemas.py`**: General validation schemas for system components

## Data Flow

The configuration system follows a hierarchical data flow:

1. **Exam Selection**: Based on exam type (GMAT/GRE), the appropriate exam config is loaded
2. **Generator Discovery**: Generator configurations are loaded from JSON files to identify available question types  
3. **Schema Validation**: All inputs and outputs are validated against predefined schemas
4. **Runtime Configuration**: Configurations are merged and applied during question generation

## Key Functions

### Exam Configuration (`exams/`)

#### `BaseExamConfig` (Abstract)
- **`get_section_config(section_type)`**: Returns configuration for a specific exam section
- **`get_question_distribution(section_type)`**: Provides question type distribution for sections
- **`get_total_questions()`**: Calculates total questions across all sections
- **`get_time_limits()`**: Returns time limits for each section
- **`from_difficulty(difficulty)`**: Creates configuration from difficulty level
- **`to_dict()`**: Serializes configuration to dictionary format
- **`validate_section_type(section_type)`**: Validates section support for exam type

Input: Difficulty level (1-5), section type
Output: Configured exam instance with all parameters set

### Generator Configuration (`generators/`)

The JSON files define generator metadata:
- Generator class paths for dynamic loading
- Question type mappings and capabilities  
- Example prompts and usage patterns
- Section-specific requirements and time limits

### Schema Validation (`schemas/`)

#### `QuestionSchema`
- **`get_schema(question_type)`**: Retrieves schema for specific question type
- **`get_supported_question_types(exam_type)`**: Lists supported question types per exam
- **`validate_question_output(question_type, mode, output)`**: Validates generated content
- **`get_schema_info()`**: Provides comprehensive schema metadata

Input: Question type, generation mode, output data
Output: Validation results and error messages (if any)

## Example Usage

### Loading Exam Configuration
```python
from config.exams.gmat_config import GMATConfig

# Create GMAT configuration for difficulty level 3
config = GMATConfig.from_difficulty(3)
section_config = config.get_section_config(SectionType.QUANTITATIVE)
```

### Validating Question Output  
```python
from config.schemas.question_schemas import QuestionSchema

schema = QuestionSchema()
errors = schema.validate_question_output(
    QuestionType.DATA_SUFFICIENCY,
    "questionText", 
    {"passage": "...", "statements": [...]}
)
```

### Generator Discovery
```python
import json
with open('config/generators/gmat_generators.json') as f:
    generators = json.load(f)
    quant_generators = generators['sections'][0]['generators']
```

## Configuration Validation

All configurations undergo validation at multiple levels:
- **Structure Validation**: Ensures required fields are present
- **Type Validation**: Confirms correct data types for all parameters
- **Range Validation**: Validates difficulty levels, time limits, and counts
- **Dependency Validation**: Ensures referenced components exist and are accessible

The configuration system ensures consistency across the entire question generation pipeline while maintaining flexibility for future exam types and question formats.