# 📜 Core Instructions

This directory is responsible for managing and processing the instruction templates that guide the AI in generating questions. It acts as the central nervous system for controlling the AI's behavior.

---

## `instruction_loader.py` 📂

This file is responsible for loading instruction templates and exam-specific customizations from the file system. It is the first step in the instruction generation process.

### `InstructionLoader`
*   **🎯 Purpose**: To abstract the file system operations required to get the raw text of instruction templates and customization files.
*   **Key Functions**:
    *   **`load_template(question_type, mode)`**
        *   **📲 Called By**: `InstructionManager.get_instruction()`
        *   **📥 Inputs**: `question_type` (e.g., `QuestionType.DATA_SUFFICIENCY`), `mode` (e.g., `"questionText"`).
        *   **➡️ Flow**: Reads the appropriate template file from the `system_instructions/templates` directory.
        *   **↩️ Returns**: The raw string content of the template file.
    *   **`load_customizations(exam_type, question_type)`**
        *   **📲 Called By**: `InstructionManager.get_instruction()`
        *   **📥 Inputs**: `exam_type`, `question_type`.
        *   **➡️ Flow**: Reads the `customizations.json` file for the specified exam and extracts the customizations for the given question type.
        *   **↩️ Returns**: A dictionary of customization parameters.

---

## `template_processor.py` ⚙️

This file is responsible for processing the raw instruction templates, injecting variables and customizations to create the final instruction text.

### `TemplateProcessor`
*   **🎯 Purpose**: To take a raw template and a set of variables and produce the final, processed instruction text.
*   **Key Functions**:
    *   **`process_template(template, ...)`**
        *   **📲 Called By**: `InstructionManager.get_instruction()`
        *   **📥 Inputs**: The raw `template` string, `exam_type`, `question_type`, and a dictionary of `customizations`.
        *   **➡️ Flow**:
            1.  Prepares a dictionary of variables, including default values and exam-specific customizations.
            2.  Processes conditional blocks in the template (e.g., `{{#if_gmat}}...{{/if_gmat}}`).
            3.  Injects graph style information if a prompt is provided.
            4.  Substitutes the variables into the template.
        *   **↩️ Returns**: The final, processed instruction string.

---

## `graph_style_manager.py` 🎨

This file manages the styles for graphs and other visual elements that can be included in questions.

### `GraphStyleManager`
*   **🎯 Purpose**: To load, manage, and inject graph styles into instruction templates.
*   **Key Functions**:
    *   **`inject_graph_style(template, prompt)`**
        *   **📲 Called By**: `TemplateProcessor.process_template()`
        *   **📥 Inputs**: The `template` string and the user `prompt`.
        *   **➡️ Flow**:
            1.  Parses the `prompt` to detect the type of graph being requested (e.g., "bar chart").
            2.  Loads the style configuration for that graph type from `system_instructions/templates/0-questionMetadata/metadata.json`.
            3.  Injects the style information into the `template`.
        *   **↩️ Returns**: The template with the graph style information injected.

---

## `instruction_manager.py` 🧠

This file is the main entry point for the instruction system. It orchestrates the loading, processing, and caching of instructions.

### `InstructionManager`
*   **🎯 Purpose**: To provide a single, high-level interface for getting a fully processed instruction for any given context.
*   **Key Functions**:
    *   **`get_instruction(exam_type, question_type, mode, ...)`**
        *   **📲 Called By**: `core/components/question_components.py` ➡️ `BaseQuestionComponent._get_response()`
        *   **📥 Inputs**: `exam_type`, `question_type`, `mode`, and an optional `prompt`.
        *   **➡️ Flow**:
            1.  Calls `InstructionLoader.load_template()` to get the raw template.
            2.  Calls `InstructionLoader.load_customizations()` to get the exam-specific customizations.
            3.  Calls `TemplateProcessor.process_template()` to get the final, processed instruction.
        *   **↩️ Returns**: The fully processed instruction string, ready to be sent to the AI.
