# 📄 Mock Paper Generation System

This directory contains the unified mock exam paper generation system that coordinates the creation of complete GMAT and GRE exam papers. The system orchestrates question generation, section building, and paper assembly through a modular, thread-safe architecture.

---

## 📊 Data Flow and System Architecture

**🎯 Purpose**: This module provides a comprehensive mock paper generation pipeline that coordinates multiple question generators to produce complete, properly structured exam papers with accurate timing, difficulty distribution, and format compliance.

**Flow**: Paper configuration → Section planning → Threaded question generation → Section assembly → Paper compilation → Validation & output

The mock generation system follows a three-tier architecture:
1. **Paper Level**: `MockPaperBuilder` orchestrates overall paper structure and metadata
2. **Section Level**: `MockSectionBuilder` manages individual section construction and question organization  
3. **Coordination Level**: `UnifiedMockGenerator` provides the unified interface and threading coordination

---

## 🗂️ System Components Overview

### `paper_builder.py` 📋

**🎯 Purpose**: Provides fluent builder interface for constructing complete exam papers with proper structure, metadata management, and format validation.

**📊 Component Architecture**:
- `PaperMetadata` - Dataclass for paper-level metadata tracking
- `SectionMetadata` - Dataclass for section-level performance tracking  
- `MockPaperBuilder` - Main builder class with fluent interface

**🔗 System Integration**:
- **📲 Used By**: `UnifiedMockGenerator.generate_mock_paper()` for paper assembly
- **➡️ Uses**: Section data from `MockSectionBuilder` for content integration
- **🔄 Coordination**: Aggregates sections into final paper format with comprehensive metadata

**📊 Data Processing Flow**:
```
Exam Configuration → Paper Builder → Section Integration → Metadata Calculation → Format Validation → Output Generation
```

### `section_builder.py` 🔧

**🎯 Purpose**: Handles individual section construction with proper question organization, timing estimates, difficulty distribution, and section-specific formatting requirements.

**📊 Component Architecture**:
- `QuestionInfo` - Dataclass for individual question metadata and timing
- `SectionConfig` - Dataclass for section configuration and constraints
- `MockSectionBuilder` - Builder class for section assembly and organization

**🔗 System Integration**:
- **📲 Used By**: `UnifiedMockGenerator._build_section()` for section construction
- **➡️ Uses**: Generated question data from various question generators
- **🔄 Coordination**: Organizes questions into section format and calculates section-level statistics

**📊 Data Processing Flow**:
```
Section Configuration → Question Collection → Difficulty Analysis → Timing Estimation → Organization → Section Output
```

### `unified_mock_generator.py` 🎯

**🎯 Purpose**: Provides the main unified interface for mock paper generation, coordinating thread management, generator selection, and overall paper assembly workflow for both GMAT and GRE exams.

**📊 Component Architecture**:
- `GeneratorClass` - Enum for legacy generator compatibility mapping
- `UnifiedMockGenerator` - Main coordinator class with exam-agnostic interface
- Exam-specific configuration integration with `GMATConfig` and `GREConfig`

**🔗 System Integration**:
- **📲 Called By**: `main.py:main()` for paper generation requests
- **📲 Called By**: `GMAT/Mock.py` and `GRE/Mock.py` for exam-specific generation
- **➡️ Uses**: `core.factories.question_generator_factory` for generator creation
- **➡️ Uses**: `core.threading.APIThreadPoolManager` for concurrent generation
- **➡️ Uses**: Both `MockPaperBuilder` and `MockSectionBuilder` for assembly

**📊 Data Processing Flow**:
```
Generation Request → Exam Configuration → Thread Pool Setup → Parallel Question Generation → Section Building → Paper Assembly → Quality Validation → Output
```

---

## 🔄 Inter-Component Data Flow

