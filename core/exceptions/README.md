# 🚨 Core Exceptions

This directory contains custom exception classes for the question generation system, providing specific error types for different failure modes.

---

## `generation_exceptions.py` 💥

This file defines the custom exception classes used throughout the application to provide specific and informative errors.

### `QGenBaseException(Exception)`
*   **🎯 Purpose**: This is the foundational exception class for all custom errors within the QGen project. It's designed to be subclassed, not raised directly.
*   **✨ Key Attributes**:
    *   `message` (str): The error message.
    *   `error_code` (Optional[str]): An optional, unique code for the error.
    *   `timestamp` (float): The time at which the exception was raised.
*   **`__init__(self, message: str, error_code: Optional[str] = None)`**
    *   **🎯 Purpose**: Initializes the base exception.
    *   **📥 Inputs**:
        *   `message`: A descriptive error message.
        *   `error_code`: An optional error code.
    *   **📲 Called By**: The `__init__` methods of its subclasses.

### `QuestionGenerationException(QGenBaseException)`
*   **🎯 Purpose**: Raised to indicate a failure during the generation of any part of a question (e.g., text, options, solution).
*   **📲 Raised In**:
    *   `core/components/question_components.py` ➡️ `create_question_component()`: When an unsupported question type is requested.
        *   **Example**: `raise QuestionGenerationException(f"Unsupported question type: {question_type}")`
    *   `core/components/question_components.py` ➡️ `BaseQuestionComponent.__init__()`: When an invalid prompt format is provided.
        *   **Example**: `raise QuestionGenerationException(f"Invalid prompt format: {prompt}")`

### `PromptGenerationException(QGenBaseException)`
*   **🎯 Purpose**: Specifically used when the process of creating a prompt for the AI fails.
*   **📲 Raised In**: This exception is available for use but is not currently raised in the provided codebase. It would be used in a function responsible for dynamically constructing prompts.

### `PromptValidationException(QGenBaseException)`
*   **🎯 Purpose**: Used when a generated prompt fails a validation check before being sent to the AI.
*   **📲 Raised In**: This exception is available for use but is not currently raised in the provided codebase. It would be used in a function that validates prompts against a set of rules.

### `MockGenerationException(QGenBaseException)`
*   **🎯 Purpose**: Raised to indicate an error during the creation of a mock exam paper.
*   **📲 Raised In**: This exception is intended for use in the `core/mock` directory, for example, if the `paper_builder.py` fails to assemble a complete mock paper.

### `ConfigurationException(QGenBaseException)`
*   **🎯 Purpose**: Raised when a configuration setting is invalid or missing.
*   **📲 Raised In**: This exception is intended for use in the `core/config` directory, for example, if a `validate()` method within `exam_config.py` fails.
