# GMAT/GRE Question Generation System - Metadata Values

This document lists all standardized metadata values used throughout the question generation system.

## Graph/Chart Types

### Standardized Naming (with hyphens)
- `bar-graph`
- `line-graph`
- `pie-chart`
- `scatter-plot`
- `stacked-bar-graph`

### STANDARDIZED JSON STRUCTURES

All graph/chart structures now follow consistent field naming:
- Use `type` field only (remove redundant `graph` field)
- Use `x_axis` and `y_axis` (with underscores)
- Use `label` consistently for data point identifiers
- Use lowercase with hyphens for type values

#### 1. Bar-Graph Structure
```json
{
  "type": "bar-graph",
  "title": "Chart Title",
  "description": "Description of what this bar-graph shows",
  "x_axis": "X-axis Label",
  "y_axis": "Y-axis Label", 
  "data": [
    { "label": "Category A", "value": 1500 },
    { "label": "Category B", "value": 1200 },
    { "label": "Category C", "value": 900 }
  ]
}
```

#### 2. Stacked Bar-Graph Structure
```json
{
  "type": "stacked-bar-graph",
  "title": "Chart Title",
  "description": "Description of what this stacked bar-graph shows",
  "x_axis": "X-axis Label",
  "y_axis": "Y-axis Label",
  "data": [
    {
      "category": "Q1",
      "values": [
        { "label": "Region A", "value": 500 },
        { "label": "Region B", "value": 300 }
      ]
    }
  ]
}
```

#### 3. Line-Graph Structure
```json
{
  "type": "line-graph",
  "title": "Chart Title",
  "description": "Description of what this line-graph shows",
  "x_axis": "X-axis Label",
  "y_axis": "Y-axis Label",
  "data": [
    {
      "series": "Series A",
      "values": [
        { "x": "Jan", "y": 500 },
        { "x": "Feb", "y": 700 }
      ]
    }
  ]
}
```

#### 4. Pie-Chart Structure
```json
{
  "type": "pie-chart",
  "title": "Chart Title", 
  "description": "Description of what this pie-chart shows",
  "data": [
    { "label": "Category A", "value": 30, "color": "#FF6B6B" },
    { "label": "Category B", "value": 25, "color": "#4ECDC4" }
  ]
}
```

#### 5. Scatter-Plot Structure
```json
{
  "type": "scatter-plot",
  "title": "Chart Title",
  "description": "Description of what this scatter-plot shows", 
  "x_axis": "X-axis Label",
  "y_axis": "Y-axis Label",
  "data": [
    { "label": "Point A", "x": 5000, "y": 20000 },
    { "label": "Point B", "x": 7000, "y": 30000 }
  ]
}
```

## Table Types

### Standard Data Structures
- `standard data table`
- `pivot table`
- `highlight table`
- `heat table`
- `text table`
- `matrix table`
- `frequency table`
- `contingency table`

## Question Types

### GMAT Question Types
- `Data Sufficiency` (DS)
- `MCQ-Single` (Multiple Choice - Single Answer)
- `RC` (Reading Comprehension)
- `CR` (Critical Reasoning)
- `GI` (Graphic Interpretation)
- `TPA` (Two-Part Analysis)
- `TA` (Table Analysis)
- `MSR` (Multi-Source Reasoning)

### GRE Question Types
- `DS` (Data Sufficiency)
- `NE` (Numeric Entry)
- `PS` (Problem Solving)
- `rc-s` (Reading Comprehension - Short, 2 questions)
- `rc-m` (Reading Comprehension - Medium, 3 questions)
- `rc-l` (Reading Comprehension - Long, 4 questions)
- `TC-1` (Text Completion - 1 blank)
- `TC-2` (Text Completion - 2 blanks)
- `TC-3` (Text Completion - 3 blanks)
- `SE` (Sentence Equivalence)

## Difficulty Levels
- `1` (Easiest)
- `2` (Easy)
- `3` (Medium)
- `4` (Hard)
- `5` (Hardest)

## Section Types

### GMAT Sections
- `GMAT_Q` (GMAT Quantitative)
- `GMAT_V` (GMAT Verbal)
- `GMAT_IR` (GMAT Integrated Reasoning)

### GRE Sections
- `GRE_Q` (GRE Quantitative)
- `GRE_V` (GRE Verbal)

## Tags and Skills

