# GMAT/GRE Question Generation System - Migration Roadmap

## Executive Summary

This document outlines a comprehensive migration strategy to eliminate code duplication and establish 100% code reusability in the GMAT/GRE Question Generation System. The migration is designed in 7 sequential chunks, ensuring the codebase remains functional after each completion.

## Current Code Analysis

### Major Duplication Areas Identified

1. **APIThreadPoolManager Class**: 95% identical between GMAT/Mock.py and GRE/Mock.py
2. **Question Components**: `questionComponents.py` files are nearly identical across sections
3. **Question Generator Classes**: Similar structure and initialization patterns
4. **Mock Classes**: GMAT_Mock and GRE_Mock have identical threading and generation logic
5. **Prompt Generation Classes**: Similar patterns in Mock_prompts directories
6. **System Architecture**: Repeated folder structures and file organization
7. **Utility Functions**: JSON refinement, error handling, and API management

### Code Duplication Statistics
- **Estimated Duplicate Lines**: ~2,500 lines (40% of codebase)
- **Duplicate Files**: 15+ files with 80%+ similarity
- **Redundant Classes**: 8 major classes with identical functionality

## Migration Strategy

### Core Principles
1. **Backward Compatibility**: Ensure main.py remains runnable after each chunk
2. **Incremental Refactoring**: Small, testable changes with immediate benefits
3. **Type Safety**: Introduce comprehensive typing and enums
4. **Single Responsibility**: Each module handles one concern
5. **Configuration-Driven**: Use enums and config files instead of hardcoded values

---

## CHUNK 1: Foundation Layer and Core Infrastructure

**Estimated Time**: 3-4 hours  
**Risk Level**: Low  
**Dependencies**: None

### 1.1 Create Core Directory Structure
```
core/
├── __init__.py
├── enums/
│   ├── __init__.py
│   ├── exam_types.py          # GMAT, GRE enums
│   ├── section_types.py       # Quants, Verbal, IR enums
│   ├── question_types.py      # DS, MCQ, RC, etc.
│   └── difficulty_levels.py   # 1-5 difficulty enum
├── interfaces/
│   ├── __init__.py
│   ├── question_generator.py  # Abstract base class
│   ├── mock_generator.py      # Abstract mock class
│   └── prompt_generator.py    # Abstract prompt class
├── utilities/
│   ├── __init__.py
│   ├── json_utils.py         # Centralized JSON handling
│   ├── api_utils.py          # API key management
│   ├── file_utils.py         # File operations
│   └── validation_utils.py   # Input validation
└── config/
    ├── __init__.py
    ├── exam_config.py        # Exam-specific configurations
    └── system_config.py      # System-wide settings
```

### 1.2 Implement Core Enums
Create comprehensive enums to replace hardcoded strings and enable type safety.

**Files to Create:**
- `core/enums/exam_types.py`
- `core/enums/section_types.py`  
- `core/enums/question_types.py`
- `core/enums/difficulty_levels.py`

### 1.3 Extract Utility Functions
Move shared utility functions to centralized location.

**Priority Functions to Extract:**
- `refine_response()` from questionComponents.py files
- JSON validation and parsing functions
- Error handling utilities
- API key management functions

### 1.4 Create Abstract Interfaces
Define abstract base classes for question generators and mock generators.

### 1.5 Validation & Testing
- Ensure all imports work correctly
- Verify enum values match existing hardcoded values
- Test utility functions with existing data
- Confirm main.py still runs successfully

**Deliverables:**
- ✅ Core directory structure created
- ✅ All enums implemented with comprehensive coverage
- ✅ Utility functions extracted and tested
- ✅ Abstract interfaces defined
- ✅ main.py runs without errors

---

## CHUNK 2: Unified Question Components

**Estimated Time**: 4-5 hours  
**Risk Level**: Medium  
**Dependencies**: Chunk 1 completed

### 2.1 Consolidate questionComponents.py Files
Currently, GMAT and GRE have nearly identical questionComponents.py files across different sections.

**Approach:**
1. Create `core/components/question_components.py`
2. Merge all common functionality from existing files
3. Use enums to handle exam-specific differences
4. Maintain backward compatibility through adapters

### 2.2 Create Unified Question Component Classes
**Target Classes to Unify:**
- `DataSufficiencyQuestion` (currently in GMAT/Quants and GRE/Quants)
- `SimpleQuestion` (currently in multiple locations)
- `ParentChildQuestion` (currently in Verbal sections)
- Generic question processing classes

