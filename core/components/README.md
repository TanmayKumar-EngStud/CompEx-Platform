# 🚀 Core Components

This directory contains the core, unified components of the application, responsible for the main functionalities of the question generation process. These components are designed to be exam-agnostic, with exam-specific behavior handled by adapters.

---

## `question_components.py` 🧩

This file is the heart of the question generation system. It defines a set of classes that encapsulate the logic for generating different types of questions.

### `BaseQuestionComponent` 🏗️
An abstract base class that provides common functionality for all question components, including:
- **Rate Limiting** ⏱️
- **Retry Logic** 🔄
- **Error Handling & Logging** 📝
- **Response Processing** 📦

### `SimpleQuestion` ❓
Generates simple, single-part questions (e.g., standard multiple-choice, numeric entry).

### `DataSufficiencyQuestion` 🤔
Handles the generation of data sufficiency questions, including the question stem and two statements.

### `ParentChildQuestion` 👨‍👧‍👦
Manages questions with a shared parent element (like a passage or graph) and multiple child questions.

### Specialized IR Components 📊
Includes classes for GMAT Integrated Reasoning: `GraphicInterpretationQuestion`, `TableAnalysisQuestion`, `TwoPartAnalysisQuestion`, and `MultiSourceReasoningQuestion`.

---

## `adapters/` 🔌

This subdirectory contains adapters that act as **translators**. They bridge the gap between the unified components in `question_components.py` and the specific, often older, function names and data structures expected by the exam-specific parts of the application (e.g., scripts in the `GMAT/` and `GRE/` directories).

### `gmat_adapter.py` 🦁

This adapter provides classes that wrap the unified components for the GMAT workflow.

#### `GMATSimpleQuestionAdapter`
*   **📦 Wraps**: `SimpleQuestion`
*   **🎯 Purpose**: Handles standard GMAT questions like Problem Solving and Critical Reasoning.
*   **📲 Interaction Example**:
    *   **Caller**: A script like `GMAT/Quants/files/simpleQuestionGeneration.py`.
    *   **Calls**: `GMATSimpleQuestionAdapter.generate_questionText(...)`
    *   **➡️ Flow**: The adapter function `generate_questionText` immediately calls the core component: `question_components.py` ➡️ `SimpleQuestion.generate_question_text(...)`.
    *   **↩️ Returns**: A `string` containing the question text.

#### `GMATDataSufficiencyAdapter`
*   **📦 Wraps**: `DataSufficiencyQuestion`
*   **🎯 Purpose**: Handles GMAT Data Sufficiency questions.
*   **📲 Interaction Example**:
    *   **Caller**: A script like `GMAT/Quants/files/dataSufficiencyQuestionGeneration.py`.
    *   **Calls**: `GMATDataSufficiencyAdapter.generate_questionOptions()`
    *   **➡️ Flow**: The adapter function calls `question_components.py` ➡️ `DataSufficiencyQuestion.generate_question_options_with_answer()`.
    *   **↩️ Returns**: A `Tuple` containing a `Dict` of the standard A-E options and a `str` with the correct answer key (e.g., 'A').

#### `GMATParentChildAdapter`
*   **📦 Wraps**: `ParentChildQuestion`
*   **🎯 Purpose**: Handles GMAT Reading Comprehension.
*   **📲 Interaction Example**:
    *   **Caller**: A script handling GMAT Verbal sections.
    *   **Calls**: `GMATParentChildAdapter.generate_parentQuestion()`
    *   **➡️ Flow**: The adapter calls `question_components.py` ➡️ `ParentChildQuestion.generate_parent_question()` to get the main passage.
    *   **↩️ Returns**: A `str` containing the RC passage.

---

### `gre_adapter.py` 🦉

This adapter provides classes that wrap the unified components for the GRE workflow.

#### `GRESimpleQuestionAdapter`
*   **📦 Wraps**: `SimpleQuestion`
*   **🎯 Purpose**: Handles GRE questions like Quantitative Comparison, standard multiple-choice, and Numeric Entry.
*   **📲 Interaction Example**:
    *   **Caller**: A script like `GRE/Quants/files/simpleQuestionGeneration.py`.
    *   **Calls**: `GRESimpleQuestionAdapter.generate_questionSolution(isNE=True)` for a Numeric Entry question.
    *   **➡️ Flow**: The adapter calls `question_components.py` ➡️ `SimpleQuestion.generate_question_solution(is_numeric_entry=True)`.
    *   **↩️ Returns**: A `Tuple` containing the solution `str` and the numeric answer `float`.

#### `GREDataSufficiencyAdapter`
*   **📦 Wraps**: `DataSufficiencyQuestion`
*   **🎯 Purpose**: Handles GRE Data Sufficiency questions.
*   **📲 Interaction Example**:
    *   **Caller**: A script like `GRE/Quants/files/dataSufficiencyQuestionGeneration.py`.
    *   **Calls**: `GREDataSufficiencyAdapter.generate_questionText()`
    *   **➡️ Flow**: The adapter calls `question_components.py` ➡️ `DataSufficiencyQuestion.generate_question_text()`.
    *   **↩️ Returns**: A `Tuple` containing the passage `str`, a `List` of statements, and the question `str`.

#### `GREParentChildAdapter`
*   **📦 Wraps**: `ParentChildQuestion`
*   **🎯 Purpose**: Handles GRE Reading Comprehension and Quantitative questions with shared elements.
*   **📲 Interaction Example**:
    *   **Caller**: A script handling GRE Verbal sections.
    *   **Calls**: `GREParentChildAdapter.generate_passages()`
    *   **➡️ Flow**: The adapter calls `question_components.py` ➡️ `ParentChildQuestion.generate_question_metadata()` and extracts the passage from the returned dictionary.
    *   **↩️ Returns**: A `str` containing the RC passage.