### Quantitative Tags
- `Algebra`
- `Geometry`
- `Number Theory`
- `Arithmetic`
- `Data Analysis`
- `Statistics`
- `Logical Reasoning`
- `Word Problems`
- `Probability`
- `Combinatorics`
- `Advanced Topics`
- `Permutations and Combinations`
- `Ratio and Proportion`
- `Work and Time`

### Verbal Tags
- `Critical Reasoning`
- `Reading Comprehension`
- `Text Completion`
- `Sentence Equivalence`
- `Analyze the Argument`
- `Strengthen/Weaken`
- `Assumption`
- `Inference`

### Integrated Reasoning Tags
- `Data Interpretation`
- `Multi-Source Reasoning`
- `Table Analysis`
- `Graphic Interpretation`
- `Two-Part Analysis`

## Data Sufficiency Answer Options
- `A`: "Statement (1) ALONE is sufficient, but statement (2) alone is not sufficient."
- `B`: "Statement (2) ALONE is sufficient, but statement (1) alone is not sufficient."
- `C`: "BOTH statements TOGETHER are sufficient, but NEITHER statement alone is sufficient."
- `D`: "EITHER statement ALONE is sufficient."
- `E`: "Statements (1) and (2) TOGETHER are NOT sufficient."

## Mock Test Metadata
- `isMockQuestion`: Boolean (true/false)
- `mockquestionnumber`: Integer (order within mock test)

## Database Fields

### Required JSON Structure
```json
{
  "type": "question_type",
  "prompt": "original_prompt",
  "content": {...},
  "question": "question_text",
  "title": "question_title",
  "options": [...],
  "answer": "correct_answer",
  "solution": "detailed_solution",
  "difficulty": 1-5,
  "tags": [...]
}
```

### Content Structure Examples

#### For Data Sufficiency Questions
```json
{
  "content": {
    "passage": "question passage",
    "statements": ["statement 1", "statement 2"]
  }
}
```

#### For Graph/Table Questions
```json
{
  "content": {
    "graph/table": {
      "type": "bar-graph",
      "title": "graph title",
      "data": {...}
    }
  }
}
```

#### For Parent-Child Questions
```json
{
  "content": {
    "passage": "main passage",
    "graph/table": [...],
    "childQuestions": [...]
  }
}
```

## File Naming Conventions

### Paper Output Files
- `GMAT_paper-DD-MM-HH-MM-difficulty-X.json`
- `GRE_paper-DD-MM-HH-MM-difficulty-X.json`

### Log Files
- `question_generation_YYYY-MM-DD_HH-MM-SS.log`
- `validation_summary_YYYY-MM-DD_HH-MM-SS.json`

## System Prompt Keywords

### Mode Keywords
- `questionText`
- `questionTitle`
- `questionSolution`
- `questionOptions`
- `questionGraph`
- `parentTitle`
- `childQuestionText`
- `childQuestionTitle`
- `childQuestionSolution`
- `childQuestionOptions`

### Input Format Keywords
- `mode:-`
- `input:-`
- `difficulty-level:`
- `<topic>`
- `<skill>`
- `<question_type>`

## API Configuration

### Model Settings
- `MODEL`: "gemini-2.5-flash"
- Rate limit: 10 requests per minute per API key
- Retry attempts: 3

### Response Format Requirements
- All responses must be wrapped in ```json code blocks
- Use double quotes for all JSON keys and values
- Use backticks (`) instead of single quotes inside strings
- Use `<br>` tags for line breaks within JSON values
- Use `~~mathematical expressions~~` for mathematical notation

## Error Handling

### Common Error Types
- `JSON parsing failed`
- `Empty response received`
- `Failed to parse JSON response`
- `Resource Exhausted (429)`
- `Internal Server Error (500)`

### Retry Logic
- Maximum 3 retry attempts per generation
- Exponential backoff with rate limiting
- API key rotation on failures

## Theme Examples

### Quantitative Themes
- Business investment data
- Manufacturing statistics
- Sales performance metrics
- Population demographics
- Technology adoption rates
- Economic indicators

### Verbal Themes
- Scientific research findings
- Historical analysis
- Social policy discussions
- Environmental studies
- Literature criticism
- Philosophy and ethics

## Output Quality Standards

### Solution Requirements
- Step-by-step explanations
- Mathematical work clearly shown
- Logical reasoning emphasized
- Strategic tips included
- 2 decimal place precision for numerical answers

### Content Requirements
- Formal language and tone
- Proper grammar and syntax
- Clear and unambiguous wording
- Appropriate difficulty level
- Educational value