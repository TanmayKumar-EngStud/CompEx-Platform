# 🛠️ Core Utilities Module

This directory contains fundamental utility functions that provide centralized support capabilities across the entire GMAT/GRE question generation system. These utilities eliminate code duplication and provide consistent functionality for API management, JSON processing, validation, debugging, logging, file operations, and data format conversion.

---

## 📄 Data Flow and Manipulation

**🎯 Purpose**: This module provides foundational utility functions that support all other system components. Data flows from various system components through these utilities for processing, validation, storage, and debugging. The utilities act as a service layer, handling common operations like API requests, JSON parsing, file I/O, and data validation.

**Flow**: System components → Utility functions → External services/files/validation → Processed data back to system components

---

## 📁 File Structure

### `api_utils.py` 🌐

**🎯 Purpose**: Provides centralized API management for Google Gemini AI integration including key rotation, rate limiting, and request handling.

#### **Function: `get_api_key`**
*   **🎯 Purpose**: Retrieve API key from environment variables by index with validation
*   **📥 Inputs**:
    *   `index: int` - Index of API key in environment
    *   Example values: `0` (for API_0), `1` (for API_1), `5` (for API_5)
*   **↩️ Returns**:
    *   `str` - API key string from environment
    *   Example: `"AIzaSyBX8Fm3nV2cK9QwZrTpL5oY7dXeR4jMqAb"` for valid key
*   **📲 Called By**:
    *   `core/threading/api_thread_pool_manager.py:APIThreadPoolManager.__init__()`
    *   `GMAT/Mock.py:initialize_api_clients()`
    *   `GRE/Mock.py:initialize_api_clients()`
*   **➡️ Calls**: 
    *   `os.getenv()` to retrieve environment variables
    *   `_validate_api_key_format()` for key validation

#### **Function: `_validate_api_key_format`**
*   **🎯 Purpose**: Validate Google Gemini API key format for basic correctness
*   **📥 Inputs**:
    *   `api_key: str` - API key string to validate
    *   Example values: `"AIzaSyBX8Fm3nV2cK9QwZrTpL5oY7dXeR4jMqAb"`, `"invalid_key"`, `""`
*   **↩️ Returns**:
    *   `bool` - Validation result
    *   Example: `True` for valid format (length > 20, string type)
    *   Example: `False` for invalid format
*   **📲 Called By**:
    *   `get_api_key()` for key validation
    *   `core/utilities/validation_utils.py:validate_api_key_format()`
*   **➡️ Calls**: No external function calls

#### **Function: `rotate_api_key`**
*   **🎯 Purpose**: Calculate next API key index for round-robin rotation to distribute load
*   **📥 Inputs**:
    *   `current_index: int` - Current API key index
    *   `max_keys: int` - Maximum number of API keys available (default: 10)
    *   Example combinations: `(0, 10)`, `(9, 10)`, `(5, 8)`
*   **↩️ Returns**:
    *   `int` - Next API key index using modulo arithmetic
    *   Example: `1` for input `(0, 10)`
    *   Example: `0` for input `(9, 10)` (wraps around)
*   **📲 Called By**:
    *   `core/threading/api_thread_pool_manager.py:APIThreadPoolManager.rotate_api_key()`
    *   `GMAT/Mock.py:handle_api_rotation()`
    *   `GRE/Mock.py:handle_api_rotation()`
*   **➡️ Calls**: No external function calls

#### **Function: `get_available_api_keys`**
*   **🎯 Purpose**: Scan environment variables to find all available API key indices
*   **📥 Inputs**: None
*   **↩️ Returns**:
    *   `List[int]` - List of available API key indices
    *   Example: `[0, 1, 2, 5, 7]` if API_0, API_1, API_2, API_5, API_7 exist
    *   Example: `[0]` if only API_0 exists
*   **📲 Called By**:
    *   `core/threading/api_thread_pool_manager.py:APIThreadPoolManager.__init__()`
    *   `main.py:initialize_api_management()`
*   **➡️ Calls**: 
    *   `os.getenv()` to check for environment variables

#### **Function: `create_api_client`**
*   **🎯 Purpose**: Create and configure Google Gemini API client with authentication
*   **📥 Inputs**:
    *   `api_key: str` - Valid API key for authentication
    *   Example values: `"AIzaSyBX8Fm3nV2cK9QwZrTpL5oY7dXeR4jMqAb"`
*   **↩️ Returns**:
    *   `genai.Client` - Configured Gemini API client
    *   Example: Authenticated client ready for question generation
*   **📲 Called By**:
    *   `core/threading/api_thread_pool_manager.py:APIThreadPoolManager._create_client()`
    *   `core/components/question_components.py:BaseQuestionComponent.__init__()`
*   **➡️ Calls**: 
    *   `genai.configure()` to set API key
    *   `genai` module functions for client creation

#### **Class: `RateLimitManager`**
*   **🎯 Purpose**: Manage API rate limiting to prevent quota exhaustion and 429 errors
*   **✨ Key Attributes**:
    *   `requests_per_minute: int` - Maximum requests per minute (default: 9)
    *   `request_count: int` - Current request count in window
    *   `start_time: float` - Window start timestamp
    *   `lock: threading.Lock` - Thread synchronization lock

#### **Method: `wait_if_needed`**
*   **🎯 Purpose**: Block execution if rate limit would be exceeded, with automatic window reset
*   **📥 Inputs**: None (instance method)
*   **↩️ Returns**: None (blocks execution as needed)
*   **📲 Called By**:
    *   `APIRequestHandler.make_request()` before each API call
    *   `core/components/question_components.py:BaseQuestionComponent._get_response()`
*   **➡️ Calls**: 
    *   `time.time()` for timestamp calculations
    *   `time.sleep()` for rate limiting delays

