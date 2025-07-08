# Claude Code-Companion Onboarding Guide

## Project Overview

This project is a sophisticated, domain-specific question generation system, meticulously designed to produce high-quality questions for standardized tests like the GMAT and GRE. It leverages a modular architecture, where each component is responsible for a specific part of the question generation process, such as text generation, solution creation, and diagrammatic representation. The system is engineered for continuous improvement, incorporating feedback loops to refine and enhance the quality of the generated content. This is a sophisticated AI-powered question generation system for GMAT and GRE standardized tests. The system uses Google's Gemini AI models to generate various types of exam questions with proper difficulty calibration and format validation.

### Core Functionality

The system operates through a pipeline of specialized components:

1. **Question Text Generation**: Creates the title and text of questions based on specified parameters like tags and difficulty levels.
2. **Solution Generation**: Produces detailed, step-by-step solutions for the generated questions, including identifying the correct answer and creating plausible distractors.
3. **Metadata Generation**: When required, this component generates visual aids such as graphs and tables to accompany the questions.
4. **Feedback Integration**: A crucial component that allows for the collection and analysis of user feedback to iteratively improve the models.

This modular approach ensures that each part of the question generation process can be independently developed, tested, and refined, leading to a robust and scalable system.

## Development Process with Claude

To ensure a streamlined and efficient development process, we will adhere to the following guidelines:

### Single Source of Truth: `README.md`

For every folder and subfolder, a `README.md` file will serve as the primary source of documentation. These files will detail:

-  **Data Flow**: How data is manipulated, stored, and fetched within the files of that folder.
-  **Function Descriptions**: A clear explanation of each function's purpose, its role in the overall feature, its input parameters, and its expected output.
-  **Example Usage**: Concrete examples of input and output for each function, covering all relevant use cases.

For higher-level `README.md` files (in folders containing multiple subfolders), the documentation will provide a more abstract overview, focusing on the interaction and data flow between the subfolders rather than the implementation details within each file.

### Testing Framework: The `/.testing` Folder

A dedicated `/.testing` folder will be established to house all testing-related files. This will include:

-  **Unit Tests**: To verify the functionality of individual functions and components.
-  **Integration Tests**: To ensure that different parts of the system work together as expected.

When a function's logic is modified, the corresponding tests in the `/.testing` folder must be updated to reflect the changes. The development workflow will be as follows:

1. **Understand the Change**: First, review the relevant `README.md` to understand the current implementation.
2. **Update Tests**: Modify the tests in the `/.testing` folder to validate the new functionality.
3. **Modify Code**: Implement the required changes in the source code.
4. **Run Tests**: Execute the updated tests to ensure the changes are working correctly and have not introduced any regressions.
5. **Update Documentation**: Once the tests pass, update the corresponding `README.md` file to reflect the new functionality.

This test-driven approach ensures that the codebase remains stable and that the documentation is always in sync with the implementation.

### Continuous Improvement

This `CLAUDE.md` file, along with all other documentation, is a living document. It will be updated as the project evolves to reflect any changes in functionality or workflow.

## Project Structure

Below is the complete folder structure of the project, with a brief description of each file and folder's purpose.

