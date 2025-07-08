# 🧵 Threading and Concurrency Management

This directory contains the threading infrastructure for concurrent question generation, providing thread pool management, API rate limiting, and resource coordination for scalable exam paper generation.

---

## 📊 Data Flow and Manipulation

**🎯 Purpose**: This module manages concurrent execution of question generation tasks with intelligent API rate limiting, resource management, and error recovery to maximize throughput while respecting API quotas and system constraints.

**Flow**: Configuration setup → Thread pool initialization → Task distribution → API state management → Concurrent execution → Resource cleanup → Result aggregation

---

## 📁 File Structure and Components

### `api_thread_pool_manager.py` 🏗️

**🎯 Purpose**: Central thread pool manager that coordinates concurrent question generation with intelligent API management and resource optimization.

#### **Class: `APIThreadPoolManager`**
*   **🎯 Purpose**: Main thread pool coordinator handling concurrent task execution with API rate limiting and resource management
*   **✨ Key Attributes**:
    *   `config: ThreadConfig` - Thread pool configuration and settings
    *   `paper: Dict[str, Any]` - Generated paper data structure being populated
    *   `executor: ThreadPoolExecutor` - Python concurrent executor instance
    *   `futures: List[Future]` - Active task futures tracking
    *   `api_states: List[APIState]` - Per-API state tracking objects
    *   `locks: List[threading.Lock]` - Thread synchronization locks per API
    *   `logger: logging.Logger` - Structured logging instance

#### **Method: `__init__`**
*   **🎯 Purpose**: Initialize thread pool with configuration, paper structure, and API state management
*   **📥 Inputs**:
    *   `config: ThreadConfig` - Thread pool configuration object
    *   `paper: Optional[Dict[str, Any]]` - Optional existing paper structure (default: None)
    *   Example: `(ThreadConfig(max_workers=8, exam_type=ExamType.GMAT), None)`
*   **↩️ Returns**: None (constructor)
*   **📲 Called By**:
    *   `core/mock/unified_mock_generator.py:UnifiedMockGenerator._setup_thread_pool()`
    *   `GMAT/Mock.py:initialize_thread_pool()`
    *   `GRE/Mock.py:initialize_thread_pool()`
*   **➡️ Calls**:
    *   `ThreadConfig.validate()` for configuration validation
    *   `PaperStructure.create_paper_dict()` for paper initialization
    *   `ThreadPoolExecutor()` for executor creation
    *   `_setup_api_states()` for API state initialization

#### **Method: `add_task`**
*   **🎯 Purpose**: Submit a question generation task to the thread pool with proper resource allocation
*   **📥 Inputs**:
    *   `task_factory: Callable` - Function that creates the generation task
    *   `*args: Any` - Arguments to pass to the task factory
    *   Example: `(create_question_generator, "DS - Algebra - Problem Solving - difficulty_level: 3", api_idx=0)`
*   **↩️ Returns**: None (async task submission)
*   **📲 Called By**:
    *   `core/mock/unified_mock_generator.py:UnifiedMockGenerator._generate_questions_parallel()`
    *   Question generation coordination methods
*   **➡️ Calls**:
    *   `self.executor.submit()` for task submission
    *   `_assign_api_instance()` for API allocation
    *   `_track_future()` for future management

#### **Method: `wait_for_completion`**
*   **🎯 Purpose**: Wait for all submitted tasks to complete with timeout and progress monitoring
*   **📥 Inputs**:
    *   `timeout: Optional[float]` - Maximum wait time in seconds (default: None for no timeout)
    *   Example values: `None`, `300.0`, `600.0`
*   **↩️ Returns**:
    *   `List[Any]` - Results from completed tasks
    *   Example: `[{"question": "...", "answer": "A"}, {"question": "...", "answer": "B"}]`
    *   Example: `[]` for timeout or all failed tasks
*   **📲 Called By**:
    *   `core/mock/unified_mock_generator.py:UnifiedMockGenerator.generate_mock_paper()`
    *   Paper generation completion handlers
*   **➡️ Calls**:
    *   `as_completed()` for future iteration
    *   `_handle_task_completion()` for result processing
    *   `_update_api_states()` for state management

