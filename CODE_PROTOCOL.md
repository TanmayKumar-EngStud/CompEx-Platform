# Code Protocol and Standards - GMAT/GRE Question Generation System

## Overview

This document establishes comprehensive coding standards, naming conventions, and architectural guidelines for the unified GMAT/GRE Question Generation System. These protocols ensure maximum code reusability, maintainability, and consistency across the entire codebase.

## Table of Contents

1. [Project Architecture](#project-architecture)
2. [Directory Structure](#directory-structure)
3. [Naming Conventions](#naming-conventions)
4. [Code Organization](#code-organization)
5. [Type Safety and Enums](#type-safety-and-enums)
6. [Error Handling](#error-handling)
7. [Configuration Management](#configuration-management)
8. [Testing Standards](#testing-standards)
9. [Documentation Standards](#documentation-standards)
10. [Import Organization](#import-organization)

---

## Project Architecture

### Core Principles

1. **Single Responsibility Principle**: Each module handles one specific concern
2. **Open/Closed Principle**: Extensible for new exam types without modifying existing code
3. **Dependency Inversion**: Depend on abstractions, not concrete implementations
4. **Configuration Over Convention**: Use configuration files for customization
5. **Type Safety First**: Comprehensive use of type hints and enums

### Architectural Layers

```
┌─────────────────────────────────────┐
│            Application Layer        │  ← main.py, CLI interfaces
├─────────────────────────────────────┤
│            Service Layer            │  ← Mock generators, orchestration
├─────────────────────────────────────┤
│            Business Layer           │  ← Question generators, processors
├─────────────────────────────────────┤
│            Core Layer               │  ← Shared utilities, interfaces
├─────────────────────────────────────┤
│            Data Layer               │  ← Database, file operations
└─────────────────────────────────────┘
```

---

## Directory Structure

### Optimized Folder Structure

```
QGen-py-compex/
├── main.py                           # Application entry point
├── requirements.txt                  # Dependencies
├── prisma/                          # Database schema and migrations
│   ├── schema.prisma
│   └── migrations/
├── core/                           # Core reusable components
│   ├── __init__.py
│   ├── enums/                      # Type-safe enumerations
│   │   ├── __init__.py
│   │   ├── exam_types.py           # ExamType.GMAT, ExamType.GRE
│   │   ├── section_types.py        # SectionType.QUANTS, VERBAL, IR
│   │   ├── question_types.py       # QuestionType.DATA_SUFFICIENCY, etc.
│   │   ├── difficulty_levels.py    # DifficultyLevel.EASY to EXPERT
│   │   └── api_status.py           # APIStatus.AVAILABLE, RATE_LIMITED
│   ├── interfaces/                 # Abstract base classes
│   │   ├── __init__.py
│   │   ├── question_generator.py   # IQuestionGenerator protocol
│   │   ├── mock_generator.py       # IMockGenerator protocol
│   │   ├── prompt_generator.py     # IPromptGenerator protocol
│   │   └── api_client.py           # IAPIClient protocol
│   ├── exceptions/                 # Custom exception classes
│   │   ├── __init__.py
│   │   ├── generation_exceptions.py
│   │   ├── api_exceptions.py
│   │   └── validation_exceptions.py
│   ├── utilities/                  # Shared utility functions
│   │   ├── __init__.py
│   │   ├── json_utils.py           # JSON processing and validation
│   │   ├── api_utils.py            # API key management and rotation
│   │   ├── file_utils.py           # File operations and path management
│   │   ├── validation_utils.py     # Input validation and sanitization
│   │   ├── logging_utils.py        # Structured logging utilities
│   │   └── time_utils.py           # Time and timestamp utilities
│   ├── components/                 # Unified question components
│   │   ├── __init__.py
│   │   ├── question_components.py  # Core question processing classes
│   │   ├── adapters/               # Exam-specific adapters
│   │   │   ├── __init__.py
│   │   │   ├── gmat_adapter.py
│   │   │   └── gre_adapter.py
│   │   └── processors/             # Content processors
│   │       ├── __init__.py
│   │       ├── json_processor.py
│   │       ├── text_processor.py
│   │       └── validation_processor.py
│   ├── threading/                  # Thread management
│   │   ├── __init__.py
│   │   ├── api_thread_pool_manager.py
│   │   ├── thread_config.py
│   │   └── thread_exceptions.py
│   ├── factories/                  # Factory pattern implementations
│   │   ├── __init__.py
│   │   ├── question_generator_factory.py
│   │   ├── mock_generator_factory.py
│   │   ├── prompt_generator_factory.py
│   │   └── api_client_factory.py
│   ├── mock/                       # Mock generation logic
│   │   ├── __init__.py
│   │   ├── unified_mock_generator.py
│   │   ├── paper_builder.py
│   │   └── section_builder.py
│   └── instructions/               # System instruction management
│       ├── __init__.py
│       ├── instruction_manager.py
│       ├── instruction_loader.py
│       └── template_processor.py
├── generators/                     # Question generator implementations
│   ├── __init__.py
│   ├── base/                       # Base generator classes
│   │   ├── __init__.py
│   │   ├── base_question_generator.py
│   │   └── base_section_generator.py
│   ├── quants/                     # Quantitative question generators
│   │   ├── __init__.py
│   │   ├── data_sufficiency_generator.py
│   │   ├── simple_question_generator.py
│   │   ├── numeric_entry_generator.py
│   │   └── parent_child_generator.py
│   ├── verbal/                     # Verbal question generators
│   │   ├── __init__.py
│   │   ├── reading_comprehension_generator.py
│   │   ├── critical_reasoning_generator.py
│   │   ├── sentence_equivalence_generator.py
│   │   └── text_completion_generator.py
│   └── integrated_reasoning/       # IR question generators (GMAT only)
│       ├── __init__.py
│       ├── graphic_interpretation_generator.py
│       ├── table_analysis_generator.py
│       ├── two_part_analysis_generator.py
│       └── multi_source_reasoning_generator.py
├── prompts/                        # Prompt generation system
│   ├── __init__.py
│   ├── base/
│   │   ├── __init__.py
│   │   └── base_prompt_generator.py
│   ├── gmat/
│   │   ├── __init__.py
│   │   ├── gmat_quants_prompts.py
│   │   ├── gmat_verbal_prompts.py
│   │   └── gmat_ir_prompts.py
│   └── gre/
│       ├── __init__.py
│       ├── gre_quants_prompts.py
│       └── gre_verbal_prompts.py
├── config/                         # Configuration management
│   ├── __init__.py
│   ├── base_config.py              # Base configuration class
│   ├── system_config.py            # System-wide settings
│   ├── exams/                      # Exam-specific configurations
│   │   ├── __init__.py
│   │   ├── gmat_config.py
│   │   └── gre_config.py
│   ├── generators/                 # Generator configurations
│   │   ├── gmat_generators.json
│   │   └── gre_generators.json
│   └── sections/                   # Section configurations
│       ├── quants_config.json
│       ├── verbal_config.json
│       └── ir_config.json
├── system_instructions/            # Centralized instruction templates
│   ├── templates/                  # Template files
│   │   ├── data_sufficiency.txt.template
│   │   ├── simple_question.txt.template
│   │   ├── reading_comprehension.txt.template
│   │   ├── critical_reasoning.txt.template
│   │   └── integrated_reasoning.txt.template
│   ├── gmat/
│   │   └── customizations.json     # GMAT-specific template variables
│   └── gre/
│       └── customizations.json     # GRE-specific template variables
├── data/                           # Static data and resources
│   ├── combinations/               # Question combination tracking
│   │   ├── gmat_combinations.json
│   │   └── gre_combinations.json
│   ├── allocation/                 # Component allocation data
│   │   └── component_allocation.json
│   └── reference/                  # Reference data and examples
│       ├── sample_questions/
│       └── expected_formats/
├── tests/                          # Comprehensive test suite
│   ├── __init__.py
│   ├── unit/                       # Unit tests
│   │   ├── test_generators/
│   │   ├── test_components/
│   │   └── test_utilities/
│   ├── integration/                # Integration tests
│   │   ├── test_mock_generation/
│   │   └── test_end_to_end/
│   ├── fixtures/                   # Test data and fixtures
│   └── conftest.py                 # Pytest configuration
├── scripts/                        # Utility and maintenance scripts
│   ├── migration/                  # Migration utilities
│   │   ├── cleanup_old_files.py
│   │   ├── validate_migration.py
│   │   └── performance_benchmark.py
│   ├── validation/                 # Validation scripts
│   └── maintenance/                # Maintenance tools
├── logs/                           # Application logs
├── papers/                         # Generated papers
│   ├── gmat/
│   └── gre/
└── docs/                           # Documentation
    ├── api/                        # API documentation
    ├── architecture/               # Architecture diagrams and docs
    └── examples/                   # Usage examples
```

---

## Naming Conventions

### 1. Python Files and Modules

**Pattern**: `snake_case.py`

```python
# ✅ Good
question_generator_factory.py
api_thread_pool_manager.py
unified_mock_generator.py

# ❌ Bad
QuestionGeneratorFactory.py
apiThreadPoolManager.py
UnifiedMockGenerator.py
```

### 2. Classes

**Pattern**: `PascalCase`

```python
# ✅ Good
class QuestionGeneratorFactory:
class APIThreadPoolManager:
class UnifiedMockGenerator:

# ❌ Bad
class question_generator_factory:
class apiThreadPoolManager:
class unified_mock_generator:
```

### 3. Functions and Methods

**Pattern**: `snake_case`

```python
# ✅ Good
def generate_question():
def process_api_response():
def validate_question_format():

# ❌ Bad
def GenerateQuestion():
def processApiResponse():
def validateQuestionFormat():
```

### 4. Variables

**Pattern**: `snake_case`

```python
# ✅ Good
question_data = {}
api_response_time = 1.5
max_retry_attempts = 3

# ❌ Bad
questionData = {}
apiResponseTime = 1.5
maxRetryAttempts = 3
```

### 5. Constants

**Pattern**: `SCREAMING_SNAKE_CASE`

```python
# ✅ Good
MAX_API_RETRIES = 3
DEFAULT_DIFFICULTY_LEVEL = 1
SUPPORTED_QUESTION_TYPES = ["DS", "MCQ", "RC"]

# ❌ Bad
max_api_retries = 3
defaultDifficultyLevel = 1
supportedQuestionTypes = ["DS", "MCQ", "RC"]
```

### 6. Enums

**Pattern**: `PascalCase` for class, `SCREAMING_SNAKE_CASE` for values

```python
# ✅ Good
class ExamType(Enum):
    GMAT = "gmat"
    GRE = "gre"

class QuestionType(Enum):
    DATA_SUFFICIENCY = "data_sufficiency"
    MULTIPLE_CHOICE = "multiple_choice"
    READING_COMPREHENSION = "reading_comprehension"

# ❌ Bad
class examType(Enum):
    gmat = "gmat"
    gre = "gre"
```

### 7. Directories

**Pattern**: `snake_case`

```
# ✅ Good
question_generators/
system_instructions/
api_thread_pool/

# ❌ Bad
QuestionGenerators/
systemInstructions/
apiThreadPool/
```

### 8. Configuration Files

**Pattern**: `snake_case.json` or `snake_case.yaml`

```
# ✅ Good
gmat_generators.json
system_config.yaml
question_types.json

# ❌ Bad
GMATGenerators.json
systemConfig.yaml
questionTypes.json
```

### 9. Interface/Protocol Names

**Pattern**: `I` prefix + `PascalCase`

```python
# ✅ Good
class IQuestionGenerator(Protocol):
class IMockGenerator(Protocol):
class IAPIClient(Protocol):

# ❌ Bad
class QuestionGeneratorInterface:
class MockGeneratorProtocol:
```

### 10. Exception Classes

**Pattern**: `PascalCase` + `Exception` suffix

```python
# ✅ Good
class QuestionGenerationException(Exception):
class APIRateLimitException(Exception):
class ValidationException(Exception):

# ❌ Bad
class QuestionGenerationError:
class APIRateLimit:
class ValidateError:
```

---

## Code Organization

### 1. Import Order

```python
# Standard library imports
import json
import os
import time
from typing import List, Dict, Optional

# Third-party imports
from dotenv import load_dotenv
from google import genai
from prisma import Prisma

# Local imports - core components first
from core.enums.exam_types import ExamType
from core.enums.question_types import QuestionType
from core.interfaces.question_generator import IQuestionGenerator
from core.utilities.json_utils import refine_response

# Local imports - specific implementations
from generators.base.base_question_generator import BaseQuestionGenerator
```

### 2. Class Structure Template

```python
class ExampleQuestionGenerator(BaseQuestionGenerator):
    """
    Brief description of the class purpose.
    
    Attributes:
        attribute_name (type): Description of attribute
        
    Example:
        generator = ExampleQuestionGenerator(config)
        question = generator.generate_question(prompt)
    """
    
    # Class-level constants
    DEFAULT_RETRIES: int = 3
    SUPPORTED_TYPES: List[str] = ["type1", "type2"]
    
    def __init__(self, config: ExampleConfig) -> None:
        """Initialize the generator with configuration."""
        super().__init__(config)
        self._private_attribute: Optional[str] = None
        self.public_attribute: int = 0
    
    # Public methods first
    def generate_question(self, prompt: str) -> Dict[str, Any]:
        """
        Generate a question based on the provided prompt.
        
        Args:
            prompt: The input prompt for question generation
            
        Returns:
            Dictionary containing the generated question data
            
        Raises:
            QuestionGenerationException: If generation fails
        """
        pass
    
    # Private methods last
    def _validate_prompt(self, prompt: str) -> bool:
        """Validate the input prompt format."""
        pass
    
    def _process_response(self, response: str) -> Dict[str, Any]:
        """Process the API response into structured data."""
        pass
```

### 3. Function Structure Template

```python
def process_question_data(
    question_data: Dict[str, Any],
    exam_type: ExamType,
    difficulty: DifficultyLevel = DifficultyLevel.MEDIUM
) -> ProcessedQuestion:
    """
    Process raw question data into a standardized format.
    
    Args:
        question_data: Raw question data from API
        exam_type: Target exam type (GMAT or GRE)
        difficulty: Question difficulty level (default: MEDIUM)
        
    Returns:
        ProcessedQuestion object with standardized format
        
    Raises:
        ValidationException: If question data is invalid
        ProcessingException: If processing fails
    """
    # Input validation
    if not question_data:
        raise ValidationException("Question data cannot be empty")
    
    # Main processing logic
    processed = ProcessedQuestion()
    
    # Return statement
    return processed
```

---

## Type Safety and Enums

### 1. Comprehensive Type Hints

```python
from typing import Dict, List, Optional, Union, Tuple, Any, Protocol
from typing_extensions import TypedDict

# Use TypedDict for structured dictionaries
class QuestionData(TypedDict):
    question_id: str
    content: Dict[str, Any]
    difficulty: int
    exam_type: str

# Type hints for all function signatures
def generate_questions(
    prompts: List[str],
    exam_type: ExamType,
    difficulty_range: Tuple[int, int]
) -> List[QuestionData]:
    pass
```

### 2. Enum Definitions

#### core/enums/exam_types.py
```python
from enum import Enum, auto

class ExamType(Enum):
    """Supported examination types."""
    GMAT = "gmat"
    GRE = "gre"
    
    @classmethod
    def from_string(cls, value: str) -> 'ExamType':
        """Create ExamType from string value."""
        for exam_type in cls:
            if exam_type.value.lower() == value.lower():
                return exam_type
        raise ValueError(f"Invalid exam type: {value}")
```

#### core/enums/section_types.py
```python
class SectionType(Enum):
    """Examination section types."""
    QUANTITATIVE = "quantitative"
    VERBAL = "verbal"
    INTEGRATED_REASONING = "integrated_reasoning"
    ANALYTICAL_WRITING = "analytical_writing"
```

#### core/enums/question_types.py
```python
class QuestionType(Enum):
    """Question type classifications."""
    # Quantitative types
    DATA_SUFFICIENCY = "data_sufficiency"
    PROBLEM_SOLVING = "problem_solving"
    NUMERIC_ENTRY = "numeric_entry"
    
    # Verbal types
    READING_COMPREHENSION = "reading_comprehension"
    CRITICAL_REASONING = "critical_reasoning"
    SENTENCE_CORRECTION = "sentence_correction"
    TEXT_COMPLETION = "text_completion"
    SENTENCE_EQUIVALENCE = "sentence_equivalence"
    
    # Integrated Reasoning types (GMAT only)
    GRAPHIC_INTERPRETATION = "graphic_interpretation"
    TABLE_ANALYSIS = "table_analysis"
    TWO_PART_ANALYSIS = "two_part_analysis"
    MULTI_SOURCE_REASONING = "multi_source_reasoning"
```

#### core/enums/difficulty_levels.py
```python
class DifficultyLevel(Enum):
    """Question difficulty levels."""
    VERY_EASY = 1
    EASY = 2
    MEDIUM = 3
    HARD = 4
    VERY_HARD = 5
    
    @property
    def display_name(self) -> str:
        """Human-readable difficulty name."""
        return self.name.replace('_', ' ').title()
```

### 3. Protocol Definitions

```python
from typing import Protocol, runtime_checkable

@runtime_checkable
class IQuestionGenerator(Protocol):
    """Protocol for question generators."""
    
    def generate_question(self, prompt: str) -> Dict[str, Any]:
        """Generate a single question."""
        ...
    
    def validate_output(self, question_data: Dict[str, Any]) -> bool:
        """Validate generated question format."""
        ...
```

---

## Error Handling

### 1. Exception Hierarchy

```python
# core/exceptions/base_exceptions.py
class QGenBaseException(Exception):
    """Base exception for all QGen-related errors."""
    
    def __init__(self, message: str, error_code: Optional[str] = None):
        super().__init__(message)
        self.error_code = error_code
        self.timestamp = time.time()

# core/exceptions/generation_exceptions.py
class QuestionGenerationException(QGenBaseException):
    """Raised when question generation fails."""
    pass

class PromptValidationException(QGenBaseException):
    """Raised when prompt validation fails."""
    pass

# core/exceptions/api_exceptions.py
class APIException(QGenBaseException):
    """Base class for API-related exceptions."""
    pass

class APIRateLimitException(APIException):
    """Raised when API rate limit is exceeded."""
    pass
```

### 2. Error Handling Patterns

```python
import logging
from typing import Optional

logger = logging.getLogger(__name__)

def safe_question_generation(
    generator: IQuestionGenerator,
    prompt: str,
    max_retries: int = 3
) -> Optional[Dict[str, Any]]:
    """
    Safely generate a question with retry logic.
    
    Args:
        generator: Question generator instance
        prompt: Generation prompt
        max_retries: Maximum retry attempts
        
    Returns:
        Generated question data or None if all attempts fail
    """
    for attempt in range(max_retries):
        try:
            question_data = generator.generate_question(prompt)
            if generator.validate_output(question_data):
                return question_data
            else:
                logger.warning(f"Invalid output on attempt {attempt + 1}")
                
        except APIRateLimitException as e:
            logger.warning(f"Rate limit hit on attempt {attempt + 1}: {e}")
            time.sleep(2 ** attempt)  # Exponential backoff
            
        except QuestionGenerationException as e:
            logger.error(f"Generation failed on attempt {attempt + 1}: {e}")
            if attempt == max_retries - 1:
                raise
                
        except Exception as e:
            logger.error(f"Unexpected error on attempt {attempt + 1}: {e}")
            if attempt == max_retries - 1:
                raise QuestionGenerationException(f"Generation failed after {max_retries} attempts") from e
    
    return None
```

---

## Configuration Management

### 1. Configuration Class Structure

```python
# config/base_config.py
from abc import ABC, abstractmethod
from typing import Dict, Any
from dataclasses import dataclass
from core.enums.exam_types import ExamType

@dataclass
class BaseConfig(ABC):
    """Base configuration class."""
    exam_type: ExamType
    debug_mode: bool = False
    log_level: str = "INFO"
    
    @abstractmethod
    def validate(self) -> bool:
        """Validate configuration values."""
        pass
    
    @classmethod
    @abstractmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'BaseConfig':
        """Create config from dictionary."""
        pass
```

### 2. Exam-Specific Configuration

```python
# config/exams/gmat_config.py
@dataclass
class GMATConfig(BaseConfig):
    """GMAT-specific configuration."""
    include_integrated_reasoning: bool = True
    ir_questions_per_section: int = 12
    quant_questions_per_section: int = 31
    verbal_questions_per_section: int = 36
    
    def validate(self) -> bool:
        """Validate GMAT configuration."""
        return (
            self.ir_questions_per_section > 0 and
            self.quant_questions_per_section > 0 and
            self.verbal_questions_per_section > 0
        )
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'GMATConfig':
        """Create GMAT config from dictionary."""
        return cls(
            exam_type=ExamType.GMAT,
            include_integrated_reasoning=config_dict.get('include_ir', True),
            ir_questions_per_section=config_dict.get('ir_questions', 12),
            quant_questions_per_section=config_dict.get('quant_questions', 31),
            verbal_questions_per_section=config_dict.get('verbal_questions', 36),
            debug_mode=config_dict.get('debug', False),
            log_level=config_dict.get('log_level', 'INFO')
        )
```

### 3. Configuration Loading

```python
# config/config_loader.py
import json
import os
from typing import Dict, Any, Type
from core.enums.exam_types import ExamType
from .base_config import BaseConfig
from .exams.gmat_config import GMATConfig
from .exams.gre_config import GREConfig

class ConfigLoader:
    """Centralized configuration loading."""
    
    CONFIG_CLASSES: Dict[ExamType, Type[BaseConfig]] = {
        ExamType.GMAT: GMATConfig,
        ExamType.GRE: GREConfig
    }
    
    @classmethod
    def load_exam_config(cls, exam_type: ExamType, config_path: Optional[str] = None) -> BaseConfig:
        """Load configuration for specific exam type."""
        if config_path is None:
            config_path = f"config/exams/{exam_type.value}_config.json"
        
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Config file not found: {config_path}")
        
        with open(config_path, 'r') as f:
            config_dict = json.load(f)
        
        config_class = cls.CONFIG_CLASSES[exam_type]
        config = config_class.from_dict(config_dict)
        
        if not config.validate():
            raise ValueError(f"Invalid configuration for {exam_type.value}")
        
        return config
```

---

## Testing Standards

### 1. Test File Organization

```
tests/
├── unit/
│   ├── test_generators/
│   │   ├── test_base_generator.py
│   │   ├── test_data_sufficiency_generator.py
│   │   └── test_question_factory.py
│   ├── test_utilities/
│   │   ├── test_json_utils.py
│   │   └── test_validation_utils.py
│   └── test_enums/
│       ├── test_exam_types.py
│       └── test_question_types.py
├── integration/
│   ├── test_end_to_end_generation.py
│   └── test_mock_paper_creation.py
└── fixtures/
    ├── sample_prompts.json
    └── expected_outputs.json
```

### 2. Test Naming Conventions

```python
# test_data_sufficiency_generator.py
class TestDataSufficiencyGenerator:
    """Test suite for DataSufficiencyGenerator."""
    
    def test_generate_question_with_valid_prompt_should_return_valid_data(self):
        """Test question generation with valid prompt returns properly formatted data."""
        pass
    
    def test_generate_question_with_invalid_prompt_should_raise_exception(self):
        """Test question generation with invalid prompt raises ValidationException."""
        pass
    
    def test_validate_output_with_correct_format_should_return_true(self):
        """Test output validation returns True for correctly formatted questions."""
        pass
```

### 3. Test Fixtures and Utilities

```python
# tests/conftest.py
import pytest
from typing import Dict, Any
from core.enums.exam_types import ExamType
from config.exams.gmat_config import GMATConfig

@pytest.fixture
def gmat_config() -> GMATConfig:
    """Provide GMAT configuration for testing."""
    return GMATConfig(
        exam_type=ExamType.GMAT,
        debug_mode=True,
        log_level="DEBUG"
    )

@pytest.fixture
def sample_prompt() -> str:
    """Provide sample prompt for testing."""
    return "DS - <Arithmetic> - <Logical Reasoning> - <difficulty_level: 3>"

@pytest.fixture
def expected_question_format() -> Dict[str, Any]:
    """Provide expected question format for validation."""
    return {
        "type": "Data Sufficiency",
        "content": {"passages": str, "statements": list},
        "question": str,
        "options": list,
        "answer": str,
        "solution": str,
        "difficulty": int,
        "tags": list
    }
```

---

## Documentation Standards

### 1. Docstring Format

Use Google-style docstrings consistently:

```python
def generate_question_batch(
    prompts: List[str],
    exam_type: ExamType,
    batch_size: int = 10
) -> List[Dict[str, Any]]:
    """
    Generate multiple questions in batches for improved performance.
    
    This function processes prompts in batches to optimize API usage and
    improve generation speed while maintaining quality standards.
    
    Args:
        prompts: List of question generation prompts
        exam_type: Target examination type (GMAT or GRE)
        batch_size: Number of questions to generate per batch (default: 10)
        
    Returns:
        List of generated question dictionaries, each containing:
            - type: Question type classification
            - content: Question content and data
            - difficulty: Numerical difficulty level (1-5)
            - metadata: Additional question metadata
    
    Raises:
        ValidationException: If any prompt is invalid or malformed
        APIException: If API communication fails
        QuestionGenerationException: If question generation fails
        
    Example:
        >>> prompts = ["DS - <Arithmetic> - <difficulty_level: 3>"]
        >>> questions = generate_question_batch(prompts, ExamType.GMAT)
        >>> len(questions)
        1
        >>> questions[0]["type"]
        "Data Sufficiency"
    
    Note:
        Batch processing may take longer for initial requests due to
        API connection establishment, but subsequent batches will be faster.
    """
    pass
```

### 2. Module Documentation

```python
"""
Question Generator Factory Module.

This module provides factory classes and utilities for creating question
generators based on exam type and question type specifications. It implements
the Factory Method pattern to enable dynamic generator creation and registration.

Classes:
    QuestionGeneratorFactory: Main factory for creating generators
    GeneratorRegistry: Registry for managing available generators
    
Functions:
    register_generator: Register a new generator type
    get_available_types: Get list of supported question types
    
Example:
    >>> from generators.factory import QuestionGeneratorFactory
    >>> from core.enums import ExamType, QuestionType
    >>> factory = QuestionGeneratorFactory()
    >>> generator = factory.create_generator(
    ...     exam_type=ExamType.GMAT,
    ...     question_type=QuestionType.DATA_SUFFICIENCY
    ... )
    >>> question = generator.generate_question("sample prompt")
"""
```

---

## Import Organization

### 1. Import Order and Grouping

```python
"""
Standard import organization following PEP 8 guidelines.
"""

# 1. Standard library imports (alphabetical)
import json
import logging
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Dict, List, Optional, Protocol, Tuple, Union

# 2. Third-party imports (alphabetical)
import pytest
from dotenv import load_dotenv
from google import genai
from prisma import Prisma

# 3. Local imports - Core components (hierarchical)
from core.enums.exam_types import ExamType
from core.enums.question_types import QuestionType
from core.enums.section_types import SectionType
from core.exceptions.generation_exceptions import QuestionGenerationException
from core.interfaces.question_generator import IQuestionGenerator
from core.utilities.json_utils import refine_response
from core.utilities.validation_utils import validate_prompt

# 4. Local imports - Application components (hierarchical)
from config.base_config import BaseConfig
from config.exams.gmat_config import GMATConfig
from generators.base.base_question_generator import BaseQuestionGenerator
from generators.quants.data_sufficiency_generator import DataSufficiencyGenerator
```

### 2. Conditional Imports

```python
# Use conditional imports for optional dependencies
try:
    from typing_extensions import TypedDict
except ImportError:
    from typing import Dict as TypedDict

# Use TYPE_CHECKING for imports only needed for type hints
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from generators.base.base_question_generator import BaseQuestionGenerator
```

---

## Performance and Optimization Guidelines

### 1. Lazy Loading

```python
class QuestionGeneratorFactory:
    """Factory with lazy loading of generators."""
    
    def __init__(self):
        self._generators: Dict[str, Type[IQuestionGenerator]] = {}
        self._loaded: bool = False
    
    def _load_generators(self):
        """Load generators only when needed."""
        if not self._loaded:
            # Load generator classes
            self._generators = self._discover_generators()
            self._loaded = True
    
    def create_generator(self, generator_type: str) -> IQuestionGenerator:
        """Create generator with lazy loading."""
        self._load_generators()
        return self._generators[generator_type]()
```

### 2. Caching Strategies

```python
from functools import lru_cache
from typing import Dict, Any

class InstructionManager:
    """Manage system instructions with caching."""
    
    @lru_cache(maxsize=128)
    def load_instruction(self, instruction_type: str, exam_type: ExamType) -> str:
        """Load instruction with LRU caching."""
        instruction_path = self._get_instruction_path(instruction_type, exam_type)
        with open(instruction_path, 'r') as f:
            return f.read()
    
    def clear_cache(self):
        """Clear instruction cache."""
        self.load_instruction.cache_clear()
```

### 3. Resource Management

```python
from contextlib import contextmanager
from typing import Generator

@contextmanager
def api_client_context(api_key: str) -> Generator[genai.Client, None, None]:
    """Context manager for API client lifecycle."""
    client = genai.Client(api_key=api_key)
    try:
        yield client
    finally:
        # Cleanup resources
        client.close()

# Usage
def generate_with_managed_client(prompt: str) -> Dict[str, Any]:
    """Generate question with proper resource management."""
    with api_client_context(get_api_key()) as client:
        return client.generate(prompt)
```

---

## Logging Standards

### 1. Structured Logging

```python
import logging
import json
from typing import Dict, Any

class StructuredLogger:
    """Structured logging utility."""
    
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
    
    def log_generation_start(self, prompt: str, exam_type: ExamType):
        """Log question generation start."""
        self.logger.info(
            "Question generation started",
            extra={
                "event": "generation_start",
                "prompt": prompt,
                "exam_type": exam_type.value,
                "timestamp": time.time()
            }
        )
    
    def log_generation_success(self, question_data: Dict[str, Any]):
        """Log successful question generation."""
        self.logger.info(
            "Question generation completed",
            extra={
                "event": "generation_success",
                "question_type": question_data.get("type"),
                "difficulty": question_data.get("difficulty"),
                "timestamp": time.time()
            }
        )
    
    def log_generation_error(self, error: Exception, context: Dict[str, Any]):
        """Log generation error with context."""
        self.logger.error(
            f"Question generation failed: {str(error)}",
            extra={
                "event": "generation_error",
                "error_type": type(error).__name__,
                "error_message": str(error),
                "context": context,
                "timestamp": time.time()
            },
            exc_info=True
        )
```

---

## Security Guidelines

### 1. API Key Management

```python
import os
from typing import Optional
from core.exceptions.api_exceptions import APIConfigurationException

class APIKeyManager:
    """Secure API key management."""
    
    @staticmethod
    def get_api_key(key_index: int) -> str:
        """Get API key by index with validation."""
        key_name = f"API_{key_index}"
        api_key = os.getenv(key_name)
        
        if not api_key:
            raise APIConfigurationException(f"API key {key_name} not found in environment")
        
        if not APIKeyManager._validate_key_format(api_key):
            raise APIConfigurationException(f"Invalid API key format for {key_name}")
        
        return api_key
    
    @staticmethod
    def _validate_key_format(api_key: str) -> bool:
        """Validate API key format."""
        # Implement key format validation
        return len(api_key) > 20 and api_key.startswith("AIza")
```

### 2. Input Sanitization

```python
import re
from typing import List

class InputSanitizer:
    """Input sanitization utilities."""
    
    ALLOWED_PROMPT_PATTERN = re.compile(r'^[a-zA-Z0-9\s\-<>:\[\],\.]+$')
    MAX_PROMPT_LENGTH = 1000
    
    @classmethod
    def sanitize_prompt(cls, prompt: str) -> str:
        """Sanitize question generation prompt."""
        if not prompt or len(prompt.strip()) == 0:
            raise ValidationException("Prompt cannot be empty")
        
        if len(prompt) > cls.MAX_PROMPT_LENGTH:
            raise ValidationException(f"Prompt too long (max {cls.MAX_PROMPT_LENGTH} chars)")
        
        if not cls.ALLOWED_PROMPT_PATTERN.match(prompt):
            raise ValidationException("Prompt contains invalid characters")
        
        return prompt.strip()
```

---

## Conclusion

This comprehensive code protocol ensures:

1. **Consistency**: Uniform naming and structure across all components
2. **Maintainability**: Clear organization and documentation standards
3. **Extensibility**: Easy addition of new exam types and question formats
4. **Type Safety**: Comprehensive use of type hints and enums
5. **Quality**: Robust error handling and testing standards
6. **Performance**: Optimization guidelines and best practices
7. **Security**: Secure handling of sensitive data and inputs

Following these protocols will result in a highly maintainable, scalable, and professional codebase that achieves 100% code reusability across GMAT and GRE question generation systems.