### 2.3 Implement Exam-Specific Adapters
Create adapter classes that translate between exam types while using the same core logic.

**Files to Create:**
- `core/components/question_components.py`
- `core/components/adapters/gmat_adapter.py`
- `core/components/adapters/gre_adapter.py`

### 2.4 Update Existing Generators
Modify existing question generator classes to use the new unified components.

**Files to Modify:**
- All `dataSufficiencyQuestionGeneration.py` files
- All `simpleQuestionGeneration.py` files
- All `parentChildQuestionGeneration.py` files

### 2.5 Validation & Testing
- Test each question type with both GMAT and GRE configurations
- Verify JSON output format remains unchanged
- Ensure all existing functionality is preserved
- Confirm main.py still generates papers correctly

**Deliverables:**
- ✅ Single unified question components file
- ✅ Exam-specific adapters implemented
- ✅ All generators updated to use new components
- ✅ Backward compatibility maintained
- ✅ Full test suite passes

---

## CHUNK 3: API Thread Pool Manager Unification

**Estimated Time**: 3-4 hours  
**Risk Level**: Medium  
**Dependencies**: Chunk 1 completed

### 3.1 Extract APIThreadPoolManager
Currently duplicated between GMAT/Mock.py and GRE/Mock.py with 95% identical code.

**Approach:**
1. Create `core/threading/api_thread_pool_manager.py`
2. Extract common functionality
3. Use configuration objects for exam-specific differences
4. Implement comprehensive error handling and logging

### 3.2 Enhance Thread Pool Manager
**Improvements to Implement:**
- Better error handling and recovery
- Configurable retry mechanisms
- Enhanced logging and monitoring
- Resource cleanup and management
- Type hints and documentation

### 3.3 Create Threading Configuration
**Files to Create:**
- `core/threading/api_thread_pool_manager.py`
- `core/threading/thread_config.py`
- `core/threading/exceptions.py`

### 3.4 Update Mock Classes
Modify GMAT_Mock and GRE_Mock classes to use the unified thread pool manager.

**Files to Modify:**
- `GMAT/Mock.py`
- `GRE/Mock.py`

### 3.5 Validation & Testing
- Test concurrent question generation
- Verify API rate limiting works correctly
- Ensure proper resource cleanup
- Test error recovery mechanisms
- Confirm paper generation still works

**Deliverables:**
- ✅ Unified APIThreadPoolManager implemented
- ✅ Enhanced error handling and logging
- ✅ Configuration-based customization
- ✅ Both GMAT and GRE Mock classes updated
- ✅ Threading functionality verified

---

## CHUNK 4: Question Generator Factory Pattern

**Estimated Time**: 5-6 hours  
**Risk Level**: Medium-High  
**Dependencies**: Chunks 1 & 2 completed

### 4.1 Implement Generator Factory Pattern
Replace the current GENERATOR_MAP approach with a comprehensive factory pattern.

**Benefits:**
- Dynamic generator registration
- Type-safe generator creation
- Easier addition of new question types
- Centralized configuration management

### 4.2 Create Generator Registry
**Files to Create:**
- `core/factories/question_generator_factory.py`
- `core/factories/generator_registry.py`
- `core/factories/generator_config.py`

### 4.3 Unify Question Generator Base Classes
All question generators currently follow similar patterns:
- Constructor with global_state, lock, api_IDX, prompt
- generate_question() method
- Similar error handling

**Approach:**
1. Create abstract base class `BaseQuestionGenerator`
2. Implement common functionality
3. Define standard interface for all generators
4. Use template method pattern for customization

### 4.4 Refactor Existing Generators
**Target Generators to Refactor:**
- GMAT: Q_DS_gen, Q_S_gen, V_PC_gen, V_S_gen, GI_gen, TPA_gen, TA_gen, MSR_gen
- GRE: Q_DS_gen, Q_NE_gen, Q_PC_gen, Q_S_gen, V_PC_gen, V_S_gen

### 4.5 Create Generator Configuration Files
Replace hardcoded generator mappings with configuration files.

**Files to Create:**
- `config/generators/gmat_generators.json`
- `config/generators/gre_generators.json`

### 4.6 Validation & Testing
- Test factory pattern with all question types
- Verify generator registration works correctly
- Ensure dynamic loading of generators
- Test error handling in factory methods
- Confirm all existing question types still work

