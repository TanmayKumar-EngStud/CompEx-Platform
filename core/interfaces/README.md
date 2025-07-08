# 🔌 Core Interfaces System

This directory contains the foundational interface definitions and protocols that establish the contracts for all major components in the QGen question generation system. These interfaces ensure consistency, enable polymorphism, and provide clear separation of concerns across different exam types and question generators.

---

## 📊 Data Flow and System Architecture

**🎯 Purpose**: This module defines the protocol-based architecture where all major system components must implement specific interfaces. Data flows through three main interaction layers: prompt generation → question generation → mock paper assembly.

**Flow**: Interface definitions → Concrete implementations → System coordination → Generated output

The interfaces establish a hierarchical flow:
1. **Prompt Layer**: `IPromptGenerator` creates standardized prompts for question generation
2. **Question Layer**: `IQuestionGenerator` transforms prompts into complete questions 
3. **Paper Layer**: `IMockGenerator` orchestrates multiple question generators to build complete exam papers

---

## 🗂️ Interface Files Overview

### `question_generator.py` 🧩

**🎯 Purpose**: Defines the core interfaces for question generation components, establishing contracts for single questions, multi-part questions, and specialized content generation.

**📊 Interface Hierarchy**:
- `IQuestionGenerator` - Core question generation protocol
- `BaseQuestionGenerator` - Abstract base implementation with common functionality
- `IMultiPartQuestionGenerator` - Protocol for parent-child question types
- `ISpecializedQuestionGenerator` - Protocol for questions requiring visual content

**🔗 System Integration**:
- **📲 Implemented By**: All concrete question generators in `GMAT/` and `GRE/` directories
- **➡️ Used By**: `core/factories/question_generator_factory.py` for polymorphic generator creation
- **🔄 Coordination**: `core/components/adapters/` provide exam-specific implementations

### `mock_generator.py` 📄

**🎯 Purpose**: Defines interfaces for generating complete exam papers and managing section-level question distribution and coordination.

**📊 Interface Hierarchy**:
- `IMockGenerator` - Core mock paper generation protocol
- `BaseMockGenerator` - Abstract base implementation with paper structure management
- `IPromptGenerator` - Protocol for prompt generation (also defined here for mock context)
- `BasePromptGenerator` - Abstract base for prompt generators

**🔗 System Integration**:
- **📲 Implemented By**: `GMAT/Mock.py`, `GRE/Mock.py`, `core/mock/unified_mock_generator.py`
- **➡️ Uses**: `IQuestionGenerator` implementations for actual question creation
- **🔄 Coordination**: `core/mock/paper_builder.py` and `core/mock/section_builder.py` orchestrate paper assembly

### `prompt_generator.py` 🎯

**🎯 Purpose**: Defines interfaces for creating varied, high-quality prompts that drive question generation across different exam types and sections.

**📊 Interface Hierarchy**:
- `IPromptGenerator` - Core prompt generation protocol  
- `BasePromptGenerator` - Abstract base with combination tracking and variety enforcement

**🔗 System Integration**:
- **📲 Implemented By**: Exam-specific prompt generators in `core/prompts/gmat/` and `core/prompts/gre/`
- **➡️ Used By**: Mock generators for generating diverse question prompts
- **🔄 Coordination**: `core/prompts/prompt_generator_factory.py` manages prompt generator selection

---

## 🔄 Interface Interaction Patterns

### **Protocol-Based Design**
All interfaces use Python's `@runtime_checkable` protocols, enabling:
- **Duck Typing**: Components can implement interfaces without inheritance
- **Type Safety**: Static type checking ensures interface compliance
- **Flexibility**: Easy addition of new implementations without modifying existing code

### **Abstract Base Classes**
Base implementations provide:
- **Common Functionality**: Shared utilities like retry logic, API management, validation
- **Template Methods**: Standard workflows that concrete classes customize
- **Error Handling**: Consistent error reporting and recovery mechanisms

### **Composition Over Inheritance**
Interfaces enable:
- **Modular Design**: Components can be mixed and matched based on requirements
- **Testability**: Easy mocking and unit testing of individual components
- **Scalability**: New exam types can be added by implementing existing interfaces

---

## 🏗️ Implementation Requirements

### **Question Generator Interface (`IQuestionGenerator`)**
**Required Methods**:
- `generate_question(prompt: str) → Optional[Dict[str, Any]]` - Core generation method
- `validate_output(question_data: Dict[str, Any]) → bool` - Output validation
- `get_supported_types() → List[QuestionType]` - Supported question types
- `get_exam_type() → ExamType` - Target exam type

**Data Contract**:
- Input: Standardized prompt strings with format: `"TYPE - <Topic> - <Skill> - <difficulty_level: N>"`
- Output: Complete question dictionaries with required keys: `type`, `content`, `question`, `answer`, `solution`, `difficulty`, `tags`

### **Mock Generator Interface (`IMockGenerator`)**
**Required Methods**:
- `generate_paper(difficulty: DifficultyLevel, is_mock: bool) → Optional[Dict[str, Any]]` - Complete paper generation
- `generate_section(section_type: SectionType, difficulty: DifficultyLevel, question_count: int) → Optional[List[Dict[str, Any]]]` - Section generation
- `validate_paper(paper_data: Dict[str, Any]) → bool` - Paper validation
- `get_supported_sections() → List[SectionType]` - Supported sections

**Data Contract**:
- Input: Difficulty levels (1-5), section types, question counts
- Output: Complete papers with metadata, sections, and question arrays

### **Prompt Generator Interface (`IPromptGenerator`)**
**Required Methods**:
- `generate_prompts(section_type: SectionType, difficulty: DifficultyLevel, question_count: int) → List[str]` - Bulk prompt generation
- `generate_single_prompt(question_type: QuestionType, difficulty: DifficultyLevel, topic: Optional[str], skill: Optional[str]) → str` - Single prompt
- `get_supported_sections() → List[SectionType]` - Supported sections

**Data Contract**:
- Input: Section types, difficulty levels, topic/skill preferences
- Output: Standardized prompt strings ready for question generation

---

## 🧪 Interface Testing and Validation

### **Runtime Checking**
All protocols use `@runtime_checkable` for dynamic validation:
```python
if isinstance(generator, IQuestionGenerator):
    # Safe to use generator methods
```

### **Type Hints Integration**
Full type hint support enables:
- Static analysis with mypy/pyright
- IDE auto-completion and error detection
- Clear API documentation through types

### **Validation Mechanisms**
Each interface defines validation methods that:
- Check required method implementations
- Validate input/output contracts
- Ensure data format compliance
- Enable quality assurance testing

---

## 🔗 External Dependencies and Integration Points

**Internal Dependencies**:
- `core.enums.*` - Type definitions for exam types, question types, difficulty levels
- `core.utilities.validation_utils` - Input validation and sanitization
- `core.utilities.logging_utils` - Structured logging for interface operations

**Implementation Locations**:
- **Question Generators**: `GMAT/*/files/*.py`, `GRE/*/files/*.py`
- **Mock Generators**: `GMAT/Mock.py`, `GRE/Mock.py`, `core/mock/unified_mock_generator.py`
- **Prompt Generators**: `core/prompts/gmat/*.py`, `core/prompts/gre/*.py`

**Factory Integration**:
- `core/factories/question_generator_factory.py` - Dynamic generator creation
- `core/factories/generator_registry.py` - Interface registration and discovery
- `core/prompts/prompt_generator_factory.py` - Prompt generator selection

This interface system provides the foundation for a scalable, maintainable, and extensible question generation architecture that can accommodate new exam types and question formats while maintaining consistency and quality.