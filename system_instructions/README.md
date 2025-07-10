# System Instructions Architecture

This document provides a comprehensive overview of the dynamic instruction generation system used to create tailored prompts for the AI model. The system is designed to be modular, extensible, and highly specific, ensuring that for any given Exam, Section, and Question Type, a precise set of instructions can be generated for each component of a question.

## High-Level Overview

The core principle of this system is the separation of structure, content, and customization. Instead of using static, monolithic instruction files, we use a template-based approach to dynamically build instructions on the fly. This allows for greater flexibility, easier maintenance, and more precise control over the AI's behavior.

The main components of this system are:

1. **Templates**: Reusable skeletons for different parts of a question.
2. **Customizations**: Exam-specific data and constraints.
3. **Code Logic**: The Python code that orchestrates the loading, processing, and assembly of the final instruction.

## Core Components

### 1. `templates` Directory

This is the heart of the system. It contains the generic, reusable templates for every component (or "mode") of a question. The directory is structured numerically to represent the order of question generation:

-  `0-questionMetadata`: Templates for generating the core data of a question, such as passages, graphs, or other stimuli.
-  `1-questionText`: Templates for generating the main question text.
-  `2-questionTitle`: Templates for generating the question title.
-  `4-questionOptions`: Templates for generating the answer options.
-  `3-questionSolution`: Templates for generating the detailed solution.
-  `5-questionAnswer`: Templates for generating the final, correct answer.

Within each directory, you will find `.txt.template` files. These files contain placeholders (e.g., `${EXAM_NAME}`, `${DIFFICULTY_SCALING}`) that are dynamically replaced with exam-specific information during the instruction generation process.

### 2. `gmat/customizations.json` & `gre/customizations.json`

These files provide the exam-specific data that is injected into the templates. They contain a nested JSON structure where the top-level keys are the `QuestionType` values (e.g., `problem_solving`, `data_sufficiency`).

When a request for a GMAT Problem Solving question comes in, the system loads the `problem_solving` object from `gmat/customizations.json` and uses its values to populate the placeholders in the chosen template. This is how a generic template is transformed into a highly specific GMAT or GRE instruction.

### 3. `templates/0-questionMetadata/metadata.json`

This file defines the structure, styling, and JSON format for various types of content that can be generated as part of a question's stimulus, including graphs, passages, and tables. It follows a unified content type architecture with a class structure: content (base class) → graph, passage, table (child classes). This ensures consistency in content representation across the platform.

## The Code Logic: How It All Comes Together

The magic of this system lies in the Python code that orchestrates the entire process. The two key files are:

-  `core/instructions/instruction_manager.py`
-  `core/instructions/instruction_loader.py`

### The Flow of an Instruction Request

Here’s a step-by-step trace of how the system generates an instruction:

1. **Request Initiation**: The process begins when a component, such as the `UnifiedMockGenerator`, needs to create a question. It requests a specific instruction component (a `mode`) for a given `ExamType` and `QuestionType` from the `InstructionManager`.

2. **InstructionManager**: This class is the central hub. It validates the request against its `SPECIALIZED_MODES` dictionary to ensure that the requested `mode` is valid for the given `QuestionType`.

3. **InstructionLoader**: The `InstructionManager` then delegates the task of finding and loading the correct template to the `InstructionLoader`. The loader uses a two-step mapping process:

   -  **`component_map`**: This dictionary maps the requested `mode` (e.g., `questionOptions`) to a specific folder within the `templates` directory (e.g., `4-questionOptions`).
   -  **`question_style_map`**: This dictionary maps the `QuestionType` (e.g., `text_completion`) to the specific template file within that folder (e.g., `3-text_completion.txt.template`). If a specific template for a question type doesn't exist, it intelligently falls back to the `0-generic.txt.template` in the same folder.

4. **Template and Customization Loading**: The `InstructionLoader` reads the content of the identified template file and also loads the corresponding customization data from the appropriate `customizations.json` file (e.g., `gre/customizations.json`).

5. **TemplateProcessor**: The `InstructionManager` receives the raw template and the customization data from the loader. It then uses the `TemplateProcessor` to perform a "mail merge." The processor intelligently injects the customization values into the placeholders in the template, creating the final, highly specific instruction.

### Example: GRE Text Completion Options

Let's trace a request for the options of a GRE Text Completion question:

1. **Request**: `InstructionManager.get_instruction(ExamType.GRE, QuestionType.TEXT_COMPLETION, 'questionOptions')`
2. **Manager**: Validates that `questionOptions` is a valid mode for `TEXT_COMPLETION`.
3. **Loader**:
   -  `component_map` maps `'questionOptions'` to the `4-questionOptions` folder.
   -  `question_style_map` maps `'text_completion'` to the `3-text_completion.txt.template` file.
4. **Loading**: The loader reads `system_instructions/templates/4-questionOptions/3-text_completion.txt.template` and the `text_completion` section from `system_instructions/gre/customizations.json`.
5. **Processing**: The `TemplateProcessor` merges the two, resulting in a detailed prompt that instructs the AI on how to generate options specifically for GRE Text Completion questions, including the correct JSON structure for single, double, or triple blanks.

## How to Extend the System

Adding a new question type or component is straightforward:

1. **Create the Template**: Add a new `.txt.template` file in the appropriate sub-directory under `templates`.
2. **Update the Maps**:
   -  If you've created a new template for an existing mode, add an entry to the `question_style_map` in `instruction_loader.py`.
   -  If you've created a completely new mode, add it to the `component_map` in `instruction_loader.py` and the `SPECIALIZED_MODES` dictionary in `instruction_manager.py`.
3. **Add Customizations**: Add the corresponding configuration for the new type to the `gmat/customizations.json` and `gre/customizations.json` files.

This modular architecture ensures that the system remains robust, maintainable, and capable of generating highly specific and effective instructions for the AI model.