### **Paper Generation Workflow**
1. **Configuration Phase**: `UnifiedMockGenerator` receives exam type and difficulty parameters
2. **Planning Phase**: System determines question distribution per section based on exam configuration
3. **Generation Phase**: Parallel question generation using thread pools and API rotation
4. **Assembly Phase**: `MockSectionBuilder` organizes questions into sections
5. **Compilation Phase**: `MockPaperBuilder` assembles sections into complete paper
6. **Validation Phase**: Comprehensive validation of paper structure and content
7. **Output Phase**: Paper serialization and file output

### **Thread Coordination**
- **API Management**: Automatic API key rotation and rate limiting across threads
- **Load Balancing**: Dynamic distribution of generation tasks across available workers  
- **Error Handling**: Graceful degradation and retry logic for failed generations
- **Progress Tracking**: Real-time monitoring of generation progress and statistics

### **Quality Assurance**
- **Difficulty Distribution**: Ensures generated questions match target difficulty distribution
- **Content Validation**: Validates question format, completeness, and exam compliance
- **Timing Estimates**: Calculates realistic timing estimates based on question complexity
- **Format Compliance**: Ensures output matches exact exam format requirements

---

## 🏗️ Configuration Integration

### **Exam-Specific Configurations**
- **GMAT Configuration**: 187-minute total time with Integrated Reasoning, Quantitative (31Q), and Verbal (36Q) sections
- **GRE Configuration**: Variable time allocation with Quantitative and Verbal sections, adaptive difficulty

### **Question Type Mapping**
- **Generator Selection**: Automatic selection of appropriate generators based on question type and exam requirements
- **Legacy Compatibility**: Maintains compatibility with existing GMAT and GRE generator classes
- **Dynamic Loading**: Runtime loading of generator classes based on configuration

### **Threading Configuration**
- **Pool Management**: Configurable thread pool sizes based on system resources and API limitations
- **Rate Limiting**: Intelligent rate limiting to prevent API quota exhaustion
- **Resource Allocation**: Dynamic allocation of resources based on generation complexity

---

## 🔧 Builder Pattern Implementation

### **Fluent Interface Design**
Both builder classes use fluent interfaces enabling readable, chainable operations:
```python
paper = (MockPaperBuilder(ExamType.GMAT, difficulty=3)
    .add_section("quantitative", quant_questions)
    .add_section("verbal", verbal_questions)  
    .add_section("integrated_reasoning", ir_questions)
    .set_metadata(generation_metadata)
    .build())
```

### **Immutable Configuration**
- **State Management**: Builders maintain immutable configuration state during construction
- **Validation**: Continuous validation during building process to catch errors early
- **Error Handling**: Comprehensive error reporting with contextual information

### **Extensibility**
- **New Exam Types**: Easy addition of new exam types through configuration extension
- **Custom Sections**: Support for custom section types and configurations
- **Metadata Extension**: Flexible metadata system supporting custom tracking requirements

---

## 🔗 External Dependencies and Integration Points

**Internal Dependencies**:
- `core.enums.*` - Type definitions for exams, questions, sections, and difficulty levels
- `core.threading.*` - Thread pool management and API coordination
- `core.factories.*` - Dynamic generator creation and registry management
- `core.utilities.*` - Logging, validation, and file management utilities
- `config.exams.*` - Exam-specific configuration classes

**External Integration**:
- **Legacy Generators**: Maintains compatibility with existing GMAT and GRE generators
- **Database Storage**: Paper output compatible with database storage requirements
- **File Output**: JSON-formatted papers ready for file system storage
- **Testing Integration**: Comprehensive testing hooks for quality assurance

**Error Handling and Recovery**:
- **Graceful Degradation**: System continues operation even if some questions fail to generate
- **Retry Logic**: Automatic retry with exponential backoff for transient failures
- **Quality Monitoring**: Real-time monitoring of generation success rates and quality metrics
- **Fallback Mechanisms**: Alternative generation strategies when primary methods fail

This mock generation system provides a robust, scalable foundation for producing high-quality standardized test papers while maintaining the flexibility to accommodate different exam formats and requirements.