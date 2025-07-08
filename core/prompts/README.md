# 🎯 Prompt Generation System

This directory contains the comprehensive prompt generation system that creates diverse, high-quality prompts for question generation across different exam types and sections. The system ensures variety, appropriate difficulty distribution, and exam-specific formatting requirements through a factory-based architecture with specialized generators.

---

## 📊 Data Flow and System Architecture

**🎯 Purpose**: This module provides intelligent prompt generation that creates varied, well-structured input prompts for question generators, ensuring proper topic distribution, difficulty targeting, and format compliance across GMAT and GRE exams.

**Flow**: Exam configuration → Section analysis → Topic/skill selection → Difficulty distribution → Variety enforcement → Formatted prompt generation → Question generator input

The prompt generation system follows a hierarchical factory pattern:
1. **Factory Level**: `PromptGeneratorFactory` selects appropriate generators based on exam and section type
2. **Base Level**: `BasePromptGenerator` provides common functionality and abstract interface
3. **Specialized Level**: Exam-specific generators implement section-specific logic and content pools

---

## 🗂️ System Components Overview

### `prompt_generator_factory.py` 🏭

**🎯 Purpose**: Provides factory pattern implementation for dynamic prompt generator creation based on exam type and section type combinations.

**📊 Component Architecture**:
- `PromptGeneratorFactory` - Main factory class with generator registry and creation logic
- Dynamic generator registration and mapping system
- Exception handling for unsupported exam/section combinations

**🔗 System Integration**:
- **📲 Called By**: `core/mock/unified_mock_generator.py:UnifiedMockGenerator._create_prompt_generator()`
- **📲 Called By**: Mock generation systems requiring prompt creation
- **➡️ Creates**: Exam-specific prompt generator instances from `gmat/` and `gre/` subdirectories
- **🔄 Coordination**: Manages the selection and configuration of specialized prompt generators

**📊 Generator Registration Flow**:
```
Factory Initialization → Generator Discovery → Registration Mapping → Runtime Selection → Instance Creation
```

### `base/` 📚

**🎯 Purpose**: Contains the abstract base class and common functionality shared across all prompt generators, providing standardized interfaces and utility methods.

**📊 Component Architecture**:
- `BasePromptGenerator` - Abstract base class defining prompt generation contract
- Common utilities for combination tracking, difficulty distribution, and variety enforcement
- Shared logging and configuration management

**🔗 System Integration**:
- **📲 Extended By**: All exam-specific prompt generators in `gmat/` and `gre/` subdirectories
- **➡️ Uses**: `core.utilities.file_utils` for combination data persistence
- **➡️ Uses**: `core.utilities.logging_utils` for structured logging
- **🔄 Coordination**: Provides template methods that specialized generators customize

**📊 Base Functionality Flow**:
```
Configuration Loading → Combination Tracking Setup → Difficulty Pool Creation → Topic/Skill Selection → Template Generation
```

### `gmat/` 🦁

**🎯 Purpose**: Contains GMAT-specific prompt generators that handle the unique requirements, question types, and content areas specific to GMAT exam sections.

**📊 Component Architecture**:
- `GMATQuantsPrompts` - Quantitative section prompts (Data Sufficiency, Problem Solving)
- `GMATVerbalPrompts` - Verbal section prompts (Reading Comprehension, Critical Reasoning)  
- `GMATIRPrompts` - Integrated Reasoning prompts (GI, TA, TPA, MSR)

**🔗 System Integration**:
- **📲 Created By**: `PromptGeneratorFactory` for GMAT exam requests
- **➡️ Generates**: Formatted prompts for GMAT-specific question generators
- **🔄 Coordination**: Implements GMAT-specific topic pools, difficulty distributions, and prompt formats

**📊 GMAT-Specific Processing**:
```
GMAT Configuration → Section Requirements → Question Type Distribution → Topic Pool Selection → GMAT Format Generation
```

### `gre/` 🦉

**🎯 Purpose**: Contains GRE-specific prompt generators that handle the unique requirements, question types, and content areas specific to GRE exam sections.

**📊 Component Architecture**:
- `GREQuantsPrompts` - Quantitative section prompts (Multiple Choice, Numeric Entry, Quantitative Comparison)
- `GREVerbalPrompts` - Verbal section prompts (Reading Comprehension, Text Completion, Sentence Equivalence)

**🔗 System Integration**:
- **📲 Created By**: `PromptGeneratorFactory` for GRE exam requests  
- **➡️ Generates**: Formatted prompts for GRE-specific question generators
- **🔄 Coordination**: Implements GRE-specific topic pools, difficulty distributions, and prompt formats