```
/Users/tanmaykumar/Desktop/QGen-py-compex/
├───.gitignore # Files and folders to be ignored by Git.
├───CLAUDE.md # Documentation related to the Claude model.
├───CODE_PROTOCOL.md # Guidelines and protocols for coding standards.
├───db.py # Database connection and management.
├───deletion_all_questions.py # Script for deleting all questions from the database.
├───difficulty_and_is_mock.pkl # Pickled file for difficulty and mock exam data.
├───docker-compose.yml # Docker Compose configuration for setting up the environment.
├───Dockerfile # Dockerfile for building the project's Docker image.
├───GRE-paper.json # JSON file containing a GRE paper.
├───HANDOFF.md # Handoff documentation for project transfer.
├───IMPROVISATION_ROADMAP.md # Roadmap for project improvisations.
├───main.py # Main entry point for the application.
├───MIGRATION_ROADMAP.md # Roadmap for database migrations.
├───PrimaryTablesDefinitions.json # JSON file defining the primary database tables.
├───Readme.md # Project overview and milestones.
├───register-json-paper.py # Script for registering a JSON paper.
├───requirements.txt # List of Python dependencies.
├───requirements.yaml # YAML file for project requirements.
├───STANDARDIZED_GRAPH_STRUCTURES.md # Documentation on standardized graph structures.
├───temp.json # Temporary JSON file.
├───terminal_logger.py # Logger for terminal output.
├───validation_summary_2025-06-13_17-17-42.json # Validation summary report.
├───__pycache__/ # Python cache directory.
├───.claude/ # Claude model related files.
├───.git/ # Git version control directory.
├───.vscode/ # VSCode editor configuration.
├───backup/ # Backup directory.
│   └───instructions_backup_1751729652/ # Backup of instructions.
│       ├───GMAT/ # GMAT related backups.
│       └───GRE/ # GRE related backups.
├───Backup_DB/ # Database backup directory.
│   └───backup(26-02-2025).sql # SQL backup file.
├───config/ # Configuration files.
│   ├───exams/ # Exam-specific configurations.
│   │   ├───__init__.py
│   │   ├───base_exam_config.py # Base configuration for exams.
│   │   ├───gmat_config.py # GMAT specific configuration.
│   │   ├───gre_config.py # GRE specific configuration.
│   │   └───__pycache__/
│   ├───generators/ # Generator configurations.
│   │   ├───gmat_generators.json # GMAT generator settings.
│   │   └───gre_generators.json # GRE generator settings.
│   └───schemas/ # Schema definitions.
│       ├───__init__.py
│       ├───instruction_schemas.py # Schemas for instructions.
│       ├───question_schemas.py # Schemas for questions.
│       └───validation_schemas.py # Schemas for validation.
├───core/ # Core application logic.
│   ├───__init__.py
│   ├───__pycache__/
│   ├───components/ # Core components of the application.
│   │   ├───question_components.py # Components related to questions.
│   │   ├───__pycache__/
│   │   └───adapters/ # Adapters for different exams.
│   ├───config/ # Core configuration.
│   │   ├───__init__.py
│   │   ├───exam_config.py # Exam configuration.
│   │   ├───system_config.py # System configuration.
│   │   └───__pycache__/
│   ├───enums/ # Enumerations used in the project.
│   │   ├───__init__.py
│   │   ├───difficulty_levels.py # Enum for difficulty levels.
│   │   ├───exam_types.py # Enum for exam types.
│   │   ├───question_types.py # Enum for question types.
│   │   ├───section_types.py # Enum for section types.
│   │   └───__pycache__/
│   ├───exceptions/ # Custom exception classes.
│   │   ├───__init__.py
│   │   └───generation_exceptions.py # Exceptions related to generation.
│   ├───factories/ # Factories for creating objects.
│   │   ├───__init__.py
│   │   ├───generator_config.py # Generator configuration factory.
│   │   ├───generator_registry.py # Registry for generators.
│   │   ├───question_generator_factory.py # Factory for question generators.
│   │   └───__pycache__/
│   ├───instructions/ # Instruction management.
│   │   ├───__init__.py
│   │   ├───graph_style_manager.py # Manager for graph styles.
│   │   ├───instruction_loader.py # Loader for instructions.
│   │   ├───instruction_manager.py # Manager for instructions.
│   │   ├───template_processor.py # Processor for templates.
│   │   └───__pycache__/
│   ├───interfaces/ # Interfaces for different components.
│   │   ├───__init__.py
│   │   ├───mock_generator.py # Interface for mock generators.
│   │   ├───prompt_generator.py # Interface for prompt generators.
│   │   ├───question_generator.py # Interface for question generators.
│   │   └───__pycache__/
│   ├───mock/ # Mock exam generation.
│   │   ├───__init__.py
│   │   ├───paper_builder.py # Builder for mock papers.
│   │   ├───section_builder.py # Builder for mock sections.
│   │   ├───unified_mock_generator.py # Unified mock generator.
│   │   └───__pycache__/
│   ├───prompts/ # Prompt generation.
│   │   ├───__init__.py
│   │   ├───prompt_generator_factory.py # Factory for prompt generators.
│   │   ├───__pycache__/
│   │   ├───base/ # Base prompts.
│   │   ├───gmat/ # GMAT specific prompts.
│   │   └───gre/ # GRE specific prompts.
│   ├───threading/ # Threading management.
│   │   ├───__init__.py
│   │   ├───api_thread_pool_manager.py # Thread pool manager for APIs.
│   │   ├───exceptions.py # Threading exceptions.
│   │   ├───thread_config.py # Threading configuration.
│   │   └───__pycache__/
│   └───utilities/ # Utility functions.
│       ├───__init__.py
│       ├───api_utils.py # API utilities.
│       ├───debug_utils.py # Debugging utilities.
│       ├───file_utils.py # File utilities.
│       ├───json_utils.py # JSON utilities.
│       ├───logging_utils.py # Logging utilities.
│       ├───options_converter.py # Options converter.
│       ├───tags_char.json # JSON for tags characters.
│       ├───validation_utils.py # Validation utilities.
│       └───__pycache__/
├───GMAT/ # GMAT specific files.
│   ├───assistant_ids.json # Assistant IDs for GMAT.
│   ├───Mock.py # GMAT mock exam generation.
│   ├───__pycache__/
│   ├───Integrated_Reasoning/ # Integrated Reasoning section.
│   │   ├───__pycache__/
│   │   ├───combinations/ # Combinations for IR.
│   │   ├───files/ # Files for IR.
│   │   └───Generate Assistants/ # Scripts to generate assistants.
│   ├───Mock_prompts/ # Prompts for GMAT mock exams.
│   │   ├───Integrated_Reasoning.py
│   │   ├───Quants.py
│   │   ├───Verbal.py
│   │   ├───__pycache__/
│   │   └───jsonfiles/
│   ├───Quants/ # Quantitative section.
│   │   ├───__pycache__/
│   │   ├───combinations/ # Combinations for Quants.
│   │   ├───files/ # Files for Quants.
│   │   └───Generate Assistants/ # Scripts to generate assistants.
│   └───Verbal/ # Verbal section.
│       ├───__pycache__/
│       ├───combinations/ # Combinations for Verbal.
│       ├───files/ # Files for Verbal.
│       └───Generate Assistants/ # Scripts to generate assistants.
├───GRE/ # GRE specific files.
│   ├───assistant_ids.json # Assistant IDs for GRE.
│   ├───Mock.py # GRE mock exam generation.
│   ├───__pycache__/
│   ├───Mock_prompts/ # Prompts for GRE mock exams.
│   │   ├───Quants.py
│   │   ├───Verbal.py
│   │   ├───__pycache__/
│   │   └───jsonfiles/
│   ├───Quants/ # Quantitative section.
│   │   ├───__init__.py
│   │   ├───__pycache__/
│   │   ├───combinations/ # Combinations for Quants.
│   │   ├───files/ # Files for Quants.
│   │   └───...
│   └───Verbal/ # Verbal section.
├───IMPROVEMENT REQUIRED/ # Documentation on required improvements.
│   ├───GENERAL-ARCHITECTURE-IMPROVEMENT.md
│   └───ROADMAP-FOR-INCORPORATING-THESE-IMPROVEMENT.md
├───ISSUES/ # Issue tracking.
│   └───log_22-41-20.md
├───logs/ # Log files.
├───papers/ # Generated papers.
│   ├───GMAT/
│   └───GRE/
├───prisma/ # Prisma ORM files.
│   ├───schema.prisma # Prisma schema.
│   ├───schema.prisma.txt
│   └───migrations/ # Database migrations.
├───scripts/ # Utility scripts.
│   └───migration/
├───SECURITY/ # Security related documentation.
│   └───README.md
├───system_instructions/ # System-level instructions.
│   ├───DEVELOPER_GUIDE.md
│   ├───README.md
│   ├───gmat/
│   ├───gre/
│   ├───in_the_run/
│   ├───older_system_instructions_for_reference/
│   └───templates/
├───testing/ # Testing directory.
│   ├───README_validation.md
│   ├───README.md
│   ├───run_all_tests.py # Script to run all tests.
│   ├───test_dynamic_selection.py
│   ├───test_generator_integration.py
│   ├───test_graph_styles.py
│   ├───test_instruction_system.py
│   ├───test_main_instructions.py
│   ├───test_philosophical_alignment.py
│   ├───validate_all_papers.py # Script to validate all papers.
│   ├───validate_question_paper.py # Script to validate a single paper.
│   └───__pycache__/
└───venv/ # Python virtual environment.
    ├───bin/
    ├───include/
    └───lib/
```
