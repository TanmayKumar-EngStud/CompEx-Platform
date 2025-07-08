# 🏭 Core Factories

This directory contains the factories responsible for creating and managing question generators. It acts as a central hub for instantiating the correct generator based on the provided configuration.

---

## `generator_config.py` 📄

This file defines the data classes for managing generator configurations from JSON files. It is the source of truth for what generators are available and how they are configured.

### `GeneratorConfig`

-  **🎯 Purpose**: To load and manage generator configurations from JSON files (e.g., `config/generators/gmat_generators.json`), providing a type-safe way to access generator metadata.
-  **Key Functions**:
   -  **`load_configurations()`**
      -  **📲 Called By**: This function is called internally by other methods in this class to ensure configurations are loaded before they are accessed.
      -  **➡️ Flow**: Reads the JSON files in the `config/generators` directory and parses them into `ExamConfig` objects.
   -  **`get_exam_config(exam_type: ExamType)`**
      -  **📲 Called By**: `GeneratorRegistry` to get the full configuration for an exam.
      -  **📥 Inputs**: `exam_type` (e.g., `ExamType.GMAT`).
      -  **↩️ Returns**: An `ExamConfig` object containing all the sections and generators for that exam.
   -  **`get_generator_metadata(...)`**
      -  **📲 Called By**: `QuestionGeneratorFactory` to get the metadata for a specific generator.
      -  **📥 Inputs**: `exam_type`, `question_type`, `section_type`.
      -  **↩️ Returns**: A `GeneratorMetadata` object with details like the generator's class path and system instruction file.

---

## `generator_registry.py` 📚

This file provides a registry for dynamically loading and managing question generator classes. It uses the information from `GeneratorConfig` to find and import the correct generator classes at runtime.

### `GeneratorRegistry`

-  **🎯 Purpose**: To dynamically load and manage question generator classes based on the configurations in `generator_config.py`.
-  **Key Functions**:
   -  **`load_generators()`**
      -  **📲 Called By**: Internally, to ensure generators are loaded before being accessed.
      -  **➡️ Flow**:
         1. Calls `GeneratorConfig.get_available_generators()` to get the metadata for all generators.
         2. For each generator, it dynamically imports the class specified in the metadata.
   -  **`get_generator_class(...)`**
      -  **📲 Called By**: `QuestionGeneratorFactory` to get the class for a specific generator.
      -  **📥 Inputs**: `exam_type`, `question_type`, `section_type`.
      -  **↩️ Returns**: The generator's class (e.g., `SimpleQuestion`), not an instance.
   -  **`create_generator_instance(...)`**
      -  **📲 Called By**: Can be used to directly create a generator instance, but the `QuestionGeneratorFactory` is the preferred way.
      -  **📥 Inputs**: `exam_type`, `question_type`, `section_type`, and optional `init_args`.
      -  **↩️ Returns**: An instance of the requested generator.

---

## `question_generator_factory.py` 🏭

This file provides the main factory class for creating question generators. This is the primary entry point for the rest of the application to get a question generator.

### `QuestionGeneratorFactory`

-  **🎯 Purpose**: To provide a single, consistent interface for creating instances of question generators.
-  **Key Functions**:
   -  **`create_generator(...)`**
      -  **📲 Called By**: The main application logic, likely in `main.py` or a similar high-level orchestrator.
      -  **📥 Inputs**:
         -  `exam_type`: `ExamType` (e.g., `ExamType.GMAT`)
         -  `question_type`: `QuestionType` (e.g., `QuestionType.PROBLEM_SOLVING`)
         -  `section_type`: `SectionType` (e.g., `SectionType.QUANTITATIVE`)
         -  `global_state`: A shared dictionary for rate limiting.
         -  `lock`: A threading lock.
         -  `api_idx`: The index of the API key to use.
         -  `prompt`: The prompt for the question.
      -  **➡️ Flow**:
         1. Calls `GeneratorRegistry.get_generator_class(...)` to get the generator's class.
         2. Calls `GeneratorRegistry.get_generator_metadata(...)` to get the generator's configuration.
         3. Loads the system instructions from the file specified in the metadata.
         4. Initializes the AI client (`genai.Client`).
         5. Creates an instance of the generator class with all the necessary dependencies.
      -  **↩️ Returns**: An instance of a question generator that implements the `IQuestionGenerator` interface, ready to be used.
