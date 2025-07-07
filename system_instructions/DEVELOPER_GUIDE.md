# Developer Guide - Template Customization

## Overview

This guide provides developers with detailed instructions for customizing and extending the philosophy-driven template system for GMAT and GRE question generation.

## Template Development Workflow

### 1. Understanding Template Structure

#### Main Instructions Template Format
```
# {question_type} Question Generation - {exam_type}

## Core Philosophy
[Define the cognitive testing approach]

## Your Role
[Explain the AI model's responsibilities]

## Operational Modes
[Describe different generation modes]

## Component Relationships
[Explain how components work together]

## Trap Generation Strategy
[Detail how to create realistic distractors]

## Quality Standards
[Define standards for real exam alignment]
```

#### Component Template Format
```
# {component_name} Component

## Purpose
[Explain the component's role]

## Input Requirements
[List required variables and formats]

## Output Specification
[Define expected output structure]

## Dynamic Variables
[Document variable substitution rules]

## Validation Rules
[Specify validation requirements]
```

### 2. Creating New Templates

#### Step 1: Define Template Purpose
```python
# Document the template's specific role
PURPOSE = """
This template handles [specific functionality] for [question type]
questions in the [exam type] format.
"""

# Define required variables
REQUIRED_VARIABLES = [
    "exam_type",
    "question_type", 
    "difficulty_level",
    "focused_skill"
]

# Define optional variables
OPTIONAL_VARIABLES = [
    "topic",
    "content_type",
    "graph_types"
]
```

#### Step 2: Create Template File
```bash
# Create template in appropriate directory
touch system_instructions/templates/!Main\ Instructions/new_question_type.txt.template

# Or for component templates
touch system_instructions/templates/3-questionOptions/new_option_type.txt.template
```

#### Step 3: Implement Template Logic
```
# New Question Type Generation - {exam_type}

## Core Philosophy

You are generating {question_type} questions that test {focused_skill} at difficulty level {difficulty_level}.

### Cognitive Testing Approach
- Focus on realistic mistake patterns
- Create educationally sound trap options
- Test specific cognitive skills, not just content knowledge
- Align with official {exam_type} standards

### Question Generation Strategy
1. Analyze the focused skill requirements
2. Design scenarios that naturally lead to common mistakes
3. Create options that represent these mistake patterns
4. Ensure one clearly correct answer exists
5. Validate against difficulty level expectations

## Component Integration

### Required Components
- Question Metadata: {metadata_requirements}
- Question Text: {text_requirements}
- Question Options: {options_requirements}
- Question Solution: {solution_requirements}
- Question Answer: {answer_requirements}

### Dynamic Variables
{{#if_difficulty_1_2}}
- Use simpler vocabulary and concepts
- Limit complexity of calculations
- Focus on fundamental skill application
{{/if_difficulty_1_2}}

{{#if_difficulty_3_4}}
- Introduce multi-step reasoning
- Include moderate complexity
- Test skill application in context
{{/if_difficulty_3_4}}

{{#if_difficulty_5}}
- Require advanced reasoning
- Complex multi-step solutions
- Test skill mastery and application
{{/if_difficulty_5}}

## Quality Assurance

### Validation Checklist
- [ ] Tests the focused skill effectively
- [ ] Includes realistic trap options
- [ ] Matches difficulty level expectations
- [ ] Aligns with {exam_type} standards
- [ ] Follows proper JSON format

### Common Pitfalls to Avoid
- Generic trap options that don't reflect real mistakes
- Questions testing content knowledge over skills
- Difficulty misalignment with expectations
- Poor integration between components
```

### 3. Implementing Dynamic Variables

#### Variable Types

**Simple Variables**
```python
# String replacement
template_content = template_content.replace("{exam_type}", exam_type)
template_content = template_content.replace("{difficulty_level}", str(difficulty_level))
```

**Complex Variables**
```python
# Array population for graphs
if "{graphs_array}" in template_content:
    graph_formats = []
    for graph_type in requested_graphs:
        graph_format = load_graph_format(graph_type)
        graph_formats.append(graph_format)
    
    graphs_array = json.dumps(graph_formats, indent=2)
    template_content = template_content.replace("{graphs_array}", graphs_array)
```