#### **Method: `reset_on_error`**
*   **🎯 Purpose**: Reset rate limiting state after API errors with extra safety buffer
*   **📥 Inputs**: None (instance method)
*   **↩️ Returns**: None (resets internal state)
*   **📲 Called By**:
    *   `APIRequestHandler.make_request()` on API errors
    *   `core/components/question_components.py:BaseQuestionComponent._get_response()` on exceptions
*   **➡️ Calls**: 
    *   `time.time()` for timestamp calculations
    *   `time.sleep()` for error recovery delays

#### **Class: `APIRequestHandler`**
*   **🎯 Purpose**: Handle API requests with built-in retry logic, error handling, and rate limiting integration

#### **Method: `make_request`**
*   **🎯 Purpose**: Execute API request with rate limiting and comprehensive error handling
*   **📥 Inputs**:
    *   `chat_instance` - Gemini chat instance
    *   `prompt: str` - Text prompt to send
    *   `warn: bool` - Whether to append JSON warning (default: False)
    *   Example combinations: `(chat_instance, "Generate a math question", False)`, `(chat_instance, "QuestionSolution", True)`
*   **↩️ Returns**:
    *   `Optional[str]` - AI response text or None on failure
    *   Example: `"Here is a mathematics question about..."` for successful response
    *   Example: `None` for failed request
*   **📲 Called By**:
    *   `core/components/question_components.py:BaseQuestionComponent._get_response()`
    *   Custom API request handlers in question generators
*   **➡️ Calls**: 
    *   `self.rate_limit_manager.wait_if_needed()` for rate limiting
    *   `core.utilities.json_utils.JSON_ERROR_WARNING` for warning messages
    *   `chat_instance.send_message()` for actual API call

#### **Function: `get_model_name`**
*   **🎯 Purpose**: Retrieve AI model name from environment variables with fallback
*   **📥 Inputs**: None
*   **↩️ Returns**:
    *   `str` - Model name string
    *   Example: `"gemini-1.5-pro"` if MODEL environment variable is set
    *   Example: `"gemini-1.5-flash"` as default fallback
*   **📲 Called By**:
    *   `create_chat_instance()` for model configuration
    *   `core/components/question_components.py:BaseQuestionComponent._create_chat_session()`
*   **➡️ Calls**: 
    *   `os.getenv()` to retrieve environment variables

#### **Function: `create_chat_instance`**
*   **🎯 Purpose**: Create configured chat instance with system instructions and thinking mode
*   **📥 Inputs**:
    *   `api_client` - Configured API client
    *   `system_instructions: str` - System instruction text for AI behavior
    *   `thinking_enabled: bool` - Whether to enable thinking mode (default: True)
    *   Example: `(client, "Generate GMAT questions...", True)`
*   **↩️ Returns**:
    *   Configured chat instance ready for question generation
*   **📲 Called By**:
    *   `core/components/question_components.py:BaseQuestionComponent._create_chat_session()`
    *   Question generator initialization methods
*   **➡️ Calls**: 
    *   `get_model_name()` for model selection
    *   `google.genai.types.GenerateContentConfig()` for configuration
    *   `api_client.chats.create()` for instance creation

---

### `json_utils.py` 📄

**🎯 Purpose**: Centralized JSON processing with AI response cleanup, LaTeX conversion, and character tag replacement for mathematical notation.

#### **Function: `_load_tags_mapping`**
*   **🎯 Purpose**: Load character tag mapping from tags_char.json file for mathematical symbol conversion
*   **📥 Inputs**: None (module-level initialization)
*   **↩️ Returns**:
    *   `Dict[str, str]` - Mapping from tags to Unicode characters
    *   Example: `{"<pi>": "π", "<alpha>": "α", "<implies>": "⇒", "<infinity>": "∞"}`
    *   Example: `{}` empty dict as fallback on file load error
*   **📲 Called By**:
    *   Module initialization (executed once at import)
*   **➡️ Calls**: 
    *   `os.path.dirname()` and `os.path.join()` for file path construction
    *   `json.load()` to read tags_char.json file