**Deliverables:**
- ✅ Factory pattern implemented
- ✅ Generator registry functional
- ✅ All generators inherit from base class
- ✅ Configuration-driven generator loading
- ✅ Type safety throughout generator system

---

## CHUNK 5: Mock Class Unification and Prompt System

**Estimated Time**: 4-5 hours  
**Risk Level**: Medium  
**Dependencies**: Chunks 1, 3, 4 completed

### 5.1 Create Unified Mock Generator
GMAT_Mock and GRE_Mock classes are nearly identical except for:
- Different prompt generators (no Integrated Reasoning for GRE)
- Different generator mappings
- Minor differences in paper structure

**Approach:**
1. Create `core/mock/unified_mock_generator.py`
2. Use composition pattern with exam-specific configurations
3. Implement strategy pattern for different exam requirements

### 5.2 Unify Prompt Generation System
**Current Prompt Classes to Unify:**
- `GMAT.Mock_prompts.Verbal`
- `GMAT.Mock_prompts.Quants`  
- `GMAT.Mock_prompts.Integrated_Reasoning`
- `GRE.Mock_prompts.Verbal`
- `GRE.Mock_prompts.Quants`

**Files to Create:**
- `core/prompts/prompt_generator_factory.py`
- `core/prompts/base_prompt_generator.py`
- `core/prompts/verbal_prompt_generator.py`
- `core/prompts/quants_prompt_generator.py`
- `core/prompts/ir_prompt_generator.py`

### 5.3 Create Exam Configuration System
**Files to Create:**
- `config/exams/gmat_config.py`
- `config/exams/gre_config.py`
- `config/exams/base_exam_config.py`

### 5.4 Implement Paper Structure Unification
Create a unified paper structure that works for both GMAT and GRE.

### 5.5 Update Main Entry Point
Modify main.py to use the new unified system while maintaining the same external interface.

### 5.6 Validation & Testing
- Test paper generation for both GMAT and GRE
- Verify prompt generation works correctly
- Ensure paper structure is maintained
- Test with different difficulty levels
- Confirm database registration still works

**Deliverables:**
- ✅ Unified mock generator implemented
- ✅ Prompt generation system unified
- ✅ Configuration-driven exam definitions
- ✅ Paper structure standardized
- ✅ main.py updated and functional

---

## CHUNK 6: System Instructions and Configuration Management

**Estimated Time**: 3-4 hours  
**Risk Level**: Low-Medium  
**Dependencies**: Chunks 1, 2, 4 completed

### 6.1 Centralize System Instructions
Currently scattered across multiple directories:
- `GMAT/*/System_instructions/`
- `GRE/*/System_Instructions/`

**Approach:**
1. Create `system_instructions/` directory at root level
2. Organize by question type rather than exam type
3. Use template system with exam-specific parameters
4. Implement instruction loading and caching

### 6.2 Create Instruction Management System
**Files to Create:**
- `core/instructions/instruction_manager.py`
- `core/instructions/instruction_loader.py`
- `core/instructions/template_processor.py`

### 6.3 Implement Template System
Create templates that can be customized for different exams:
```
system_instructions/
├── templates/
│   ├── data_sufficiency.txt.template
│   ├── simple_question.txt.template
│   ├── parent_child.txt.template
│   └── integrated_reasoning.txt.template
├── gmat/
│   └── customizations.json
└── gre/
    └── customizations.json
```

### 6.4 Create Configuration Schema
Define schemas for:
- Question type configurations
- Difficulty level mappings
- Output format specifications
- Validation rules

### 6.5 Validation & Testing
- Test instruction loading for all question types
- Verify template processing works correctly
- Ensure all existing instructions are preserved
- Test configuration validation
- Confirm generators use new instruction system

**Deliverables:**
- ✅ Centralized instruction management
- ✅ Template system implemented
- ✅ Configuration schemas defined
- ✅ All generators updated to use new system
- ✅ Instruction loading optimized and cached

---

## CHUNK 7: Final Integration and Optimization

**Estimated Time**: 4-5 hours  
**Risk Level**: Low  
**Dependencies**: All previous chunks completed

### 7.1 Code Cleanup and Optimization
- Remove all duplicate files and code
- Optimize imports and dependencies
- Clean up unused functions and classes
- Standardize error handling throughout

