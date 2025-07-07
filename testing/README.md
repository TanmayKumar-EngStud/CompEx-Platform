# Testing Suite for GMAT/GRE Question Generation System

This directory contains comprehensive tests for Phase 4: Integration & Testing of the architectural improvisation roadmap.

## 📁 Test Files

### Core Integration Tests

- **`test_main_instructions.py`** - Tests the integration of !Main Instructions templates with the instruction management system
- **`test_dynamic_selection.py`** - Validates dynamic template selection based on question type, difficulty, and context
- **`test_generator_integration.py`** - Verifies that existing question generators work correctly with the new template system
- **`test_philosophical_alignment.py`** - Validates that the new system aligns with educational philosophy and trap-based option generation

### Test Runner

- **`run_all_tests.py`** - Comprehensive test runner that executes all tests with proper reporting

## 🚀 Running Tests

### Run Individual Tests

```bash
# From the testing directory
cd testing

# Test main instruction integration
python test_main_instructions.py

# Test dynamic template selection
python test_dynamic_selection.py

# Test generator integration
python test_generator_integration.py

# Test philosophical alignment
python test_philosophical_alignment.py
```

### Run All Tests

```bash
# From the testing directory
python run_all_tests.py
```

### Run from Project Root

```bash
# From project root
python testing/run_all_tests.py
```

## 📊 Test Coverage

### Phase 4 Checkpoints Validated

1. ✅ **Template Integration System** - Verifies !Main Instructions are properly loaded and processed
2. ✅ **Dynamic Template Selection** - Tests context-aware instruction optimization
3. ✅ **Template Rendering with Generators** - Ensures existing generators work with new system
4. ✅ **Philosophical Alignment** - Validates educational philosophy implementation

### Key Features Tested

- **Template Inheritance** - `{{GENERIC_PHILOSOPHY_TEMPLATE}}` and `{{0_GENERIC_PHILOSOPHY_TEMPLATE}}` processing
- **Conditional Processing** - Exam-specific (`{{#if_gmat}}`, `{{#if_gre}}`) and question-type conditionals
- **Dynamic Optimization** - Difficulty-based, prompt-based, and question-type specific enhancements
- **Generator Compatibility** - BaseQuestionGenerator integration with optimized instructions
- **Philosophy Implementation** - Trap-based option generation and educational alignment

## 🎯 Expected Test Results

### Successful Test Run Should Show:

- **100% Philosophical Alignment** across all question types
- **Template Inheritance Working** with generic philosophy found in specific templates
- **Conditional Processing Working** with exam-specific content properly applied
- **Generator Integration Success** with optimized features present in instructions
- **Dynamic Selection Active** with context-appropriate optimizations applied

### Test Validation Criteria

#### Main Instructions Test
- ✅ Generic philosophy template loads correctly
- ✅ Question-specific templates inherit from generic
- ✅ Full instruction concatenation works

#### Dynamic Selection Test
- ✅ High difficulty emphasis for difficulty 4-5
- ✅ Fundamental level emphasis for difficulty 1-2
- ✅ Visual data emphasis for graph/chart content
- ✅ Logical reasoning emphasis for relevant prompts
- ✅ Parent-child coordination for RC/MSR questions
- ✅ Exam-specific context (GMAT business, GRE academic)

#### Generator Integration Test
- ✅ Generators load optimized instructions automatically
- ✅ Individual mode instructions work correctly
- ✅ Philosophy features present in generator instructions

#### Philosophical Alignment Test
- ✅ Core principles: trap-based options, realistic assessment, skill focus
- ✅ Educational elements: mistake anticipation, authentic content
- ✅ Assessment validity: cognitive skill testing, student differentiation

## 🐛 Troubleshooting

### Common Issues

1. **Import Errors** - Ensure you're running from the correct directory
2. **API Key Warnings** - Tests use mock API keys, warnings are normal
3. **File Path Issues** - Tests add `..` to sys.path for project root access

### Debug Mode

Add `import pdb; pdb.set_trace()` to any test for debugging:

```python
def test_function():
    import pdb; pdb.set_trace()  # Debug breakpoint
    # Test code here
```

## 📈 Success Metrics

- **100% Test Pass Rate** - All tests should pass
- **100% Philosophical Alignment** - All question types show complete alignment
- **Template Inheritance Working** - Generic philosophy properly inherited
- **Conditional Processing Active** - Exam and question-type specific content applied
- **Generator Compatibility** - Existing generators work with new templates

## 🔄 Continuous Integration

These tests should be run:
- ✅ After any template system changes
- ✅ Before major releases
- ✅ When adding new question types
- ✅ When modifying instruction management

## 🎓 Educational Philosophy Validation

The tests specifically validate these core educational principles:

1. **Trap-Based Option Generation** - Options that catch common student mistakes
2. **Realistic Assessment** - Questions that mirror real exam conditions
3. **Skill-Focused Testing** - Questions that genuinely test intended cognitive skills
4. **Student Differentiation** - Ability to distinguish true understanding from superficial knowledge
5. **Mistake Anticipation** - Systematic identification and inclusion of common errors
6. **Authentic Content** - Exam-level language and complexity
7. **Educational Value** - Questions that teach through testing

---

## 🚀 Next Steps After Successful Testing

Once all tests pass:

1. **Phase 5: Documentation & Finalization** - Update system documentation
2. **Performance Optimization** - Template loading and caching improvements
3. **Production Deployment** - Roll out new template system to live generators

---

*For questions about testing or to report issues, refer to the main project documentation or create an issue in the project repository.*