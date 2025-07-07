# GMAT/GRE Question Generation System - Claude Notes

## Project Overview
This is a sophisticated AI-powered question generation system for GMAT and GRE standardized tests. The system uses Google's Gemini AI models to generate various types of exam questions with proper difficulty calibration and format validation.

## System Architecture

### Core Technologies
- **AI Model**: Google GenerativeAI (Gemini) with API key rotation
- **Database**: PostgreSQL with Prisma ORM
- **Threading**: ThreadPoolExecutor for concurrent question generation
- **Languages**: Python with asyncio support

### Key Components
1. **Main Entry Point**: `main.py` - Orchestrates paper generation for both GMAT and GRE
2. **Mock Classes**: `GMAT/Mock.py` and `GRE/Mock.py` - Handle exam paper generation
3. **Database Layer**: `db.py` with Prisma client for question storage
4. **Question Generators**: Modular generators for different question types
5. **Template System**: Philosophy-driven instruction templates for cognitive testing
6. **Instruction Management**: Dynamic template loading and processing system

## Database Schema (Prisma)

### Key Tables
- **ProblemsSet**: Question collections with metadata, content (JSON), difficulty
- **problems**: Individual questions with solution, metadata, difficulty tracking
- **examtypes**: GMAT/GRE exam type definitions
- **sections**: Quantitative, Verbal, Integrated Reasoning sections
- **tags**: Topic and skill categorization
- **mocktests**: Test sessions with timing and difficulty
- **userattempts**: User performance tracking

### Important Fields
- `content`: JSON field storing question structure (passages, statements, options)
- `solution`: JSON field with detailed step-by-step solutions
- `difficulty`: Integer 1-5 difficulty scale
- `isMockQuestion`: Boolean to distinguish practice vs mock questions
- `mockquestionnumber`: Order within mock tests

## Question Types and Generators

### GMAT Question Types

#### Quantitative Section
1. **Data Sufficiency (`Q_DS_gen`)**
   - Format: Passage + 2 statements + standard 5 DS options
   - File: `GMAT/Quants/files/dataSufficiencyQuestionGeneration.py`
   - Output: `{"type": "Data Sufficiency", "content": {"passages": str, "statements": [str, str]}}`

2. **Simple Questions (`Q_S_gen`)**
   - Format: Multiple choice with 4-5 options
   - File: `GMAT/Quants/files/simpleQuestionGeneration.py`
   - Type: "MCQ-Single"

#### Verbal Section
1. **Parent-Child Questions (`V_PC_gen`)**
   - Format: Reading Comprehension with 3-4 child questions
   - File: `GMAT/Verbal/files/parentChildQuestionGeneration.py`
   - Type: "RC"

2. **Simple Questions (`V_S_gen`)**
   - Format: Critical Reasoning questions
   - File: `GMAT/Verbal/files/simpleQuestionGeneration.py`
   - Type: "CR"

#### Integrated Reasoning Section
1. **Graphic Interpretation (`GI_gen`)**
   - Format: Charts/graphs with fill-in-the-blank
   - File: `GMAT/Integrated_Reasoning/files/GI.py`
   - Content: Bar charts, pie charts, line charts, scatter plots

2. **Two-Part Analysis (`TPA_gen`)**
   - Format: Shared content with two related questions
   - File: `GMAT/Integrated_Reasoning/files/TPA.py`

3. **Table Analysis (`TA_gen`)**
   - Format: Data tables with True/False questions
   - File: `GMAT/Integrated_Reasoning/files/TA.py`
   - Features: Dynamic table size (rows: difficulty + 5-7, cols: difficulty + 3-5)

4. **Multi-Source Reasoning (`MSR_gen`)**
   - Format: 3 sources with 3 child questions
   - File: `GMAT/Integrated_Reasoning/files/MSR.py`
   - Sources: Text, tables, graphs combined

### GRE Question Types

#### Quantitative Section
1. **Data Sufficiency (`Q_DS_gen`)**
   - Similar to GMAT but GRE-specific formatting
   - Type: "DS"

2. **Numeric Entry (`Q_NE_gen`)**
   - Format: Open-ended numerical answers (2 decimal places)
   - File: `GRE/Quants/files/numericEntryQuestionGeneration.py`
   - Type: "NE"

3. **Parent-Child Questions (`Q_PC_gen`)**
   - Format: Problem-solving with shared graphs/tables
   - File: `GRE/Quants/files/parentChildQuestionGeneration.py`
   - Type: "PS"

4. **Simple Questions (`Q_S_gen`)**
   - Standard multiple choice quantitative questions

#### Verbal Section
1. **Parent-Child Questions (`V_PC_gen`)**
   - Format: Reading Comprehension with variable length
   - Types: "rc-s" (2 questions), "rc-m" (3 questions), "rc-l" (4 questions)

2. **Simple Questions (`V_S_gen`)**
   - Text completion and sentence equivalence questions

## Input Prompt Structure

**Standard Format**: `<topic> - <skill> - <question_type> - <difficulty_level: 1-5>`

**Examples**:
- GMAT DS: `"DS - <Arithmetic> - <Logical Reasoning> - <difficulty_level: 4>"`
- GRE NE: `"<work and time> - <difficulty-level: 2>"`
- GMAT GI: `"GI - <Economics> - <Data Interpretation> - <Pie Chart> - <difficulty_level: 2>"`

