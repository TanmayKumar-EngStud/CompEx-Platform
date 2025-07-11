# GMAT Mock Prompts

This directory contains the scripts and configuration files responsible for generating the prompts for a complete GMAT mock exam. The system is designed to create a balanced and realistic mock exam experience by dynamically generating prompts based on a predefined difficulty level and component allocation.

## Data Flow and Architecture

The prompt generation process is driven by a set of Python scripts, one for each section of the GMAT exam (Integrated Reasoning, Quants, and Verbal). These scripts leverage a common set of JSON configuration files to ensure consistency and adherence to the GMAT's structure and difficulty distribution.

1.  **`jsonfiles` Directory**: This directory contains the core configuration files that drive the prompt generation process:
    *   **`difficulty_distribution.json`**: This file defines the distribution of question difficulty levels (easy, medium, hard) for each section of the GMAT exam. The distribution is based on the overall difficulty level of the mock exam.
    *   **`component_allocation.json`**: This file specifies the allocation of different question types, styles, and themes within each section. It also includes a `combination_number` that is used to ensure a varied selection of components.

2.  **Prompt Generation Scripts**: Each Python script in this directory is responsible for generating the prompts for a specific section of the GMAT exam:
    *   **`Integrated_Reasoning.py`**: This script generates the prompts for the Integrated Reasoning section. It uses the `difficulty_distribution.json` and `component_allocation.json` files to create a balanced set of prompts with varying question types (MSR, TPA, TA, GI), themes, and difficulty levels.
    *   **`Quants.py`**: This script generates the prompts for the Quantitative section. It follows a similar approach to the `Integrated_Reasoning.py` script, but with a focus on Quantitative question types, topics, and themes.
    *   **`Verbal.py`**: This script generates the prompts for the Verbal section. It uses the same configuration-driven approach to create a balanced set of prompts for Reading Comprehension (RC) and Critical Reasoning (CR) questions.

3.  **`get_difficulty_pool()` Method**: Each prompt generation script includes a `get_difficulty_pool()` method that creates a pool of difficulty levels based on the mock exam's overall difficulty. This ensures that the generated prompts have a realistic distribution of difficulty.

4.  **`generate_question_prompts()` Method**: This is the main method in each prompt generation script. It uses the difficulty pool and component allocation to generate a list of prompts for the corresponding section. The method also updates the `combination_number` in the `component_allocation.json` file to ensure that subsequent mock exams have a different combination of prompts.

## Function Descriptions

-   **`__init__(mock_difficulty)`**: The constructor for each prompt generation class. It takes the overall difficulty level of the mock exam as input and initializes the difficulty distribution and component allocation from the JSON files.

-   **`get_difficulty_pool()`**: This method returns a list of difficulty levels that are used to generate the prompts. The distribution of difficulty levels is determined by the mock exam's overall difficulty.

-   **`generate_question_prompts()`**: This method generates a list of prompts for the corresponding section of the GMAT exam. The prompts are created based on the difficulty pool and component allocation, and the `combination_number` is updated to ensure variety in subsequent mock exams.

## Example Usage

To generate the prompts for a GMAT mock exam, you would typically instantiate each of the prompt generation classes (e.g., `Integrated_Reasoning_prompts`, `Quants_prompts`, `Verbal_prompts`) with the desired mock exam difficulty. Then, you would call the `generate_question_prompts()` method on each instance to get a list of prompts for each section.
