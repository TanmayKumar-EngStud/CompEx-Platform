# Exam Configuration

This directory contains the exam-specific configurations for the question generation system. Each file defines the structure and parameters for a specific standardized test.

## Files

-  **`base_exam_config.py`**: This file defines the abstract base class for all exam configurations. It outlines the common interface that all specific exam configurations must implement, ensuring consistency across the system.

-  **`gmat_config.py`**: This file contains the specific configuration for the GMAT exam. It implements the `BaseExamConfig` and defines the sections, question types, timing, and other parameters relevant to the GMAT.

-  **`gre_config.py`**: This file contains the specific configuration for the GRE exam. It also implements the `BaseExamConfig` and defines the parameters for the GRE.