#### **Function: `refine_response`**
*   **🎯 Purpose**: Clean and normalize AI responses by removing markdown, fixing LaTeX, and converting character tags
*   **📥 Inputs**:
    *   `response_text: str` - Raw AI response text
    *   Example values: `"```json\\n{\"question\": \"What is π?\"}\\n```"`, `"The answer is \\sqrt{25}"`, `"<pi> equals 3.14159"`
*   **↩️ Returns**:
    *   `str` - Cleaned and formatted JSON string
    *   Example: `"{\"question\": \"What is π?\"}"` for markdown-wrapped input
    *   Example: `"{\"error\": \"Failed to parse JSON response\"}"` for unparseable input
*   **📲 Called By**:
    *   `core/components/question_components.py:BaseQuestionComponent._process_json_response()`
    *   All question generation components for response processing
    *   Legacy question generators for JSON cleanup
*   **➡️ Calls**: 
    *   `re.sub()` for pattern matching and replacement
    *   `json.loads()` for validation
    *   `json.dumps()` for formatting
    *   `fix_tags_in_json()` for character tag replacement

#### **Function: `validate_json_format`**
*   **🎯 Purpose**: Validate that a string contains valid JSON syntax
*   **📥 Inputs**:
    *   `json_string: str` - String to validate
    *   Example values: `"{\"valid\": \"json\"}"`, `"invalid json"`, `"{'single': 'quotes'}"`
*   **↩️ Returns**:
    *   `bool` - Validation result
    *   Example: `True` for valid JSON syntax
    *   Example: `False` for invalid JSON syntax
*   **📲 Called By**:
    *   `core/utilities/validation_utils.py:validate_json_structure()`
    *   Question generation validation methods
    *   Data integrity checks before database storage
*   **➡️ Calls**: 
    *   `json.loads()` for validation

#### **Function: `is_error_response`**
*   **🎯 Purpose**: Check if parsed JSON is an error response from refine_response processing
*   **📥 Inputs**:
    *   `message: Dict[str, Any]` - Parsed JSON dictionary
    *   Example values: `{"error": "Failed to parse JSON response"}`, `{"question": "Valid content"}`, `{"error": "Empty response", "data": "extra"}`
*   **↩️ Returns**:
    *   `bool` - True if this is an error response, False otherwise
    *   Example: `True` for `{"error": "Failed to parse JSON response"}`
    *   Example: `False` for `{"question": "Valid content"}`
*   **📲 Called By**:
    *   `core/components/question_components.py:BaseQuestionComponent._process_json_response()`
    *   Error handling logic in question generators
*   **➡️ Calls**: No external function calls

#### **Function: `safe_json_loads`**
*   **🎯 Purpose**: Safely parse JSON string with comprehensive error handling and logging
*   **📥 Inputs**:
    *   `json_string: str` - JSON string to parse
    *   Example values: `"{\"valid\": \"json\"}"`, `"malformed {json"`, `"null"`
*   **↩️ Returns**:
    *   `Optional[Dict[str, Any]]` - Parsed dictionary or None on failure
    *   Example: `{"valid": "json"}` for valid input
    *   Example: `None` for malformed input
*   **📲 Called By**:
    *   `core/utilities/file_utils.py:load_json_file()` for safe file loading
    *   Configuration file loading methods
    *   Data validation utilities
*   **➡️ Calls**: 
    *   `json.loads()` for parsing

#### **Function: `log_detailed_error`**
*   **🎯 Purpose**: Log comprehensive error information for debugging AI response parsing failures
*   **📥 Inputs**:
    *   `context: str` - Context description for the error
    *   `raw_response: str` - Original AI response that caused error
    *   `error: str` - Error message or exception details
    *   `expected_keys: Optional[list]` - Expected JSON keys for validation
    *   Example: `("GMAT DataSufficiency generate_options", "C", "Missing required keys", ["options", "answer"])`
*   **↩️ Returns**: None (logging function)
*   **📲 Called By**:
    *   `core/components/question_components.py:BaseQuestionComponent._process_json_response()`
    *   Error handling methods in question generators
*   **➡️ Calls**: 
    *   `refine_response()` to show processed output
    *   `json.loads()` for parsing analysis

---

### `validation_utils.py` ✅

**🎯 Purpose**: Centralized validation system for prompts, question data, enum values, and system inputs with comprehensive error reporting.

#### **Function: `validate_prompt`**
*   **🎯 Purpose**: Validate question generation prompt format and content for basic correctness
*   **📥 Inputs**:
    *   `prompt: str` - Prompt string to validate
    *   Example values: `"DS - Arithmetic - Logical Reasoning - difficulty level: 4"`, `""`, `"a"`, `"Very long prompt that exceeds reasonable limits..."`
*   **↩️ Returns**:
    *   `bool` - Validation result
    *   Example: `True` for valid prompt with reasonable length and content
    *   Example: `False` for empty, too short, too long, or invalid prompts
*   **📲 Called By**:
    *   `core/components/question_components.py:BaseQuestionComponent.__init__()`
    *   All question generator initialization methods
    *   Input validation in main.py
*   **➡️ Calls**: 
    *   `re.search()` for content pattern matching

#### **Function: `validate_difficulty_level`**
*   **🎯 Purpose**: Validate difficulty level input accepts integers, strings, or DifficultyLevel enums
*   **📥 Inputs**:
    *   `difficulty: Union[int, str, DifficultyLevel]` - Difficulty level to validate
    *   Example values: `1`, `"easy"`, `DifficultyLevel.HARD`, `6`, `"invalid"`, `None`
*   **↩️ Returns**:
    *   `bool` - Validation result
    *   Example: `True` for valid range 1-5 integers, valid enum values, or parseable strings
    *   Example: `False` for out-of-range values or invalid types
*   **📲 Called By**:
    *   `validate_question_data()` for question data validation
    *   `core/utilities/api_utils.py:validate_difficulty()` for API input validation
    *   `main.py:parse_difficulty_from_pickle()`
*   **➡️ Calls**: 
    *   `DifficultyLevel.from_string()` for string conversion

#### **Function: `validate_exam_type`**
*   **🎯 Purpose**: Validate exam type input accepts strings or ExamType enums
*   **📥 Inputs**:
    *   `exam_type: Union[str, ExamType]` - Exam type to validate
    *   Example values: `"GMAT"`, `"gre"`, `ExamType.GMAT`, `"invalid"`, `123`
*   **↩️ Returns**:
    *   `bool` - Validation result
    *   Example: `True` for valid exam types ("GMAT", "GRE", or enum values)
    *   Example: `False` for invalid types or unrecognized strings
*   **📲 Called By**:
    *   `core/factories/question_generator_factory.py:QuestionGeneratorFactory.create_generator()`
    *   Configuration validation methods
    *   `main.py:validate_exam_selection()`
*   **➡️ Calls**: 
    *   `ExamType.from_string()` for string conversion

#### **Function: `validate_question_type`**
*   **🎯 Purpose**: Validate question type input accepts strings, abbreviations, or QuestionType enums
*   **📥 Inputs**:
    *   `question_type: Union[str, QuestionType]` - Question type to validate
    *   Example values: `"DS"`, `"data_sufficiency"`, `QuestionType.DATA_SUFFICIENCY`, `"invalid"`, `None`
*   **↩️ Returns**:
    *   `bool` - Validation result
    *   Example: `True` for valid question types, abbreviations, or enum values
    *   Example: `False` for unrecognized types
*   **📲 Called By**:
    *   `core/factories/question_generator_factory.py:QuestionGeneratorFactory.create_generator()`
    *   Question type parsing in generator files
    *   Legacy compatibility validation
*   **➡️ Calls**: 
    *   `QuestionType.from_string()` for string/abbreviation conversion

#### **Function: `validate_section_type`**
*   **🎯 Purpose**: Validate section type input accepts strings, abbreviations, or SectionType enums
*   **📥 Inputs**:
    *   `section_type: Union[str, SectionType]` - Section type to validate
    *   Example values: `"quantitative"`, `"V"`, `"IR"`, `SectionType.VERBAL`, `"invalid"`
*   **↩️ Returns**:
    *   `bool` - Validation result
    *   Example: `True` for valid section types ("quantitative", "verbal", "integrated_reasoning", or abbreviations)
    *   Example: `False` for unrecognized section types
*   **📲 Called By**:
    *   `core/mock/section_builder.py:SectionBuilder.build_section()`
    *   Section configuration validation
    *   Legacy section mapping validation
*   **➡️ Calls**: 
    *   `SectionType.from_string()` for string/abbreviation conversion

#### **Function: `validate_question_data`**
*   **🎯 Purpose**: Comprehensive validation of generated question data structure and content
*   **📥 Inputs**:
    *   `question_data: Dict[str, Any]` - Question data dictionary to validate
    *   `question_type: Optional[QuestionType]` - Expected question type for type-specific validation
    *   Example: `({"type": "DS", "content": {"passages": "...", "statements": [...]}, "question": "...", "answer": "A", "solution": "...", "difficulty": 3}, QuestionType.DATA_SUFFICIENCY)`
*   **↩️ Returns**:
    *   `bool` - Validation result
    *   Example: `True` for complete, well-formed question data
    *   Example: `False` for missing fields, invalid structure, or type-specific validation failures
*   **📲 Called By**:
    *   All question generator methods before returning generated data
    *   Database storage validation in `db.py`
    *   Quality assurance checks in testing modules
*   **➡️ Calls**: 
    *   `validate_difficulty_level()` for difficulty validation
    *   `_validate_type_specific_content()` for question-type specific checks

#### **Function: `_validate_type_specific_content`**
*   **🎯 Purpose**: Validate question content based on specific question type requirements
*   **📥 Inputs**:
    *   `question_data: Dict[str, Any]` - Question data to validate
    *   `question_type: QuestionType` - Question type for validation rules
    *   Example: `({"content": {"passages": "text", "statements": ["stmt1", "stmt2"]}}, QuestionType.DATA_SUFFICIENCY)`
*   **↩️ Returns**:
    *   `bool` - Type-specific validation result
    *   Example: `True` for data sufficiency questions with proper passages and 2 statements
    *   Example: `False` for missing required fields or incorrect structure
*   **📲 Called By**:
    *   `validate_question_data()` for type-specific validation
*   **➡️ Calls**: No external function calls

#### **Function: `validate_api_key_format`**
*   **🎯 Purpose**: Validate API key format for security and basic correctness checks
*   **📥 Inputs**:
    *   `api_key: str` - API key to validate
    *   Example values: `"AIzaSyBX8Fm3nV2cK9QwZrTpL5oY7dXeR4jMqAb"`, `"short"`, `"invalid-chars!@#"`
*   **↩️ Returns**:
    *   `bool` - Validation result
    *   Example: `True` for keys with proper length and character set
    *   Example: `False` for too short keys or invalid characters
*   **📲 Called By**:
    *   `core/utilities/api_utils.py:_validate_api_key_format()`
    *   API key configuration validation
    *   Security validation in initialization
*   **➡️ Calls**: 
    *   `re.match()` for character pattern validation

#### **Function: `validate_file_path`**
*   **🎯 Purpose**: Validate file path format and optionally check existence for security
*   **📥 Inputs**:
    *   `file_path: str` - File path to validate
    *   `must_exist: bool` - Whether file must exist (default: False)
    *   Example combinations: `("/valid/path/file.json", True)`, `("../../../etc/passwd", False)`, `("safe/path.txt", False)`
*   **↩️ Returns**:
    *   `bool` - Validation result
    *   Example: `True` for safe paths without dangerous patterns
    *   Example: `False` for paths with directory traversal attempts or dangerous characters
*   **📲 Called By**:
    *   `core/utilities/file_utils.py:load_json_file()` for safe file loading
    *   Configuration file path validation
    *   Template file security checks
*   **➡️ Calls**: 
    *   `os.path.exists()` when must_exist is True

#### **Function: `sanitize_input_string`**
*   **🎯 Purpose**: Remove potentially harmful content from input strings while preserving essential content
*   **📥 Inputs**:
    *   `input_string: str` - String to sanitize
    *   `max_length: int` - Maximum allowed length (default: 1000)
    *   Example values: `("Normal text with punctuation!", 1000)`, `("Very long string...", 100)`, `("Text with <script>alert('xss')</script>", 1000)`
*   **↩️ Returns**:
    *   `str` - Sanitized string
    *   Example: `"Normal text with punctuation!"` for safe input
    *   Example: `"Text with scriptalert('xss')script"` with dangerous tags removed
*   **📲 Called By**:
    *   User input processing in question generators
    *   Prompt sanitization before API calls
    *   Database input sanitization
*   **➡️ Calls**: 
    *   `re.sub()` for pattern removal and whitespace normalization

#### **Function: `validate_question_options`**
*   **🎯 Purpose**: Validate question options format and answer correspondence for multiple choice questions
*   **📥 Inputs**:
    *   `options: List[str]` - List of option strings
    *   `answer: str` - Correct answer string or label
    *   Example: `(["Option A", "Option B", "Option C"], "Option A")`, `(["Red", "Blue"], "C")`, `([], "")`
*   **↩️ Returns**:
    *   `bool` - Validation result
    *   Example: `True` for valid options list with corresponding answer
    *   Example: `False` for empty options, invalid answer, or mismatched answer
*   **📲 Called By**:
    *   Question option generation validation
    *   Multiple choice question validation
    *   Database storage validation for MCQ questions
*   **➡️ Calls**: 
    *   `_is_valid_option_label()` for answer label validation

#### **Function: `_is_valid_option_label`**
*   **🎯 Purpose**: Check if a label is a valid option identifier (A, B, C, etc. or 1, 2, 3, etc.)
*   **📥 Inputs**:
    *   `label: str` - Label to check
    *   `num_options: int` - Number of options available
    *   Example combinations: `("A", 4)`, `("E", 3)`, `("2", 5)`, `("Z", 2)`
*   **↩️ Returns**:
    *   `bool` - Validation result
    *   Example: `True` for "A" with 4 options, "2" with 5 options
    *   Example: `False` for "E" with 3 options, "Z" with any number
*   **📲 Called By**:
    *   `validate_question_options()` for answer label validation
*   **➡️ Calls**: No external function calls

#### **Function: `validate_json_structure`**
*   **🎯 Purpose**: Validate that a JSON structure contains all required keys for completeness
*   **📥 Inputs**:
    *   `data: Dict[str, Any]` - Dictionary to validate
    *   `required_keys: List[str]` - List of required key names
    *   Example: `({"question": "...", "answer": "A"}, ["question", "answer", "options"])`, `({"complete": "data"}, ["complete"])`
*   **↩️ Returns**:
    *   `bool` - Validation result
    *   Example: `True` when all required keys are present
    *   Example: `False` when required keys are missing
*   **📲 Called By**:
    *   JSON response validation in question generators
    *   Configuration file validation
    *   API response validation
*   **➡️ Calls**: No external function calls

---

### `debug_utils.py` 🔍

**🎯 Purpose**: Debug information logging system for tracking system instruction usage and generation failures.

#### **Class: `SystemInstructionDebugger`**
*   **🎯 Purpose**: Handle logging of system instructions for debugging question generation issues
*   **✨ Key Attributes**:
    *   `base_path: Path` - Base directory for debug files (default: "system_instructions/in_the_run")

#### **Method: `log_system_instruction`**
*   **🎯 Purpose**: Log system instruction and related debug information to files for analysis
*   **📥 Inputs**:
    *   `exam_type: ExamType` - GMAT or GRE
    *   `question_type: QuestionType` - Type of question being generated
    *   `component_name: str` - Name of the component being generated
    *   `system_instruction: str` - Complete system instruction sent to AI
    *   `prompt: str` - Specific prompt used for generation
    *   `component_system_instruction: str` - System instruction for this specific component (default: "")
    *   `response: Optional[str]` - AI response if any (default: None)
    *   `call_priority_index: int` - Order of component call (default: 1)
    *   Example: `(ExamType.GMAT, QuestionType.DATA_SUFFICIENCY, "generate_question_text", "Complete instruction...", "DS prompt", "", "AI response", 1)`
*   **↩️ Returns**:
    *   `str` - Path to the debug file created
    *   Example: `"system_instructions/in_the_run/gmat/data_sufficiency/1generate_question_text.json"`
*   **📲 Called By**:
    *   `core/components/question_components.py:BaseQuestionComponent._log_debug_info()`
    *   Question generation failure tracking
*   **➡️ Calls**: 
    *   `json.dump()` to write debug data to files
    *   `pathlib.Path.mkdir()` to create directories

#### **Function: `get_debugger`**
*   **🎯 Purpose**: Get the global debugger instance using singleton pattern
*   **📥 Inputs**: None
*   **↩️ Returns**:
    *   `SystemInstructionDebugger` - Global debugger instance
*   **📲 Called By**:
    *   `log_system_instruction()` convenience function
    *   Debug utilities throughout the system
*   **➡️ Calls**: 
    *   `SystemInstructionDebugger()` constructor if not yet initialized

#### **Function: `log_system_instruction`**
*   **🎯 Purpose**: Convenience function to log system instruction using global debugger
*   **📥 Inputs**:
    *   Same parameters as `SystemInstructionDebugger.log_system_instruction()`
*   **↩️ Returns**:
    *   `str` - Path to the debug file created
*   **📲 Called By**:
    *   `core/components/question_components.py:BaseQuestionComponent._log_debug_info()`
    *   Question generator debug logging
*   **➡️ Calls**: 
    *   `get_debugger().log_system_instruction()` for actual logging

#### **Function: `get_recent_failures`**
*   **🎯 Purpose**: Retrieve recent generation failures for debugging analysis
*   **📥 Inputs**:
    *   `exam_type: ExamType` - GMAT or GRE
    *   `limit: int` - Maximum number of failures to return (default: 10)
    *   Example: `(ExamType.GMAT, 5)`, `(ExamType.GRE, 20)`
*   **↩️ Returns**:
    *   `list` - List of recent failure debug information
    *   Example: `[{"file": "path/to/debug.json", "data": {...}, "question_style": "DS", "last_updated": "2025-07-08T10:30:00"}]`
*   **📲 Called By**:
    *   Debug analysis tools
    *   System health monitoring
    *   Failure pattern analysis
*   **➡️ Calls**: 
    *   `get_debugger().get_recent_failures()` for actual retrieval

#### **Function: `cleanup_old_debug_files`**
*   **🎯 Purpose**: Clean up debug files older than specified days to manage disk usage
*   **📥 Inputs**:
    *   `days_old: int` - Number of days to keep files (default: 7)
    *   Example values: `7`, `30`, `1`
*   **↩️ Returns**: None (cleanup function)
*   **📲 Called By**:
    *   Maintenance scripts
    *   System cleanup routines
    *   Automated cleanup jobs
*   **➡️ Calls**: 
    *   `get_debugger().cleanup_old_files()` for actual cleanup

---

### `logging_utils.py` 📝

**🎯 Purpose**: Structured logging utilities providing consistent logging across all system components with contextual information.

#### **Class: `StructuredLogger`**
*   **🎯 Purpose**: Structured logging utility with consistent formatting and contextual information for debugging and monitoring
*   **✨ Key Attributes**:
    *   `logger: logging.Logger` - Python logger instance
    *   `name: str` - Logger name/component identifier

#### **Method: `log_generation_start`**
*   **🎯 Purpose**: Log the start of a generation operation with context and timing
*   **📥 Inputs**:
    *   `operation: str` - Description of operation being started
    *   `exam_type: ExamType` - GMAT or GRE
    *   Example: `("GMAT paper generation", ExamType.GMAT)`, `("Question validation", ExamType.GRE)`
*   **↩️ Returns**: None (logging function)
*   **📲 Called By**:
    *   `core/mock/unified_mock_generator.py:UnifiedMockGenerator.generate_mock_paper()`
    *   `main.py:main()` for paper generation start
*   **➡️ Calls**: 
    *   `self.logger.info()` for logging
    *   `time.time()` for timestamp

#### **Method: `log_generation_success`**
*   **🎯 Purpose**: Log successful generation completion with result data
*   **📥 Inputs**:
    *   `result_data: Dict[str, Any]` - Information about the successful generation
    *   Example: `{"questions_generated": 37, "difficulty": 3, "exam_type": "GMAT"}`
*   **↩️ Returns**: None (logging function)
*   **📲 Called By**:
    *   `core/mock/unified_mock_generator.py:UnifiedMockGenerator.generate_mock_paper()` on success
    *   Question generation completion handlers
*   **➡️ Calls**: 
    *   `self.logger.info()` for logging
    *   `time.time()` for timestamp

#### **Method: `log_generation_error`**
*   **🎯 Purpose**: Log generation errors with comprehensive context and stack trace
*   **📥 Inputs**:
    *   `error: Exception` - Exception that occurred
    *   `context: Dict[str, Any]` - Contextual information about the error
    *   Example: `(ValueError("Invalid prompt"), {"prompt": "...", "question_type": "DS", "attempt": 3})`
*   **↩️ Returns**: None (logging function)
*   **📲 Called By**:
    *   Exception handling blocks throughout the system
    *   Error recovery mechanisms
*   **➡️ Calls**: 
    *   `self.logger.error()` for logging with exc_info=True for stack traces
    *   `time.time()` for timestamp

#### **Method: `log_instruction_request`**
*   **🎯 Purpose**: Log instruction loading requests for debugging instruction system
*   **📥 Inputs**:
    *   `exam_type: ExamType` - GMAT or GRE
    *   `question_type: QuestionType` - Type of question
    *   `mode: str` - Instruction mode (e.g., "questionText", "questionSolution")
    *   Example: `(ExamType.GMAT, QuestionType.DATA_SUFFICIENCY, "questionText")`
*   **↩️ Returns**: None (logging function)
*   **📲 Called By**:
    *   `core/instructions/instruction_manager.py:InstructionManager.get_instruction()`
    *   Template loading operations
*   **➡️ Calls**: 
    *   `self.logger.debug()` for detailed logging
    *   `time.time()` for timestamp

#### **Method: `log_instruction_success`**
*   **🎯 Purpose**: Log successful instruction loading completion
*   **📥 Inputs**:
    *   `exam_type: ExamType` - GMAT or GRE
    *   `question_type: QuestionType` - Type of question
    *   `mode: str` - Instruction mode
    *   Example: `(ExamType.GRE, QuestionType.READING_COMPREHENSION, "questionOptions")`
*   **↩️ Returns**: None (logging function)
*   **📲 Called By**:
    *   `core/instructions/instruction_manager.py:InstructionManager.get_instruction()` on success
    *   Template processing completion
*   **➡️ Calls**: 
    *   `self.logger.debug()` for detailed logging
    *   `time.time()` for timestamp

#### **Method: `log_instruction_error`**
*   **🎯 Purpose**: Log instruction loading errors with context for debugging template issues
*   **📥 Inputs**:
    *   `error: Exception` - Exception that occurred during instruction loading
    *   `exam_type: ExamType` - GMAT or GRE
    *   `question_type: QuestionType` - Type of question
    *   `mode: str` - Instruction mode that failed
    *   Example: `(FileNotFoundError("Template not found"), ExamType.GMAT, QuestionType.DATA_SUFFICIENCY, "questionSolution")`
*   **↩️ Returns**: None (logging function)
*   **📲 Called By**:
    *   `core/instructions/instruction_manager.py:InstructionManager.get_instruction()` on errors
    *   Template loading error handlers
*   **➡️ Calls**: 
    *   `self.logger.error()` for error logging
    *   `time.time()` for timestamp

---

### `file_utils.py` 📁

**🎯 Purpose**: Centralized file operations providing safe JSON/text file handling, path management, and file system utilities.

#### **Function: `load_json_file`**
*   **🎯 Purpose**: Load JSON data from file with comprehensive error handling and UTF-8 encoding
*   **📥 Inputs**:
    *   `file_path: Union[str, Path]` - Path to the JSON file
    *   Example values: `"config/generators/gmat_generators.json"`, `Path("system_instructions/templates/metadata.json")`, `"nonexistent.json"`
*   **↩️ Returns**:
    *   `Optional[Dict[str, Any]]` - Loaded JSON data or None on failure
    *   Example: `{"generators": {"DS": "DataSufficiency"}}` for valid JSON file
    *   Example: `None` for missing file or malformed JSON
*   **📲 Called By**:
    *   `core/instructions/instruction_loader.py:InstructionLoader.load_customizations()`
    *   `core/instructions/graph_style_manager.py:GraphStyleManager.load_graph_styles()`
    *   `core/prompts/base/base_prompt_generator.py:BasePromptGenerator.load_combinations()`
    *   Configuration loading throughout the system
*   **➡️ Calls**: 
    *   `json.load()` for file parsing
    *   File I/O operations with UTF-8 encoding

#### **Function: `save_json_file`**
*   **🎯 Purpose**: Save data to JSON file with formatting, directory creation, and error handling
*   **📥 Inputs**:
    *   `data: Dict[str, Any]` - Data to save
    *   `file_path: Union[str, Path]` - Path to save the file
    *   `indent: int` - JSON indentation level (default: 2)
    *   `ensure_dir: bool` - Whether to create directories (default: True)
    *   Example: `({"generated": "data"}, "output/results.json", 2, True)`
*   **↩️ Returns**:
    *   `bool` - Success status
    *   Example: `True` for successful save
    *   Example: `False` for permission errors or invalid path
*   **📲 Called By**:
    *   Generated paper saving in paper generation systems
    *   Configuration file updates
    *   Debug output saving
*   **➡️ Calls**: 
    *   `json.dump()` for file writing
    *   `pathlib.Path.mkdir()` for directory creation

#### **Function: `load_text_file`**
*   **🎯 Purpose**: Load text content from file with UTF-8 encoding and error handling
*   **📥 Inputs**:
    *   `file_path: Union[str, Path]` - Path to the text file
    *   Example values: `"system_instructions/templates/0-questionMetadata/0-passage.txt.template"`, `"README.md"`
*   **↩️ Returns**:
    *   `Optional[str]` - File content as string or None on failure
    *   Example: `"RESPONSE FORMAT:- JSON\n..."` for template files
    *   Example: `None` for missing files
*   **📲 Called By**:
    *   `core/instructions/instruction_loader.py:InstructionLoader.load_template()`
    *   Template file loading throughout instruction system
    *   Text-based configuration loading
*   **➡️ Calls**: 
    *   File I/O operations with UTF-8 encoding

#### **Function: `save_text_file`**
*   **🎯 Purpose**: Save text content to file with directory creation and error handling
*   **📥 Inputs**:
    *   `content: str` - Text content to save
    *   `file_path: Union[str, Path]` - Path to save the file
    *   `ensure_dir: bool` - Whether to create directories (default: True)
    *   Example: `("Generated question text", "output/question.txt", True)`
*   **↩️ Returns**:
    *   `bool` - Success status
    *   Example: `True` for successful save
    *   Example: `False` for write permission errors
*   **📲 Called By**:
    *   Log file creation
    *   Template generation output
    *   Text report generation
*   **➡️ Calls**: 
    *   File I/O operations with UTF-8 encoding
    *   `pathlib.Path.mkdir()` for directory creation

#### **Function: `get_project_root`**
*   **🎯 Purpose**: Get the project root directory for relative path calculations
*   **📥 Inputs**: None
*   **↩️ Returns**:
    *   `Path` - Path to project root directory
    *   Example: `Path("/Users/tanmaykumar/Desktop/QGen-py-compex")`
*   **📲 Called By**:
    *   `get_data_directory()`, `get_config_directory()`, `get_papers_directory()` for path calculation
    *   Relative path resolution throughout the system
*   **➡️ Calls**: 
    *   `pathlib.Path` operations for path manipulation

#### **Function: `get_config_directory`**
*   **🎯 Purpose**: Get standardized path to configuration directory
*   **📥 Inputs**: None
*   **↩️ Returns**:
    *   `Path` - Path to config directory
    *   Example: `Path("/Users/tanmaykumar/Desktop/QGen-py-compex/config")`
*   **📲 Called By**:
    *   Configuration file loading utilities
    *   System initialization routines
*   **➡️ Calls**: 
    *   `get_project_root()` for base path calculation

#### **Function: `get_papers_directory`**
*   **🎯 Purpose**: Get standardized path to generated papers output directory
*   **📥 Inputs**: None
*   **↩️ Returns**:
    *   `Path` - Path to papers directory
    *   Example: `Path("/Users/tanmaykumar/Desktop/QGen-py-compex/papers")`
*   **📲 Called By**:
    *   Paper generation output in mock generators
    *   Paper file management utilities
*   **➡️ Calls**: 
    *   `get_project_root()` for base path calculation

#### **Function: `find_files_by_pattern`**
*   **🎯 Purpose**: Find files matching glob pattern in directory for template discovery
*   **📥 Inputs**:
    *   `directory: Union[str, Path]` - Directory to search in
    *   `pattern: str` - Glob pattern to match
    *   Example: `("system_instructions/templates", "*.txt.template")`, `("config/generators", "*.json")`
*   **↩️ Returns**:
    *   `List[Path]` - List of matching file paths
    *   Example: `[Path("system_instructions/templates/0-questionMetadata/0-passage.txt.template"), ...]`
*   **📲 Called By**:
    *   Template discovery in instruction system
    *   Configuration file scanning
    *   File pattern matching utilities
*   **➡️ Calls**: 
    *   `pathlib.Path.glob()` for pattern matching

---

### `options_converter.py` 🔄

**🎯 Purpose**: Convert between dictionary and list option formats used by AI models versus database storage systems.

#### **Function: `convert_dict_options_to_list`**
*   **🎯 Purpose**: Convert AI-friendly dictionary format options to database-compatible list format
*   **📥 Inputs**:
    *   `options_dict: Dict[str, str]` - Dictionary with format {"A": "option1", "B": "option2", ...}
    *   `answer_keys: Union[str, List[str]]` - Answer key(s) like "A" or ["A", "C"]
    *   Example: `({"A": "15", "B": "20", "C": "25"}, "A")`, `({"A": "Red", "B": "Blue", "C": "Green"}, ["A", "C"])`
*   **↩️ Returns**:
    *   `Tuple[List[str], Union[str, List[str]]]` - Tuple of (options_list, answer_values)
    *   Example: `(["15", "20", "25"], "15")` for single answer
    *   Example: `(["Red", "Blue", "Green"], ["Red", "Green"])` for multiple answers
*   **📲 Called By**:
    *   Question generators when saving to database
    *   Legacy compatibility layer
    *   Format standardization utilities
*   **➡️ Calls**: No external function calls

#### **Function: `convert_list_options_to_dict`**
*   **🎯 Purpose**: Convert database list format options to AI-compatible dictionary format
*   **📥 Inputs**:
    *   `options_list: List[str]` - List of option texts
    *   `answer_values: Union[str, List[str]]` - Answer value(s) like "option1" or ["option1", "option3"]
    *   `start_letter: str` - Starting letter for keys (default: "A")
    *   Example: `(["15", "20", "25"], "15", "A")`, `(["Red", "Blue"], ["Red"], "A")`
*   **↩️ Returns**:
    *   `Tuple[Dict[str, str], Union[str, List[str]]]` - Tuple of (options_dict, answer_keys)
    *   Example: `({"A": "15", "B": "20", "C": "25"}, "A")` for single answer
    *   Example: `({"A": "Red", "B": "Blue"}, ["A"])` for multiple answers
*   **📲 Called By**:
    *   Question data loading from database
    *   AI model input preparation
    *   Legacy data migration utilities
*   **➡️ Calls**: No external function calls

#### **Function: `ensure_options_list_format`**
*   **🎯 Purpose**: Ensure options are in list format for database compatibility regardless of input format
*   **📥 Inputs**:
    *   `options: Any` - Options in any format (dict or list)
    *   `answer: Any` - Answer in any format
    *   Example: `({"A": "option1", "B": "option2"}, "A")`, `(["option1", "option2"], "option1")`
*   **↩️ Returns**:
    *   `Tuple[List[str], Any]` - Tuple of (options_list, converted_answer)
    *   Example: `(["option1", "option2"], "option1")` for both input types
*   **📲 Called By**:
    *   Database storage preparation
    *   Data normalization utilities
    *   Legacy system compatibility
*   **➡️ Calls**: 
    *   `convert_dict_options_to_list()` for dictionary inputs

#### **Function: `ensure_options_dict_format`**
*   **🎯 Purpose**: Ensure options are in dictionary format for AI compatibility regardless of input format
*   **📥 Inputs**:
    *   `options: Any` - Options in any format (dict or list)
    *   `answer: Any` - Answer in any format
    *   Example: `(["option1", "option2"], "option1")`, `({"A": "option1"}, "A")`
*   **↩️ Returns**:
    *   `Tuple[Dict[str, str], Any]` - Tuple of (options_dict, converted_answer)
    *   Example: `({"A": "option1", "B": "option2"}, "A")` for both input types
*   **📲 Called By**:
    *   AI model input preparation
    *   Question generation preprocessing
    *   Format standardization for AI requests
*   **➡️ Calls**: 
    *   `convert_list_options_to_dict()` for list inputs

#### **Function: `validate_options_format`**
*   **🎯 Purpose**: Validate options and answer format for consistency and correctness
*   **📥 Inputs**:
    *   `options: Any` - Options to validate
    *   `answer: Any` - Answer to validate
    *   Example: `({"A": "option1", "B": "option2"}, "A")`, `(["option1"], "missing")`, `({}, "A")`
*   **↩️ Returns**:
    *   `Tuple[bool, str]` - Tuple of (is_valid, error_message)
    *   Example: `(True, "Valid format")` for correct format
    *   Example: `(False, "Answer key 'C' not found in options")` for invalid answer
*   **📲 Called By**:
    *   Question data validation before processing
    *   Quality assurance checks
    *   Input validation in question generators
*   **➡️ Calls**: No external function calls

---

## 🔗 Inter-Utility Dependencies

**Data Relationships**:

1. **api_utils** → **json_utils**: `APIRequestHandler.make_request()` imports `JSON_ERROR_WARNING` for error message formatting
2. **validation_utils** → **core.enums.*****: Imports all enum types (`ExamType`, `QuestionType`, `SectionType`, `DifficultyLevel`) for input validation
3. **debug_utils** → **core.enums.*****: Imports `ExamType` and `QuestionType` for debug file organization
4. **logging_utils** → **core.enums.*****: Imports `ExamType` and `QuestionType` for structured logging context
5. **json_utils** → **tags_char.json**: Loads mathematical symbol mapping for LaTeX conversion

**Cross-References**:
- All utilities are imported by `core/utilities/__init__.py` for centralized access
- `question_components.py` imports multiple utilities: `json_utils.refine_response`, `validation_utils.validate_prompt`, `debug_utils.log_system_instruction`
- File utilities are used by instruction system components for template loading
- Logging utilities are used throughout the instruction and mock generation systems

---

## 🏗️ System Integration Points

**API Management**: `api_utils.py` provides centralized API client creation, key rotation, and rate limiting for all question generation
**Data Processing**: `json_utils.py` handles all AI response processing with LaTeX conversion and character tag replacement
**Input Validation**: `validation_utils.py` provides comprehensive validation for all system inputs and generated data
**Debugging Support**: `debug_utils.py` enables systematic debugging of system instruction issues and generation failures
**Logging Infrastructure**: `logging_utils.py` provides structured logging across all system components
**File Operations**: `file_utils.py` handles all file I/O operations with consistent error handling and path management
**Format Conversion**: `options_converter.py` bridges the gap between AI model formats and database storage requirements
**Mathematical Notation**: `tags_char.json` enables proper rendering of mathematical symbols in generated questions

**External Dependencies**: Google Gemini AI SDK, Python standard library (json, os, re, time, threading, logging, pathlib)
**Security Features**: Input sanitization, path validation, API key format validation, dangerous pattern detection