**Conditional Variables**
```python
# Process conditional blocks
def process_conditional_blocks(template_content, conditions):
    for condition, is_active in conditions.items():
        if is_active:
            # Show content between conditional tags
            pattern = f"{{{{#{condition}}}}}(.*?){{{{/{condition}}}}}"
            template_content = re.sub(pattern, r'\1', template_content, flags=re.DOTALL)
        else:
            # Remove content between conditional tags
            pattern = f"{{{{#{condition}}}}}.*?{{{{/{condition}}}}}"
            template_content = re.sub(pattern, '', template_content, flags=re.DOTALL)
    
    return template_content
```

#### Advanced Variable Processing

**Multi-Source Content Population**
```python
def populate_multi_source_content(template_content, content_types):
    """Populate {content} variables with appropriate formats"""
    content_formats = []
    
    for content_type in content_types:
        if content_type == "graph":
            format_data = load_graph_format(requested_graph_type)
        elif content_type == "passage":
            format_data = load_passage_format(requested_passage_type)
        elif content_type == "table":
            format_data = load_table_format(requested_table_type)
        
        content_formats.append(format_data)
    
    # Replace {content} placeholders sequentially
    for i, content_format in enumerate(content_formats):
        template_content = template_content.replace(
            "{content}", 
            json.dumps(content_format, indent=2), 
            1  # Replace only first occurrence
        )
    
    return template_content
```

**Dichotomous Choice Processing**
```python
def process_dichotomous_choices(template_content, choice_type):
    """Process dichotomous choice variables"""
    choice_mappings = {
        "true_false": ["True", "False"],
        "yes_no": ["Yes", "No"],
        "would_help": ["Would Help", "Would Not Help"],
        "correct_incorrect": ["Correct", "Incorrect"]
    }
    
    choices = choice_mappings.get(choice_type, ["Option A", "Option B"])
    
    # Randomly distribute choices
    random.shuffle(choices)
    
    # Map to template variables
    template_content = template_content.replace("{type_A}", choices[0])
    template_content = template_content.replace("{type_B}", choices[1])
    template_content = template_content.replace("{type_C}", random.choice(choices))
    
    return template_content
```

### 4. Template Validation

#### Schema Validation
```python
from config.schemas.instruction_schemas import InstructionSchema
from config.schemas.validation_schemas import ValidationSchema

def validate_template(template_content, template_type):
    """Validate template against schema requirements"""
    try:
        # Parse template structure
        parsed_template = parse_template_structure(template_content)
        
        # Validate against schema
        schema = InstructionSchema.get_schema(template_type)
        ValidationSchema.validate(parsed_template, schema)
        
        return True, "Template validation successful"
    
    except ValidationError as e:
        return False, f"Template validation failed: {str(e)}"
```

#### Content Quality Validation
```python
def validate_template_quality(template_content, question_type):
    """Validate template content quality"""
    quality_checks = {
        "has_philosophy": "cognitive" in template_content.lower(),
        "has_trap_strategy": "trap" in template_content.lower(),
        "has_skill_focus": "skill" in template_content.lower(),
        "has_validation": "validation" in template_content.lower(),
        "has_components": "component" in template_content.lower()
    }
    
    failed_checks = [check for check, passed in quality_checks.items() if not passed]
    
    if failed_checks:
        raise ValueError(f"Template quality validation failed: {failed_checks}")
    
    return True
```

### 5. Integration with Instruction Manager

#### Registering New Templates
```python
# In core/instructions/instruction_manager.py

class InstructionManager:
    def __init__(self):
        self.template_registry = {
            # Main instructions
            "data_sufficiency": "!Main Instructions/data_sufficiency.txt.template",
            "new_question_type": "!Main Instructions/new_question_type.txt.template",
            
            # Component templates
            "generic_options": "3-questionOptions/generic.txt.template",
            "new_option_type": "3-questionOptions/new_option_type.txt.template"
        }
    
    def register_template(self, template_name, template_path):
        """Register a new template"""
        self.template_registry[template_name] = template_path
    
    def get_template_path(self, template_name):
        """Get template file path"""
        return self.template_registry.get(template_name)
```