#### **Method: `shutdown`**
*   **🎯 Purpose**: Gracefully shutdown thread pool with proper resource cleanup and task completion
*   **📥 Inputs**:
    *   `wait: bool` - Whether to wait for running tasks to complete (default: True)
    *   `timeout: Optional[float]` - Maximum shutdown wait time (default: None)
    *   Example combinations: `(True, 30.0)`, `(False, None)`
*   **↩️ Returns**: None (cleanup operation)
*   **📲 Called By**:
    *   `core/mock/unified_mock_generator.py:UnifiedMockGenerator.__del__()`
    *   Context manager exit methods
    *   Emergency shutdown handlers
*   **➡️ Calls**:
    *   `self.executor.shutdown(wait=wait)` for executor cleanup
    *   `_cancel_pending_tasks()` for task cancellation
    *   `_log_shutdown_summary()` for monitoring

#### **Method: `get_api_stats`**
*   **🎯 Purpose**: Retrieve comprehensive API usage statistics and performance metrics
*   **📥 Inputs**: None
*   **↩️ Returns**:
    *   `Dict[str, Any]` - API usage statistics and metrics
    *   Example: `{"total_requests": 245, "rate_limited_apis": 2, "average_response_time": 1.2, "success_rate": 0.94}`
*   **📲 Called By**:
    *   Monitoring and reporting systems
    *   Performance analysis tools
    *   Debug information collection
*   **➡️ Calls**:
    *   `_calculate_api_metrics()` for metric computation
    *   `_get_rate_limit_status()` for current status

---

### `thread_config.py` ⚙️

**🎯 Purpose**: Configuration classes for thread pool behavior, API management settings, and performance tuning parameters.

#### **Class: `APIState`**
*   **🎯 Purpose**: Track individual API instance state including request counts, rate limiting, and timing information
*   **✨ Key Attributes**:
    *   `start_time: float` - API session start timestamp
    *   `request_count: int` - Number of requests made in current window
    *   `last_request_time: Optional[float]` - Timestamp of last request
    *   `is_rate_limited: bool` - Current rate limiting status
    *   `rate_limit_reset_time: Optional[float]` - When rate limit resets

#### **Method: `reset_request_count`**
*   **🎯 Purpose**: Reset API request counting for new time window
*   **📥 Inputs**: None (instance method)
*   **↩️ Returns**: None (state modification)
*   **📲 Called By**:
    *   `APIThreadPoolManager._reset_api_window()` for window management
    *   Rate limiting reset logic
*   **➡️ Calls**:
    *   `time.time()` for current timestamp

#### **Method: `increment_request_count`**
*   **🎯 Purpose**: Increment request count and update timing information
*   **📥 Inputs**: None (instance method)
*   **↩️ Returns**: None (state modification)
*   **📲 Called By**:
    *   `APIThreadPoolManager._track_api_request()` for request tracking
    *   Before each API call execution
*   **➡️ Calls**:
    *   `time.time()` for timestamp update

#### **Method: `set_rate_limited`**
*   **🎯 Purpose**: Mark API as rate limited with optional reset time
*   **📥 Inputs**:
    *   `reset_time: Optional[float]` - When rate limit expires (default: None)
    *   Example values: `None`, `time.time() + 60`, `1725789600.0`
*   **↩️ Returns**: None (state modification)
*   **📲 Called By**:
    *   API error handlers when 429 responses received
    *   Rate limit detection logic
*   **➡️ Calls**: No external function calls

#### **Method: `to_dict`**
*   **🎯 Purpose**: Convert API state to dictionary format for backward compatibility
*   **📥 Inputs**: None (instance method)
*   **↩️ Returns**:
    *   `Dict[str, Any]` - Dictionary representation of API state
    *   Example: `{"start_time": 1725789540.123, "request_count": 15}`
*   **📲 Called By**:
    *   Legacy compatibility layers
    *   State serialization for persistence
*   **➡️ Calls**: No external function calls

