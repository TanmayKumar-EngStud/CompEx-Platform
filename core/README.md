# Core Directory

This directory contains the core logic of the application, which is shared across different exam types like GMAT and GRE. It is organized into subdirectories, each responsible for a specific aspect of the question generation process.

## Subdirectories

-   **components**: Contains the core components of the application, such as question components and adapters for different exams.
-   **config**: Holds the core configuration files for the system and exams.
-   **enums**: Defines the enumerations used throughout the project, such as difficulty levels, exam types, and question types.
-   **exceptions**: Contains custom exception classes for handling errors in a structured manner.
-   **factories**: Includes factories for creating objects, such as question generators and generator configurations.
-   **instructions**: Manages the instructions and templates used for generating questions.
-   **interfaces**: Defines the interfaces for different components, such as mock generators and prompt generators.
-   **mock**: Contains the logic for generating mock exams, including paper and section builders.
-   **prompts**: Manages the prompts used for generating questions, with subdirectories for different exams.
-   **threading**: Handles threading and concurrency for tasks like API calls.
-   **utilities**: Provides a collection of utility functions for various tasks, such as API interaction, debugging, and file handling.

For more detailed information on the functionality and data flow within each subdirectory, please refer to the `README.md` file within that specific subdirectory.