#### Template Loading and Caching
```python
class TemplateCache:
    def __init__(self):
        self._cache = {}
        self._cache_timestamps = {}
    
    def get_template(self, template_path):
        """Get template with caching"""
        # Check if template is cached and up-to-date
        if template_path in self._cache:
            file_mtime = os.path.getmtime(template_path)
            cache_time = self._cache_timestamps.get(template_path, 0)
            
            if file_mtime <= cache_time:
                return self._cache[template_path]
        
        # Load template from file
        with open(template_path, 'r', encoding='utf-8') as file:
            template_content = file.read()
        
        # Cache template
        self._cache[template_path] = template_content
        self._cache_timestamps[template_path] = time.time()
        
        return template_content
```

### 6. Testing New Templates

#### Unit Tests
```python
import unittest
from core.instructions.instruction_manager import InstructionManager

class TestNewQuestionTypeTemplate(unittest.TestCase):
    def setUp(self):
        self.manager = InstructionManager()
    
    def test_template_loading(self):
        """Test template loads correctly"""
        template = self.manager.get_template("new_question_type")
        self.assertIsNotNone(template)
        self.assertIn("New Question Type", template)
    
    def test_variable_substitution(self):
        """Test variable substitution works"""
        instruction = self.manager.build_instruction(
            exam_type="gmat",
            question_type="new_question_type",
            difficulty_level=3,
            focused_skill="logical_reasoning"
        )
        
        self.assertIn("GMAT", instruction)
        self.assertIn("difficulty level 3", instruction)
        self.assertIn("logical_reasoning", instruction)
    
    def test_conditional_processing(self):
        """Test conditional blocks process correctly"""
        # Test difficulty 1-2 conditions
        low_difficulty = self.manager.build_instruction(
            exam_type="gmat",
            question_type="new_question_type",
            difficulty_level=1,
            focused_skill="basic_math"
        )
        
        self.assertIn("simpler vocabulary", low_difficulty)
        
        # Test difficulty 5 conditions
        high_difficulty = self.manager.build_instruction(
            exam_type="gmat",
            question_type="new_question_type",
            difficulty_level=5,
            focused_skill="advanced_reasoning"
        )
        
        self.assertIn("advanced reasoning", high_difficulty)
```

#### Integration Tests
```python
def test_template_integration():
    """Test template integration with question generation"""
    from GMAT.Quants.files.newQuestionTypeGeneration import NewQuestionTypeGenerator
    
    generator = NewQuestionTypeGenerator()
    prompt = "New Question Type - Mathematics - Problem Solving - difficulty_level: 3"
    
    # Generate question using new template
    question = generator.generate_question(prompt)
    
    # Validate output structure
    assert question["type"] == "New Question Type"
    assert question["difficulty"] == 3
    assert "options" in question
    assert "solution" in question
    
    # Validate template philosophy implementation
    assert len(question["options"]) >= 4  # Sufficient trap options
    assert question["solution"] != ""     # Solution provided
```

### 7. Performance Optimization

#### Template Caching Strategy
```python
class OptimizedTemplateManager:
    def __init__(self):
        self.template_cache = {}
        self.compiled_templates = {}
    
    def get_compiled_template(self, template_name):
        """Get pre-compiled template for faster processing"""
        if template_name not in self.compiled_templates:
            template_content = self.load_template(template_name)
            compiled_template = self.compile_template(template_content)
            self.compiled_templates[template_name] = compiled_template
        
        return self.compiled_templates[template_name]
    
    def compile_template(self, template_content):
        """Pre-compile template for faster variable substitution"""
        # Extract variables and conditional blocks
        variables = re.findall(r'\{(\w+)\}', template_content)
        conditionals = re.findall(r'\{\{#(\w+)\}\}', template_content)
        
        return {
            'content': template_content,
            'variables': variables,
            'conditionals': conditionals
        }
```

