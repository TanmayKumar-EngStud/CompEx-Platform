# GMAT Integrated Reasoning

This directory contains the complete infrastructure for generating the four types of questions in the GMAT Integrated Reasoning (IR) section: Graphic Interpretation (GI), Multi-Source Reasoning (MSR), Table Analysis (TA), and Two-Part Analysis (TPA). The system is designed with a modular, component-based architecture that leverages a central `GMATAdapter` to ensure consistency and adherence to GMAT standards.

## Data Flow and Architecture

The question generation process follows a unified data flow, orchestrated by a `BaseQuestionGenerator` and specialized for each question type. Here’s a breakdown of the key components and their interactions:

1.  **`Generate Assistants`**: The `main.py` script in this subdirectory is the starting point for the entire process. It creates and manages four distinct OpenAI Assistants, one for each IR question type. These assistants are responsible for generating the raw content for the questions, solutions, and other components. The script reads system prompts from the `System_Instructions` directory and stores the resulting assistant IDs in a central `assistant_ids.json` file.

2.  **`files` Directory**: This directory contains the core logic for generating each IR question type. Each file (e.g., `GI.py`, `MSR.py`) defines a specialized class that inherits from `BaseQuestionGenerator` and implements the `generate_question` method. This method orchestrates the entire question generation process, from creating the initial prompt to validating the final output.

3.  **`GMATAdapter`**: This central component plays a crucial role in adapting the output of the core question generation components to the specific requirements of the GMAT. It provides a set of methods (e.g., `adapt_graphic_interpretation`, `adapt_two_part_analysis`) that wrap the core components and ensure their output is GMAT-compliant.

4.  **`combinations` Directory**: This directory contains JSON files that define the various combinations of question types, styles, and content. For example, the `MSR.json` file defines the different source materials and question styles that can be used in a Multi-Source Reasoning question.

5.  **`validate_output` Method**: Each question generation class includes a `validate_output` method that ensures the generated question data is valid and complete. This method checks for the presence of all required fields and validates the structure of the data.

## Function Descriptions

-   **`generate_question(prompt)`**: This is the main method in each question generation class. It takes an optional prompt as input and returns a dictionary containing the generated question data. The method is responsible for creating the question component, generating the content, and validating the output.

-   **`create_question_component(...)`**: This factory function creates an instance of the appropriate question component based on the question type. The component is then wrapped with the `GMATAdapter` to ensure GMAT-specific functionality.

-   **`GMATAdapter.adapt_*`**: These methods adapt the core question generation components to the specific requirements of the GMAT. They provide a consistent interface for generating GMAT-compliant questions.

-   **`validate_output(question_data)`**: This method validates the generated question data to ensure it is complete and correctly formatted. It returns `True` if the data is valid and `False` otherwise.

## Example Usage

To generate a GMAT Integrated Reasoning question, you would typically instantiate one of the question generation classes (e.g., `Generate_GI`) and call the `generate_question` method. The method would then orchestrate the entire process, from creating the prompt to validating the output, and return a dictionary containing the generated question data.