### 7.2 Create Migration Utilities
**Files to Create:**
- `migration/cleanup_old_files.py`
- `migration/validate_migration.py`
- `migration/performance_benchmark.py`

### 7.3 Update Documentation
- Update CLAUDE.md with new architecture
- Create API documentation for new components
- Update configuration guides
- Create troubleshooting guides

### 7.4 Implement Comprehensive Testing
- Create integration tests for full system
- Add performance tests for threading
- Implement validation tests for all question types
- Create regression tests for paper generation

### 7.5 Performance Optimization
- Optimize JSON processing
- Improve memory usage in threading
- Cache frequently used configurations
- Optimize database queries

### 7.6 Final Validation
- Run full end-to-end tests
- Generate sample papers for both exams
- Verify all functionality preserved
- Check performance improvements
- Validate database compatibility

**Deliverables:**
- ✅ All duplicate code removed
- ✅ Performance optimized
- ✅ Comprehensive test suite
- ✅ Updated documentation
- ✅ Migration utilities created
- ✅ 100% code reusability achieved

---

## Migration Benefits

### Quantitative Improvements
- **Code Reduction**: ~40% reduction in total lines of code
- **Maintenance Effort**: ~60% reduction in duplicate maintenance
- **Bug Risk**: ~50% reduction through unified code paths
- **Development Speed**: ~30% faster for new features

### Qualitative Improvements
- **Type Safety**: Comprehensive enum usage and type hints
- **Modularity**: Clear separation of concerns
- **Testability**: Improved unit and integration testing
- **Extensibility**: Easy addition of new exam types and question formats
- **Configuration Management**: Centralized, version-controlled settings
- **Error Handling**: Consistent error handling and logging
- **Performance**: Optimized resource usage and caching

## Risk Mitigation

### Chunk-by-Chunk Validation
Each chunk includes comprehensive testing to ensure:
- main.py continues to work
- Generated papers maintain same format
- Database integration remains functional
- API calls work correctly

### Rollback Strategy
Each chunk creates a git branch with:
- Clear commit messages
- Functional checkpoints
- Migration scripts
- Rollback procedures

### Testing Strategy
- Unit tests for all new components
- Integration tests for each chunk
- End-to-end tests after each chunk
- Performance regression tests

## Timeline Estimate

**Total Estimated Time**: 26-32 hours
- Chunk 1: 3-4 hours
- Chunk 2: 4-5 hours  
- Chunk 3: 3-4 hours
- Chunk 4: 5-6 hours
- Chunk 5: 4-5 hours
- Chunk 6: 3-4 hours
- Chunk 7: 4-5 hours

**Recommended Schedule**: 1-2 chunks per week for 4-6 weeks

## Success Criteria

### Technical Criteria
- ✅ Zero duplicate code across GMAT and GRE systems
- ✅ Single source of truth for all shared functionality
- ✅ Comprehensive type safety with enums and interfaces
- ✅ 100% backward compatibility maintained
- ✅ Performance improvements or maintained
- ✅ Enhanced error handling and logging

### Functional Criteria
- ✅ main.py generates papers identically to current system
- ✅ All question types function correctly
- ✅ Database integration preserved
- ✅ Threading and API management improved
- ✅ Configuration system implemented
- ✅ Comprehensive test coverage

### Maintainability Criteria
- ✅ Adding new exam types requires minimal code changes
- ✅ Adding new question types follows standard patterns
- ✅ Configuration changes don't require code modifications
- ✅ Clear documentation and architecture guides
- ✅ Standardized development patterns throughout

## Future Enhancements Enabled

This migration creates a foundation for future improvements:

1. **Multi-Exam Support**: Easy addition of SAT, LSAT, etc.
2. **Dynamic Question Types**: Runtime registration of new question formats
3. **A/B Testing**: Configuration-driven testing of different approaches
4. **Microservices**: Clear boundaries for service extraction
5. **API Layer**: RESTful API on top of unified architecture
6. **Caching Layer**: Intelligent caching of generated content
7. **Analytics**: Comprehensive metrics and monitoring
8. **Scalability**: Horizontal scaling of question generation

## Conclusion

This migration roadmap provides a comprehensive path to achieving 100% code reusability while maintaining system functionality. The chunk-based approach ensures minimal risk and continuous validation, while the final architecture provides a solid foundation for future enhancements and scalability.