#### **Class: `ThreadConfig`**
*   **🎯 Purpose**: Comprehensive configuration for thread pool behavior, API management, and performance tuning
*   **✨ Key Attributes**:
    *   `max_workers: int` - Maximum number of worker threads (default: 8)
    *   `exam_type: ExamType` - Target exam type for configuration (default: GMAT)
    *   `max_requests_per_minute: int` - API rate limit threshold (default: 60)
    *   `api_timeout_seconds: float` - API request timeout (default: 30.0)
    *   `request_delay_seconds: float` - Delay between requests (default: 1.0)
    *   `max_retries: int` - Maximum retry attempts (default: 3)
    *   `retry_delay_seconds: float` - Base retry delay (default: 2.0)
    *   `exponential_backoff: bool` - Enable exponential backoff (default: True)
    *   `shutdown_wait_timeout: float` - Shutdown timeout (default: 30.0)
    *   `enable_detailed_logging: bool` - Detailed logging flag (default: False)

#### **Method: `validate`**
*   **🎯 Purpose**: Validate all configuration values for correctness and consistency
*   **📥 Inputs**: None (instance method)
*   **↩️ Returns**:
    *   `bool` - True if configuration is valid
    *   Raises `ValueError` for invalid configurations
*   **📲 Called By**:
    *   `APIThreadPoolManager.__init__()` during initialization
    *   Configuration loading and validation systems
*   **➡️ Calls**: No external function calls

#### **Method: `create_gmat_config`**
*   **🎯 Purpose**: Create GMAT-optimized thread configuration with appropriate defaults
*   **📥 Inputs**:
    *   `max_workers: int` - Number of workers (default: 8)
    *   `**kwargs: Any` - Additional configuration overrides
    *   Example: `(max_workers=10, max_requests_per_minute=90)`
*   **↩️ Returns**:
    *   `ThreadConfig` - GMAT-optimized configuration instance
    *   Example: `ThreadConfig(max_workers=10, exam_type=ExamType.GMAT, max_requests_per_minute=90)`
*   **📲 Called By**:
    *   `GMAT/Mock.py:setup_threading_config()`
    *   GMAT-specific initialization systems
*   **➡️ Calls**:
    *   `ThreadConfig()` constructor with GMAT defaults

#### **Method: `create_gre_config`**
*   **🎯 Purpose**: Create GRE-optimized thread configuration with appropriate defaults
*   **📥 Inputs**:
    *   `max_workers: int` - Number of workers (default: 6)
    *   `**kwargs: Any` - Additional configuration overrides
    *   Example: `(max_workers=8, api_timeout_seconds=45.0)`
*   **↩️ Returns**:
    *   `ThreadConfig` - GRE-optimized configuration instance
    *   Example: `ThreadConfig(max_workers=8, exam_type=ExamType.GRE, api_timeout_seconds=45.0)`
*   **📲 Called By**:
    *   `GRE/Mock.py:setup_threading_config()`
    *   GRE-specific initialization systems
*   **➡️ Calls**:
    *   `ThreadConfig()` constructor with GRE defaults

#### **Class: `PaperStructure`**
*   **🎯 Purpose**: Generate exam-specific paper data structures for concurrent population
*   **✨ Key Attributes**:
    *   `exam_type: ExamType` - Target exam type for structure creation

#### **Method: `create_paper_dict`**
*   **🎯 Purpose**: Create empty paper structure dictionary for concurrent question addition
*   **📥 Inputs**: None (instance method)
*   **↩️ Returns**:
    *   `Dict[str, Any]` - Empty paper structure ready for population
    *   Example GMAT: `{"exam_type": "GMAT", "sections": {"quantitative": [], "verbal": [], "integrated_reasoning": []}, "metadata": {}}`
    *   Example GRE: `{"exam_type": "GRE", "sections": {"quantitative": [], "verbal": []}, "metadata": {}}`
*   **📲 Called By**:
    *   `APIThreadPoolManager.__init__()` for paper initialization
    *   Paper structure setup systems
*   **➡️ Calls**:
    *   `_get_exam_sections()` for section determination

---

### `exceptions.py` ⚠️