**📊 GRE-Specific Processing**:
```
GRE Configuration → Section Requirements → Question Type Distribution → Topic Pool Selection → GRE Format Generation
```

---

## 🔄 Prompt Generation Workflow

### **Topic and Skill Selection**
1. **Pool Loading**: Each generator loads exam-specific topic and skill pools
2. **Combination Tracking**: System tracks used topic/skill combinations to ensure variety
3. **Distribution Management**: Ensures balanced distribution across different content areas
4. **Rotation Logic**: Automatically rotates through available combinations to prevent repetition

### **Difficulty Distribution**
- **Target Distribution**: Each generator implements exam-specific difficulty distributions
- **Adaptive Selection**: Difficulty selection adapts based on overall mock exam difficulty level
- **Quality Assurance**: Validates that generated prompts match target difficulty requirements
- **Calibration**: Continuous calibration based on generation success rates

### **Format Standardization**
- **Prompt Templates**: Standardized prompt format: `"TYPE - <Topic> - <Skill> - <difficulty_level: N>"`
- **Parameter Injection**: Dynamic injection of exam-specific parameters and constraints
- **Validation**: Format validation to ensure compatibility with question generators
- **Extension Support**: Extensible format for adding custom parameters and metadata

---

## 🎨 Exam-Specific Specializations

### **GMAT Prompt Characteristics**
- **Question Types**: Data Sufficiency (DS), Problem Solving (PS), Critical Reasoning (CR), Reading Comprehension (RC)
- **Integrated Reasoning**: Specialized prompts for GI, TA, TPA, MSR question types
- **Topic Distribution**: Business-focused content with quantitative and verbal reasoning emphasis
- **Difficulty Scaling**: Five-level difficulty system with adaptive distribution

### **GRE Prompt Characteristics**  
- **Question Types**: Multiple Choice, Numeric Entry (NE), Quantitative Comparison, Text Completion (TC), Sentence Equivalence (SE)
- **Academic Focus**: Graduate-level academic content across diverse disciplines
- **Adaptive Elements**: Support for adaptive testing difficulty adjustment
- **Format Variations**: Multiple prompt formats for different question presentation styles

### **Content Pool Management**
- **Topic Categorization**: Hierarchical organization of topics by subject area and complexity
- **Skill Mapping**: Mapping of cognitive skills to question types and content areas
- **Dynamic Loading**: Runtime loading of content pools based on exam and section requirements
- **Extensibility**: Easy addition of new topics and skills through configuration

---

## 🔧 Variety and Quality Enforcement

### **Combination Tracking**
- **Usage Monitoring**: Tracks which topic/skill combinations have been used recently
- **Rotation Enforcement**: Ensures all available combinations are used before repetition
- **Reset Logic**: Automatic reset of tracking when all combinations exhausted
- **Persistence**: Saves combination usage state between generation sessions

### **Quality Metrics**
- **Prompt Validation**: Validates generated prompts against format requirements
- **Content Balance**: Ensures balanced distribution across content areas
- **Difficulty Accuracy**: Verifies that prompts generate questions at target difficulty
- **Success Rate Monitoring**: Tracks prompt generation success rates for optimization

### **Error Handling and Fallbacks**
- **Graceful Degradation**: Falls back to basic prompts when specialized generation fails
- **Retry Logic**: Automatic retry with alternative parameters for failed prompts
- **Logging Integration**: Comprehensive logging of generation issues and recovery actions
- **Quality Assurance**: Multiple validation layers to ensure prompt quality

---

## 🔗 External Dependencies and Integration Points

**Internal Dependencies**:
- `core.enums.*` - Type definitions for exams, sections, question types, and difficulty levels
- `core.utilities.file_utils` - File operations for combination data persistence
- `core.utilities.logging_utils` - Structured logging for prompt generation tracking
- `core.exceptions.*` - Specialized exceptions for prompt generation failures

**Integration Points**:
- **Question Generators**: Generated prompts feed directly into question generation pipeline
- **Mock Generation**: Integrated with mock paper generation for prompt coordination
- **Configuration System**: Uses exam configuration for prompt parameter customization
- **Testing Framework**: Provides hooks for prompt quality testing and validation

**External Configuration**:
- **Content Files**: JSON files containing topic pools, skill mappings, and combination data
- **Difficulty Mappings**: Configuration files defining difficulty distributions per exam type
- **Format Templates**: Template files for prompt format standardization
- **Quality Thresholds**: Configuration of quality metrics and acceptance criteria

This prompt generation system ensures that question generators receive high-quality, varied input prompts that result in diverse, appropriate exam questions while maintaining consistency with standardized test requirements and formats.