## Output JSON Structure

All questions follow this standardized format:
```json
{
  "type": "question_type",
  "prompt": "original_prompt",
  "content": {...}, // Passages, tables, graphs
  "question": "question_text",
  "title": "question_title", 
  "options": [...], // For MCQ types
  "answer": "correct_answer",
  "solution": "detailed_solution",
  "difficulty": 1-5,
  "tags": [...]
}
```

## Key Files and Directories

### Configuration Files
- `assistant_ids.json`: AI assistant configuration for both GMAT and GRE
- `requirements.txt`: Python dependencies
- `prisma/schema.prisma`: Database schema definition
- `difficulty_and_is_mock.pkl`: Current difficulty level and mock test status

### Generation Logic
- `GMAT/Mock_prompts/`: Prompt generation for different GMAT sections
- `GRE/Mock_prompts/`: Prompt generation for different GRE sections
- `combinations/`: JSON files tracking question combinations for variety
- `tests/`: Sample question outputs for each question type

### System Instructions & Template System
- `system_instructions/`: New centralized template system with philosophy-driven architecture
- `system_instructions/templates/`: Modular templates for different instruction components
- `system_instructions/templates/!Main Instructions/`: Core philosophy templates for each question type
- `core/instructions/`: Instruction management and template processing system
- `config/schemas/`: Validation schemas for instruction templates

#### Template Architecture
The system uses a modular template architecture with the following components:
- **Main Instructions**: Philosophy-driven templates defining cognitive testing approach
- **Question Components**: Specialized templates for metadata, text, options, solutions, and answers
- **Dynamic Processing**: Template variables populated based on question type and difficulty
- **Validation**: Schema-based validation ensuring template compliance

## Threading and API Management

### APIThreadPoolManager
- Manages concurrent question generation across multiple API keys
- Features API rotation, state management, and task queuing
- Handles rate limiting and retry logic
- Located in both `GMAT/Mock.py` and `GRE/Mock.py`

### Thread Safety
- Global state management with locks for each API instance
- Request count tracking and timing management
- Graceful handling of API failures with retry mechanisms

## Paper Generation Process

1. **Initialization**: Load difficulty level and mock status from pickle file
2. **Prompt Generation**: Create prompts for each section based on difficulty
3. **Concurrent Generation**: Use ThreadPoolExecutor to generate questions in parallel
4. **Storage**: Save generated papers as JSON files in `papers/` directory
5. **Database Registration**: Store questions in PostgreSQL database
6. **State Update**: Increment difficulty level and toggle mock status

## Development Notes

### When Adding New Question Types
1. Create generator class inheriting from base question components
2. Add system instructions file with detailed prompts
3. Update GENERATOR_MAP in respective Mock.py file
4. Add combination JSON for tracking question variety
5. Create test files with expected output formats

### When Modifying Existing Types
1. Update system instructions files
2. Modify generator classes while maintaining output format
3. Update test files with new expected outputs
4. Consider database schema changes if metadata structure changes

### Testing and Validation
- Each question type has test JSON files showing expected outputs
- System validates JSON formatting and required fields
- Built-in retry logic handles generation failures
- Error responses are logged for debugging

## Common Issues and Solutions

### API Rate Limiting
- System uses multiple API keys with rotation
- Built-in delays between API calls
- Global state tracking to respect rate limits

### JSON Format Validation
- Preprocessing and postprocessing of AI responses
- JSON refinement utilities in questionComponents.py
- Strict format validation before database storage

### Thread Synchronization
- Locks prevent race conditions in global state
- Atomic operations for request counting
- Proper cleanup of thread resources

## File Paths for Quick Reference

### Core System Files
- Main orchestrator: `/main.py`
- Database interface: `/db.py`
- GMAT paper generation: `/GMAT/Mock.py`
- GRE paper generation: `/GRE/Mock.py`

### Question Generators (GMAT)
- Data Sufficiency: `/GMAT/Quants/files/dataSufficiencyQuestionGeneration.py`
- Simple Quants: `/GMAT/Quants/files/simpleQuestionGeneration.py`
- Verbal RC: `/GMAT/Verbal/files/parentChildQuestionGeneration.py`
- Verbal CR: `/GMAT/Verbal/files/simpleQuestionGeneration.py`
- Graphic Interpretation: `/GMAT/Integrated_Reasoning/files/GI.py`
- Two-Part Analysis: `/GMAT/Integrated_Reasoning/files/TPA.py`
- Table Analysis: `/GMAT/Integrated_Reasoning/files/TA.py`
- Multi-Source Reasoning: `/GMAT/Integrated_Reasoning/files/MSR.py`

### Question Generators (GRE)
- Data Sufficiency: `/GRE/Quants/files/dataSufficiencyQuestionGeneration.py`
- Numeric Entry: `/GRE/Quants/files/numericEntryQuestionGeneration.py`
- Parent-Child Quants: `/GRE/Quants/files/parentChildQuestionGeneration.py`
- Simple Quants: `/GRE/Quants/files/simpleQuestionGeneration.py`
- Verbal RC: `/GRE/Verbal/files/parentChildQuestionGeneration.py`
- Verbal Simple: `/GRE/Verbal/files/simpleQuestionGeneration.py`