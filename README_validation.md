# Question Paper Validation System

This directory contains a comprehensive validation system for GMAT and GRE question papers. The system checks question counts, validates question completeness, and ensures papers meet the expected standards for database storage.

## Files

- `validate_question_paper.py` - Main validation script for individual papers
- `validate_all_papers.py` - Batch validation script for all papers in the papers directory
- `README_validation.md` - This documentation file

## Features

### 1. Section Count Validation
- Validates total number of questions per section matches expected counts
- Checks question type distribution within acceptable ranges
- Supports both GMAT and GRE paper formats

### 2. Question Completeness Validation
- Ensures all required fields are present (type, question, title, answer, solution, difficulty, tags)
- Checks for optional fields (content, options, prompt)
- Identifies incomplete questions that need attention

### 3. Database Readiness Validation
- Verifies questions are ready for database storage
- Provides summary of how many questions are database-ready
- Highlights missing fields that prevent database storage

### 4. Expected Question Counts

#### GMAT Papers
- **GMAT_V (Verbal)**: 23 total questions
  - RC (Reading Comprehension): 13-14 questions
  - CR (Critical Reasoning): 9-10 questions

- **GMAT_Q (Quantitative)**: 21 total questions
  - MCQ-Single (Problem Solving): 13 questions
  - Data Sufficiency: 8 questions

- **GMAT_IR (Integrated Reasoning)**: 20 total questions
  - MSR (Multi-Source Reasoning): 6 questions
  - TA (Table Analysis): 5 questions
  - GI (Graphics Interpretation): 5 questions
  - TPA (Two-Part Analysis): 4 questions

#### GRE Papers
- **GRE_Q (Quantitative)**: 20 questions per section (section1, section2)
  - DS (Data Sufficiency): 7-8 questions
  - MCQ-Single: 9-10 questions
  - MCQ-Multi: 2 questions
  - NE (Numeric Entry): 1 question

- **GRE_V (Verbal)**: 20 questions per section (section1, section2)
  - RC (Reading Comprehension): 10 questions
  - TC (Text Completion): 6 questions
  - SE (Sentence Equivalence): 4 questions

## Usage

### Validate a Single Paper

```bash
# Basic usage (auto-detects exam type)
python validate_question_paper.py papers/GMAT/GMAT_paper-13-06-16-48-difficulty-5.json

# Specify exam type explicitly
python validate_question_paper.py papers/GRE/GRE_paper-06-06-20-25-difficulty-3.json GRE
```

### Validate All Papers

```bash
# Validate all papers in the papers directory
python validate_all_papers.py
```

## Output

### Individual Paper Validation

The script generates a detailed report with:

1. **Section Count Validation Table**
   - Shows expected vs actual question counts
   - Highlights sections that don't meet requirements
   - PASS/FAIL status for each validation check

2. **Question Completeness Analysis**
   - Lists incomplete questions with missing fields
   - Shows completion percentage
   - Identifies specific missing required fields

3. **Database Readiness Report**
   - Counts questions ready for database storage
   - Lists questions that need fixes before database insertion

4. **Validation Summary**
   - Overall success rate
   - Total checks performed
   - Quick overview of paper quality

### Batch Validation

The batch script provides:

1. **Summary Table**
   - Paper name, exam type, overall status
   - Question counts and completion rates
   - Section validation pass rates

2. **Overall Statistics**
   - Breakdown by quality categories (Excellent, Good, Needs Improvement, Poor)
   - Statistics by exam type (GMAT vs GRE)
   - Average questions per paper

3. **Detailed JSON Report**
   - Complete validation results saved to timestamped JSON file
   - Suitable for further analysis or reporting

## Quality Categories

- **EXCELLENT**: ≥80% section pass rate AND ≥90% question completeness
- **GOOD**: ≥60% section pass rate AND ≥75% question completeness  
- **NEEDS_IMPROVEMENT**: ≥40% section pass rate AND ≥50% question completeness
- **POOR**: Below the above thresholds

## Common Issues and Solutions

### 1. Question Count Mismatches
- **Issue**: Section has wrong number of questions
- **Solution**: Check question generation logic in Mock.py files
- **Example**: GMAT_Q should have exactly 21 questions

### 2. Missing Question Types
- **Issue**: Expected question type not found (e.g., no Data Sufficiency questions)
- **Solution**: Verify question type mapping in generator files
- **Example**: GMAT_Q should have both MCQ-Single and Data Sufficiency

### 3. Incomplete Questions
- **Issue**: Questions missing required fields like tags, solution, etc.
- **Solution**: Check question generation templates and post-processing
- **Common missing fields**: tags, solution, question, answer

### 4. Database Readiness Issues
- **Issue**: Questions not ready for database storage
- **Solution**: Ensure all required fields are populated before saving
- **Critical fields**: type, question, title, answer, solution, difficulty, tags

## Examples

### Sample GMAT Validation Output
```
SECTION COUNT VALIDATION
+-------------------------+----------+------------+----------+-----------------------------------------------+
| Section                 | Status   | Expected   |   Actual | Message                                       |
+=========================+==========+============+==========+===============================================+
| GMAT_Q                  | PASS     | 21         |       21 | Question count matches expected               |
| GMAT_Q.MCQ-Single       | PASS     | 13-13      |       13 | MCQ-Single count within expected range       |
| GMAT_Q.Data Sufficiency | PASS     | 8-8        |        8 | Data Sufficiency count within expected range |
+-------------------------+----------+------------+----------+-----------------------------------------------+
```

### Sample GRE Validation Output
```
SECTION COUNT VALIDATION
+---------------------------+----------+------------+----------+-----------------------------------------+
| Section                   | Status   | Expected   |   Actual | Message                                 |
+===========================+==========+============+==========+=========================================+
| GRE_Q.section1            | PASS     | 20         |       20 | Question count matches expected         |
| GRE_Q.section1.DS         | PASS     | 7-8        |        8 | DS count within expected range          |
| GRE_Q.section1.MCQ-Single | PASS     | 9-10       |        9 | MCQ-Single count within expected range  |
+---------------------------+----------+------------+----------+-----------------------------------------+
```

## Integration

This validation system integrates with:

- Question generation pipeline (GMAT/Mock.py, GRE/Mock.py)
- Database storage system (db.py)
- Paper generation workflow (main.py)

Use this system as part of your quality assurance process to ensure all generated papers meet the required standards before database storage or delivery to users.