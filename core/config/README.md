# ⚙️ Core Configuration

This directory contains the core configuration files for the application. These files define the settings and parameters that control the behavior of the question generation system.

---

## `system_config.py` 🖥️

This file defines the `SystemConfig` class, which manages system-wide settings that apply across all exam types and components.

### `SystemConfig`
*   **🎯 Purpose**: To provide a centralized location for all global configuration settings.
*   **Key Attributes**:
    *   `database_url`: The connection string for the database.
    *   `api_timeout_seconds`: The timeout for API calls.
    *   `api_max_retries`: The maximum number of retries for failed API calls.
    *   `papers_output_directory`: The directory where generated papers are saved.
    *   `logs_directory`: The directory where log files are saved.
*   **Key Functions**:
    *   `from_environment()`: Loads the system configuration from environment variables.
    *   `configure_logging()`: Sets up the logging system based on the configuration.

---

## `exam_config.py` 🎓

This file defines the base classes for exam-specific configurations.

### `BaseExamConfig`
*   **🎯 Purpose**: An abstract base class that defines the common interface for all exam configurations.
*   **Key Attributes**:
    *   `exam_type`: The type of exam (e.g., GMAT or GRE).
    *   `debug_mode`: A boolean to enable or disable debug mode.
    *   `max_retries`: The maximum number of retries for question generation.

### `GMATConfig`
*   **📦 Extends**: `BaseExamConfig`
*   **🎯 Purpose**: Defines the specific configuration settings for the GMAT exam.
*   **Key Attributes**:
    *   `include_integrated_reasoning`: A boolean to include or exclude the Integrated Reasoning section.
    *   `quant_questions_per_section`: The number of questions in the Quantitative section.
    *   `verbal_questions_per_section`: The number of questions in the Verbal section.

### `GREConfig`
*   **📦 Extends**: `BaseExamConfig`
*   **🎯 Purpose**: Defines the specific configuration settings for the GRE exam.
*   **Key Attributes**:
    *   `quant_questions_per_section`: The number of questions in the Quantitative section.
    *   `verbal_questions_per_section`: The number of questions in the Verbal section.