#### Lazy Loading Implementation
```python
class LazyTemplateLoader:
    def __init__(self):
        self._templates = {}
        self._loaded = set()
    
    def __getitem__(self, template_name):
        if template_name not in self._loaded:
            self._load_template(template_name)
            self._loaded.add(template_name)
        
        return self._templates[template_name]
    
    def _load_template(self, template_name):
        """Load template only when needed"""
        template_path = self._get_template_path(template_name)
        with open(template_path, 'r', encoding='utf-8') as file:
            self._templates[template_name] = file.read()
```

### 8. Debugging and Troubleshooting

#### Debug Logging
```python
import logging

logger = logging.getLogger(__name__)

def debug_template_processing(template_name, variables):
    """Debug template processing"""
    logger.debug(f"Processing template: {template_name}")
    logger.debug(f"Variables: {variables}")
    
    # Log template loading
    template_content = load_template(template_name)
    logger.debug(f"Template content length: {len(template_content)}")
    
    # Log variable substitution
    for var_name, var_value in variables.items():
        logger.debug(f"Substituting {var_name} = {var_value}")
    
    # Log final result
    processed_template = process_template(template_content, variables)
    logger.debug(f"Processed template length: {len(processed_template)}")
    
    return processed_template
```

#### Error Handling
```python
class TemplateProcessingError(Exception):
    """Custom exception for template processing errors"""
    pass

def safe_template_processing(template_name, variables):
    """Template processing with comprehensive error handling"""
    try:
        # Validate inputs
        if not template_name:
            raise ValueError("Template name cannot be empty")
        
        if not isinstance(variables, dict):
            raise TypeError("Variables must be a dictionary")
        
        # Load template
        template_content = load_template(template_name)
        
        # Validate required variables
        required_vars = extract_required_variables(template_content)
        missing_vars = [var for var in required_vars if var not in variables]
        
        if missing_vars:
            raise TemplateProcessingError(
                f"Missing required variables: {missing_vars}"
            )
        
        # Process template
        result = process_template(template_content, variables)
        
        # Validate result
        if not result.strip():
            raise TemplateProcessingError("Template processing resulted in empty content")
        
        return result
    
    except Exception as e:
        logger.error(f"Template processing failed: {str(e)}")
        raise TemplateProcessingError(f"Failed to process template {template_name}: {str(e)}")
```

### 9. Best Practices

#### Template Design
1. **Single Responsibility**: Each template should have one clear purpose
2. **Clear Documentation**: Include comprehensive comments and examples
3. **Variable Naming**: Use descriptive, consistent variable names
4. **Validation**: Include validation rules and quality checks
5. **Modularity**: Design templates to be reusable across question types

#### Code Organization
1. **Directory Structure**: Follow established conventions
2. **File Naming**: Use descriptive, consistent file names
3. **Version Control**: Track template changes with meaningful commits
4. **Documentation**: Keep guides updated with template changes

#### Performance Considerations
1. **Caching**: Cache frequently used templates
2. **Lazy Loading**: Load templates only when needed
3. **Pre-compilation**: Pre-process templates for faster runtime
4. **Memory Management**: Monitor template memory usage

### 10. Advanced Features

#### Custom Template Processors
```python
class CustomTemplateProcessor:
    def __init__(self):
        self.processors = {
            'graph': self.process_graph_variables,
            'dichotomous': self.process_dichotomous_variables,
            'conditional': self.process_conditional_blocks
        }
    
    def process_template(self, template_content, variables, processor_type):
        """Process template with custom processor"""
        if processor_type in self.processors:
            return self.processors[processor_type](template_content, variables)
        else:
            return self.default_process(template_content, variables)
```

#### Template Inheritance
```python
class BaseQuestionTemplate:
    """Base template for all question types"""
    def __init__(self):
        self.base_template = self.load_base_template()
    
    def extend_template(self, specific_template):
        """Extend base template with specific template"""
        return self.base_template + "\n\n" + specific_template
    
    def load_base_template(self):
        """Load base template shared by all question types"""
        return load_template("!Main Instructions/generic.txt.template")
```

This developer guide provides comprehensive information for customizing and extending the template system. Regular updates should be made as the system evolves and new features are added.