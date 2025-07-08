# Template Usage Guide - GMAT/GRE Question Generation System

## Overview

This guide explains how to use the philosophy-driven template system for generating GMAT and GRE questions. The system is designed to create realistic, educationally sound standardized test questions that properly assess cognitive skills.

## Template Architecture

### Directory Structure

```
system_instructions/
├── templates/
│   ├── !Main Instructions/           # Core philosophy templates
│   │   ├── generic.txt.template     # Universal testing principles
│   │   ├── data_sufficiency.txt.template
│   │   ├── problem_solving.txt.template
│   │   ├── reading_comprehension.txt.template
│   │   ├── critical_reasoning.txt.template
│   │   ├── graphic_interpretation.txt.template
│   │   ├── table_analysis.txt.template
│   │   ├── two_part_analysis.txt.template
│   │   ├── multi_source_reasoning.txt.template
│   │   ├── numeric_entry.txt.template
│   │   ├── text_completion.txt.template
│   │   ├── sentence_equivalence.txt.template
│   │   ├── mcq_single.txt.template
│   │   └── mcq_multiple.txt.template
│   ├── 0-questionMetadata/          # Content structure templates
│   ├── 1-questionText/              # Question text templates
│   ├── 2-questionTitle/             # Question title templates
│   ├── 3-questionOptions/           # Option generation templates
│   ├── 4-questionSolution/          # Solution templates
│   └── 5-questionAnswer/            # Answer format templates
├── graph_styles.json               # Graph format definitions
├── gmat/customizations.json        # GMAT-specific customizations
└── gre/customizations.json         # GRE-specific customizations
```

## Template Types

### 1. Main Instructions Templates

These templates define the core philosophy and approach for each question type:

#### Key Features:
- **Cognitive Testing Philosophy**: How to create questions that test specific skills
- **Trap Generation Strategy**: How to create realistic distractors
- **Component Relationships**: How different question components work together
- **Real Exam Alignment**: Standards for matching actual exam conditions

#### Usage Example:
```python
from core.instructions.instruction_manager import InstructionManager

manager = InstructionManager()
instruction = manager.get_main_instruction("data_sufficiency", "gmat")
```

### 2. Question Component Templates

These templates handle specific parts of question generation:

#### 0-questionMetadata Templates:
- `passage.txt.template`: Reading comprehension passages
- `graph.txt.template`: Charts and graphs with dynamic population
- `parent_stimulus.txt.template`: Shared content for parent-child questions
- `multi_source.txt.template`: Multiple data sources
- `specialized_table.txt.template`: Data tables

#### 1-questionText Templates:
- `generic.txt.template`: Standard question text
- `data_sufficiency.txt.template`: DS-specific format
- `numeric_entry.txt.template`: Open-ended numerical questions
- `child_question.txt.template`: Sub-questions for parent-child format

#### 3-questionOptions Templates:
- `generic.txt.template`: Standard multiple choice
- `dichotomous_choice.txt.template`: True/False, Yes/No, etc.
- `sentence_equivalence.txt.template`: GRE sentence equivalence format
- `text_completion.txt.template`: GRE text completion format

#### 4-questionSolution Templates:
- `generic.txt.template`: Standard solution format
- `data_sufficiency.txt.template`: DS-specific solution approach

#### 5-questionAnswer Templates:
- `generic.txt.template`: Standard answer format
- `data_sufficiency.txt.template`: DS answer options
- `numeric_entry.txt.template`: Numerical answer format

## Dynamic Template Processing

### Template Variables

Templates use placeholder variables that are populated dynamically:

#### Common Variables:
- `{exam_type}`: "GMAT" or "GRE"
- `{question_type}`: Specific question type (e.g., "Data Sufficiency")
- `{difficulty_level}`: 1-5 difficulty scale
- `{focused_skill}`: The specific skill being tested

#### Special Variables:

**Graph Template (`graph.txt.template`)**:
- `{graphs_array}`: Populated with exact graph formats from `graph_styles.json`

**Dichotomous Choice Template (`dichotomous_choice.txt.template`)**:
- `{type_A}`, `{type_B}`, `{type_C}`: Dynamically set based on question type
  - "Would Help/Would Not Help"
  - "Yes/No"
  - "True/False"
  - "Correct/Incorrect"

**Text Completion Template (`text_completion.txt.template`)**:
- `{{#if_TC-1}}`: Single blank instructions
- `{{#if_TC-2}}`: Double blank instructions
- `{{#if_TC-3}}`: Triple blank instructions

**Multi-Source Template (`multi_source.txt.template`)**:
- `{content}`: Populated with content formats from metadata configurations

### Template Processing Flow

1. **Template Selection**: Based on question type and exam format
2. **Variable Population**: Dynamic variables filled from configuration files
3. **Conditional Processing**: Conditional blocks processed based on question specifics
4. **Validation**: Output validated against schema requirements
5. **Instruction Generation**: Final instruction sent to AI model