**🎯 Purpose**: Specialized exception classes for threading operations with contextual information and error recovery support.

#### **Class: `ThreadingException`**
*   **🎯 Purpose**: Base exception for all threading-related errors with context and timestamp tracking
*   **✨ Key Attributes**:
    *   `error_code: Optional[str]` - Machine-readable error code
    *   `context: Dict[str, Any]` - Additional error context information
    *   `timestamp: float` - Error occurrence timestamp

#### **Class: `APIThreadPoolException`**
*   **🎯 Purpose**: Exception for API thread pool operation failures with API-specific context
*   **✨ Key Attributes**:
    *   `api_idx: Optional[int]` - Index of the API that failed

#### **Method: `__init__`**
*   **🎯 Purpose**: Initialize API thread pool exception with specific API context
*   **📥 Inputs**:
    *   `message: str` - Human-readable error message
    *   `api_idx: Optional[int]` - API index that failed (default: None)
    *   `**kwargs: Any` - Additional context parameters
    *   Example: `("API request failed", api_idx=3, error_code="RATE_LIMIT")`
*   **↩️ Returns**: None (constructor)
*   **📲 Called By**:
    *   API error handling code throughout the threading system
    *   Rate limiting and timeout detection
*   **➡️ Calls**:
    *   `ThreadingException.__init__()` for base initialization

#### **Class: `ThreadExecutionException`**
*   **🎯 Purpose**: Exception for thread execution failures with thread identification
*   **✨ Key Attributes**:
    *   `thread_id: Optional[str]` - Identifier of the thread that failed

#### **Class: `APIRateLimitException`**
*   **🎯 Purpose**: Specific exception for API rate limit violations with retry timing information
*   **✨ Key Attributes**:
    *   `api_idx: Optional[int]` - API index that hit rate limit
    *   `retry_after: Optional[float]` - Seconds to wait before retry

#### **Method: `__init__`**
*   **🎯 Purpose**: Initialize rate limit exception with retry timing information
*   **📥 Inputs**:
    *   `message: str` - Human-readable error message
    *   `api_idx: Optional[int]` - API index that hit limit (default: None)
    *   `retry_after: Optional[float]` - Seconds until retry allowed (default: None)
    *   `**kwargs: Any` - Additional context parameters
    *   Example: `("Rate limit exceeded", api_idx=2, retry_after=60.0, error_code="QUOTA_EXCEEDED")`
*   **↩️ Returns**: None (constructor)
*   **📲 Called By**:
    *   Rate limiting detection and enforcement code
    *   API response handlers for 429 status codes
*   **➡️ Calls**:
    *   `ThreadingException.__init__()` for base initialization

#### **Class: `ThreadPoolShutdownException`**
*   **🎯 Purpose**: Exception for thread pool shutdown operation failures

#### **Class: `TaskSubmissionException`**
*   **🎯 Purpose**: Exception for task submission failures to thread pool
*   **✨ Key Attributes**:
    *   `task_name: Optional[str]` - Name of the task that failed to submit

---

## 🔄 Threading Workflow Integration

### **Resource Management**
- **API Allocation**: Dynamic allocation of API instances to worker threads with load balancing
- **Rate Limiting**: Intelligent rate limiting per API instance with automatic backoff
- **Memory Management**: Proper cleanup of thread resources and future objects
- **Error Recovery**: Graceful handling of API failures with automatic retry logic

### **Performance Optimization**
- **Concurrent Execution**: Parallel question generation maximizing API throughput
- **Load Balancing**: Even distribution of tasks across available worker threads
- **Resource Utilization**: Optimal utilization of system resources and API quotas
- **Monitoring Integration**: Real-time performance monitoring and metrics collection

### **Error Handling and Recovery**
- **Exception Hierarchy**: Structured exception system for specific error handling
- **Retry Logic**: Exponential backoff retry mechanisms for transient failures
- **Graceful Degradation**: System continues operation with reduced capacity during failures
- **State Recovery**: Automatic recovery of API states after error conditions

This threading system provides robust, scalable concurrent execution for question generation while maintaining reliability, performance, and proper resource management across the entire system.