## Using Templates in Code

### Basic Usage

```python
from core.instructions.instruction_manager import InstructionManager

# Initialize the instruction manager
manager = InstructionManager()

# Get a complete instruction for a question type
instruction = manager.build_instruction(
    exam_type="gmat",
    question_type="data_sufficiency",
    difficulty_level=3,
    focused_skill="logical_reasoning",
    prompt_details={"topic": "arithmetic", "content_type": "graph"}
)
```

### Advanced Usage with Custom Variables

```python
# For graph questions
graph_instruction = manager.build_instruction(
    exam_type="gmat",
    question_type="graphic_interpretation",
    difficulty_level=4,
    focused_skill="data_interpretation",
    prompt_details={
        "graph_types": ["pie_chart", "bar_chart"],
        "topic": "economics"
    }
)

# For dichotomous choice questions
dichotomous_instruction = manager.build_instruction(
    exam_type="gmat",
    question_type="table_analysis",
    difficulty_level=2,
    focused_skill="data_analysis",
    prompt_details={
        "choice_type": "true_false",
        "table_complexity": "medium"
    }
)
```

## Configuration Files

### Graph Styles (`graph_styles.json`)
Defines exact JSON formats for different graph types:
```json
{
  "pie_chart": {
    "json_format": {...},
    "description": "Pie chart for categorical data"
  },
  "bar_chart": {
    "json_format": {...},
    "description": "Bar chart for comparative data"
  }
}
```

### Exam Customizations (`gmat/customizations.json`, `gre/customizations.json`)
Exam-specific settings and variations:
```json
{
  "data_sufficiency": {
    "standard_options": ["A", "B", "C", "D", "E"],
    "option_descriptions": {...}
  },
  "difficulty_mappings": {...}
}
```

## Best Practices

### 1. Template Maintenance
- Keep templates focused on single responsibilities
- Use descriptive variable names
- Include comments for complex logic
- Regular validation against real exam standards

### 2. Variable Management
- Validate all variables before template processing
- Use default values for optional variables
- Log missing variables for debugging
- Maintain variable naming consistency

### 3. Content Quality
- Ensure trap options are educationally sound
- Maintain cognitive testing principles
- Regular review of generated content
- Alignment with official exam standards

### 4. Performance Optimization
- Cache frequently used templates
- Minimize template parsing overhead
- Use lazy loading for large templates
- Monitor template processing times

## Troubleshooting

### Common Issues

1. **Missing Variables**: Check that all required variables are provided
2. **Template Not Found**: Verify template file paths and naming
3. **Invalid JSON**: Validate template output against schemas
4. **Performance Issues**: Check template caching and loading strategies

### Debugging Tools

```python
# Enable debug logging
import logging
logging.getLogger('core.instructions').setLevel(logging.DEBUG)

# Validate template before use
from config.schemas.instruction_schemas import validate_template
validate_template(template_content)

# Check template variables
manager.get_template_variables("data_sufficiency")
```

## Testing Templates

### Unit Testing
```python
def test_data_sufficiency_template():
    manager = InstructionManager()
    instruction = manager.build_instruction(
        exam_type="gmat",
        question_type="data_sufficiency",
        difficulty_level=3,
        focused_skill="logical_reasoning"
    )
    
    assert "Data Sufficiency" in instruction
    assert "trap" in instruction.lower()
    assert "cognitive" in instruction.lower()
```

### Integration Testing
```python
def test_full_question_generation():
    # Test complete question generation pipeline
    generator = DataSufficiencyGenerator()
    question = generator.generate_question(
        prompt="DS - Arithmetic - Logical Reasoning - difficulty_level: 3"
    )
    
    # Validate output format
    assert question["type"] == "Data Sufficiency"
    assert len(question["options"]) == 5
    assert question["difficulty"] == 3
```

## Migration Guide

### From Legacy System
1. **Backup existing instructions**: Copy to `older_system_instructions_for_reference/`
2. **Update generator classes**: Modify to use new template system
3. **Test thoroughly**: Validate output quality and format
4. **Monitor performance**: Ensure no degradation in generation speed

### Template Updates
1. **Version control**: Track template changes
2. **Validation**: Test against existing question sets
3. **Documentation**: Update usage guide with changes
4. **Communication**: Notify developers of breaking changes

## Support and Maintenance

### Regular Tasks
- Review template effectiveness quarterly
- Update based on exam changes
- Monitor generation quality metrics
- Optimize performance bottlenecks

### Contact Information
- Technical issues: Check `CLAUDE.md` for system architecture
- Template bugs: Review `config/schemas/` for validation rules
- Performance issues: Monitor `core/instructions/` components
- Documentation: Update this guide with changes

---

This template system represents a philosophy-driven approach to creating realistic, educationally sound standardized test questions that properly assess cognitive skills while incorporating trap-based option generation to mirror real exam conditions.