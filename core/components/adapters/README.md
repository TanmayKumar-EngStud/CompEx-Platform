# 🔌 Component Adapters

This directory contains exam-specific adapter classes that bridge the gap between the unified core question components and the legacy exam-specific function names and data structures expected by existing GMAT and GRE question generators. These adapters ensure backward compatibility while enabling the use of modern unified components.

---

## 📊 Data Flow and Purpose

**🎯 Purpose**: These adapters act as **translators** that wrap unified question components (`core/components/question_components.py`) and expose them with the exact function names, parameters, and return formats expected by legacy exam-specific generators in `GMAT/` and `GRE/` directories.

**Flow**: Legacy generator calls → Adapter method → Unified core component → Processed result → Legacy-compatible output format

---

## 📁 Adapter Files

### `gmat_adapter.py` 🦁

**🎯 Purpose**: Provides GMAT-specific adapters that wrap unified components for seamless integration with existing GMAT question generation workflow.

#### **Class: `GMATAdapter`**
*   **🎯 Purpose**: Factory class for creating GMAT-specific component adapters
*   **📥 Inputs**: None (static factory methods)
*   **↩️ Returns**: Configured adapter instances for specific question types
*   **📲 Called By**: 
    *   `GMAT/Quants/files/simpleQuestionGeneration.py:SimpleQuestionGeneration.__init__()`
    *   `GMAT/Quants/files/dataSufficiencyQuestionGeneration.py:DataSufficiencyQuestionGeneration.__init__()`
    *   `GMAT/Verbal/files/parentChildQuestionGeneration.py:ParentChildQuestionGeneration.__init__()`
*   **➡️ Calls**: Adapter constructors for each question type

#### **Class: `GMATSimpleQuestionAdapter`**
*   **🎯 Purpose**: Adapts `SimpleQuestion` for GMAT Problem Solving and Critical Reasoning questions
*   **✨ Key Attributes**: 
    *   `component: SimpleQuestion` - Wrapped unified component

#### **Method: `generate_QuestionPassage`**
*   **🎯 Purpose**: Generate question passage/argument for Critical Reasoning (GMAT naming convention)
*   **📥 Inputs**: None
*   **↩️ Returns**: 
    *   `str` - Generated passage text
    *   Example: `"A study conducted by researchers at Stanford University found that companies implementing flexible work schedules saw a 25% increase in employee productivity..."`
*   **📲 Called By**: 
    *   `GMAT/Verbal/files/simpleQuestionGeneration.py:SimpleQuestionGeneration.generate_QuestionPassage()`
*   **➡️ Calls**: 
    *   `self.component.generate_question_passage()` from `core/components/question_components.py:SimpleQuestion`

#### **Method: `generate_questionText`**
*   **🎯 Purpose**: Generate question text (GMAT naming convention)
*   **📥 Inputs**: 
    *   `input_data: Optional[str]` - Optional input data for context (default: None)
    *   Example values: `None`, `"Given the information above..."`, `"Based on the passage..."`
*   **↩️ Returns**: 
    *   `str` - Generated question text
    *   Example: `"Which of the following best describes the main conclusion of the study mentioned in the passage?"`
*   **📲 Called By**: 
    *   `GMAT/Quants/files/simpleQuestionGeneration.py:SimpleQuestionGeneration.generate_questionText()`
    *   `GMAT/Verbal/files/simpleQuestionGeneration.py:SimpleQuestionGeneration.generate_questionText()`
*   **➡️ Calls**: 
    *   `self.component.generate_question_text(input_data)` from `core/components/question_components.py:SimpleQuestion`

#### **Method: `generate_questionTitle`**
*   **🎯 Purpose**: Generate question title (GMAT naming convention)
*   **📥 Inputs**: None
*   **↩️ Returns**: 
    *   `str` - Generated question title
    *   Example: `"Critical Reasoning - Strengthen"`
    *   Example: `"Problem Solving - Geometry"`
*   **📲 Called By**: 
    *   All GMAT question generators for title generation
*   **➡️ Calls**: 
    *   `self.component.generate_question_title()` from `core/components/question_components.py:SimpleQuestion`

#### **Method: `generate_questionSolution`**
*   **🎯 Purpose**: Generate question solution (GMAT naming convention)
*   **📥 Inputs**: None
*   **↩️ Returns**: 
    *   `str` - Generated solution explanation (plain text)
    *   Example: `"To solve this problem, we need to find the area of the triangle. Using the formula A = (1/2) × base × height, we get A = (1/2) × 8 × 6 = 24 square units."`
*   **📲 Called By**: 
    *   All GMAT question generators for solution generation
*   **➡️ Calls**: 
    *   `self.component.generate_question_solution(is_numeric_entry=False)` from `core/components/question_components.py:SimpleQuestion`

#### **Method: `generate_questionOptions`**
*   **🎯 Purpose**: Generate question options (GMAT naming convention)
*   **📥 Inputs**: None
*   **↩️ Returns**: 
    *   `Tuple[List[str], str]` - Tuple of (options_list, correct_answer)
    *   Example: `(["24", "36", "48", "52", "64"], "24")`
*   **📲 Called By**: 
    *   All GMAT multiple choice question generators
*   **➡️ Calls**: 
    *   `self.component.generate_question_options()` from `core/components/question_components.py:SimpleQuestion`

#### **Class: `GMATDataSufficiencyAdapter`**
*   **🎯 Purpose**: Adapts `DataSufficiencyQuestion` for GMAT Data Sufficiency questions
*   **✨ Key Attributes**: 
    *   `component: DataSufficiencyQuestion` - Wrapped unified component

#### **Method: `generate_questionGraph`**
*   **🎯 Purpose**: Generate question graph/table for visual data
*   **📥 Inputs**: None
*   **↩️ Returns**: 
    *   `Optional[Dict[str, Any]]` - Graph data or None if not needed
    *   Example: `{"type": "bar_chart", "data": {"x": [1,2,3], "y": [10,20,30]}, "title": "Sales Data"}`
    *   Example: `None` for non-visual questions
*   **📲 Called By**: 
    *   `GMAT/Quants/files/dataSufficiencyQuestionGeneration.py:DataSufficiencyQuestionGeneration.generate_questionGraph()`
*   **➡️ Calls**: 
    *   `self.component.generate_question_graph()` from `core/components/question_components.py:DataSufficiencyQuestion`

#### **Method: `generate_questionText`**
*   **🎯 Purpose**: Generate question text components for data sufficiency
*   **📥 Inputs**: None
*   **↩️ Returns**: 
    *   `Tuple[Optional[str], Optional[List[str]], Optional[str]]` - Tuple of (passage, statements, question)
    *   Example: `("Company X reported the following quarterly results...", ["Statement (1): Revenue increased by 15%", "Statement (2): Expenses decreased by 8%"], "Is Company X's profit margin greater than 20%?")`
    *   Example: `(None, ["Statement (1): x > 5", "Statement (2): x < 10"], "What is the value of x?")` for pure DS
*   **📲 Called By**: 
    *   `GMAT/Quants/files/dataSufficiencyQuestionGeneration.py:DataSufficiencyQuestionGeneration.generate_questionText()`
*   **➡️ Calls**: 
    *   `self.component.generate_question_text()` from `core/components/question_components.py:DataSufficiencyQuestion`

#### **Method: `generate_questionOptions`**
*   **🎯 Purpose**: Generate question options and answer for data sufficiency
*   **📥 Inputs**: None
*   **↩️ Returns**: 
    *   `Tuple[Dict[str, str], str]` - Tuple of (options_dict, correct_answer_key)
    *   Example: `({"A": "Statement (1) ALONE is sufficient", "B": "Statement (2) ALONE is sufficient", "C": "BOTH statements TOGETHER are sufficient", "D": "EACH statement ALONE is sufficient", "E": "Statements (1) and (2) TOGETHER are NOT sufficient"}, "C")`
*   **📲 Called By**: 
    *   `GMAT/Quants/files/dataSufficiencyQuestionGeneration.py:DataSufficiencyQuestionGeneration.generate_questionOptions()`
*   **➡️ Calls**: 
    *   `self.component.generate_question_options_with_answer()` from `core/components/question_components.py:DataSufficiencyQuestion`

#### **Class: `GMATParentChildAdapter`**
*   **🎯 Purpose**: Adapts `ParentChildQuestion` for GMAT Reading Comprehension questions
*   **✨ Key Attributes**: 
    *   `component: ParentChildQuestion` - Wrapped unified component

#### **Method: `generate_parentQuestion`**
*   **🎯 Purpose**: Generate parent question (passage content)
*   **📥 Inputs**: None
*   **↩️ Returns**: 
    *   `Optional[str]` - Generated reading comprehension passage
    *   Example: `"The emergence of artificial intelligence in the workplace has fundamentally altered the landscape of modern business operations. Companies across various industries are increasingly integrating AI technologies to streamline processes, enhance decision-making capabilities, and improve overall efficiency. However, this technological revolution has also raised significant concerns about job displacement and the future of human employment..."`
*   **📲 Called By**: 
    *   `GMAT/Verbal/files/parentChildQuestionGeneration.py:ParentChildQuestionGeneration.generate_parentQuestion()`
*   **➡️ Calls**: 
    *   `self.component.generate_parent_question()` from `core/components/question_components.py:ParentChildQuestion`

#### **Method: `generate_childQuestion`**
*   **🎯 Purpose**: Generate child question text for a specific index
*   **📥 Inputs**: 
    *   `index: int` - Index of the child question (0-based)
    *   `child_prompt: str` - Optional specific prompt for this child (default: "")
    *   Example combinations: `(0, "")`, `(1, "main idea")`, `(2, "author's tone")`
*   **↩️ Returns**: 
    *   `Optional[str]` - Generated child question text
    *   Example: `"Which of the following best describes the primary purpose of the passage?"`
    *   Example: `"The author's attitude toward AI implementation can best be characterized as:"`
*   **📲 Called By**: 
    *   `GMAT/Verbal/files/parentChildQuestionGeneration.py:ParentChildQuestionGeneration.generate_childQuestion()`
*   **➡️ Calls**: 
    *   `self.component.generate_child_question(index, child_prompt)` from `core/components/question_components.py:ParentChildQuestion`

#### **Method: `generate_childOptions`**
*   **🎯 Purpose**: Generate child question options for a specific index
*   **📥 Inputs**: 
    *   `index: int` - Index of the child question
    *   Example values: `0`, `1`, `2`, `3`
*   **↩️ Returns**: 
    *   `Tuple[Optional[List[str]], Optional[str]]` - Tuple of (options_list, correct_answer)
    *   Example: `(["To advocate for increased AI adoption", "To warn about the dangers of AI", "To provide a balanced view of AI implementation", "To criticize current business practices"], "To provide a balanced view of AI implementation")`
*   **📲 Called By**: 
    *   `GMAT/Verbal/files/parentChildQuestionGeneration.py:ParentChildQuestionGeneration.generate_childOptions()`
*   **➡️ Calls**: 
    *   `self.component.generate_child_options(index)` from `core/components/question_components.py:ParentChildQuestion`

### `gre_adapter.py` 🦉

**🎯 Purpose**: Provides GRE-specific adapters that wrap unified components for seamless integration with existing GRE question generation workflow.

#### **Class: `GREAdapter`**
*   **🎯 Purpose**: Factory class for creating GRE-specific component adapters
*   **📥 Inputs**: None (static factory methods)
*   **↩️ Returns**: Configured adapter instances for specific question types
*   **📲 Called By**: 
    *   `GRE/Quants/files/simpleQuestionGeneration.py:SimpleQuestionGeneration.__init__()`
    *   `GRE/Quants/files/dataSufficiencyQuestionGeneration.py:DataSufficiencyQuestionGeneration.__init__()`
    *   `GRE/Verbal/files/parentChildQuestionGeneration.py:ParentChildQuestionGeneration.__init__()`
*   **➡️ Calls**: Adapter constructors for each question type

#### **Class: `GRESimpleQuestionAdapter`**
*   **🎯 Purpose**: Adapts `SimpleQuestion` for GRE Quantitative Comparison, multiple choice, and Numeric Entry questions
*   **✨ Key Attributes**: 
    *   `component: SimpleQuestion` - Wrapped unified component

#### **Method: `generate_questionSolution`**
*   **🎯 Purpose**: Generate question solution with GRE-specific numeric entry handling
*   **📥 Inputs**: 
    *   `isNE: bool` - Whether this is a numeric entry question (default: False)
    *   Example values: `False` for regular questions, `True` for numeric entry
*   **↩️ Returns**: 
    *   `Union[str, Tuple[str, float]]` - Solution string for regular questions, or (solution, numeric_answer) tuple for NE
    *   Example regular: `"To find the probability, we calculate favorable outcomes divided by total outcomes: 3/12 = 1/4 = 0.25"`
    *   Example NE: `("The area of the circle is π × r² = π × 5² = 25π", 78.54)`
*   **📲 Called By**: 
    *   `GRE/Quants/files/simpleQuestionGeneration.py:SimpleQuestionGeneration.generate_questionSolution()`
    *   `GRE/Quants/files/numericEntryQuestionGeneration.py:NumericEntryQuestionGeneration.generate_questionSolution()`
*   **➡️ Calls**: 
    *   `self.component.generate_question_solution(is_numeric_entry=isNE)` from `core/components/question_components.py:SimpleQuestion`

#### **Method: `generate_questionOptions`**
*   **🎯 Purpose**: Generate question options with GRE-specific format
*   **📥 Inputs**: 
    *   `num_options: Optional[int]` - Number of options to generate (default: None for component default)
    *   Example values: `None` (use default), `4`, `5`
*   **↩️ Returns**: 
    *   `Tuple[Dict[str, str], str]` - Tuple of (options_dict, correct_answer_key)
    *   Example: `({"A": "Quantity A is greater", "B": "Quantity B is greater", "C": "The two quantities are equal", "D": "The relationship cannot be determined"}, "B")`
*   **📲 Called By**: 
    *   `GRE/Quants/files/simpleQuestionGeneration.py:SimpleQuestionGeneration.generate_questionOptions()`
*   **➡️ Calls**: 
    *   `self.component.generate_question_options()` from `core/components/question_components.py:SimpleQuestion`

#### **Class: `GREDataSufficiencyAdapter`**
*   **🎯 Purpose**: Adapts `DataSufficiencyQuestion` for GRE Data Sufficiency questions (legacy compatibility)
*   **✨ Key Attributes**: 
    *   `component: DataSufficiencyQuestion` - Wrapped unified component

#### **Method: `generate_questionSolution`**
*   **🎯 Purpose**: Generate question solution and answer with GRE-specific tuple format
*   **📥 Inputs**: None
*   **↩️ Returns**: 
    *   `Tuple[Optional[str], Optional[str]]` - Tuple of (solution_text, answer_key)
    *   Example: `("Statement (1) alone provides sufficient information because it establishes that x > 10, which combined with the given constraint x < 15, narrows the range to 10 < x < 15. Statement (2) alone is insufficient because...", "A")`
*   **📲 Called By**: 
    *   `GRE/Quants/files/dataSufficiencyQuestionGeneration.py:DataSufficiencyQuestionGeneration.generate_questionSolution()`
*   **➡️ Calls**: 
    *   `self.component.generate_question_solution()` from `core/components/question_components.py:DataSufficiencyQuestion`
    *   `self.component.generate_question_options_with_answer()` for answer extraction

#### **Class: `GREParentChildAdapter`**
*   **🎯 Purpose**: Adapts `ParentChildQuestion` for GRE Reading Comprehension and shared quantitative questions
*   **✨ Key Attributes**: 
    *   `component: ParentChildQuestion` - Wrapped unified component

#### **Method: `generate_passages`**
*   **🎯 Purpose**: Generate passages (parent content) for GRE reading comprehension
*   **📥 Inputs**: None
*   **↩️ Returns**: 
    *   `str` - Generated reading passage extracted from parent question metadata
    *   Example: `"Recent archaeological discoveries in the Amazon rainforest have challenged long-held assumptions about pre-Columbian civilizations in South America. Advanced LiDAR technology has revealed the existence of sophisticated urban settlements that were previously hidden beneath dense forest canopy..."`
*   **📲 Called By**: 
    *   `GRE/Verbal/files/parentChildQuestionGeneration.py:ParentChildQuestionGeneration.generate_passages()`
*   **➡️ Calls**: 
    *   `self.component.generate_question_metadata()` from `core/components/question_components.py:ParentChildQuestion`
    *   Extracts passage from returned metadata dictionary

---

## 🔄 Adapter Design Patterns

### **Method Name Translation**
- **GMAT Convention**: Mixed case with descriptive names (`generate_QuestionPassage`, `generate_questionText`)
- **GRE Convention**: Camel case with exam-specific parameters (`generate_questionSolution(isNE=True)`)
- **Unified Component**: Consistent snake_case with clear semantics (`generate_question_solution`)

### **Return Format Adaptation**
- **Legacy Format**: Various tuple and individual return types expected by existing generators
- **Unified Format**: Consistent dictionary-based returns from core components
- **Adapter Translation**: Extracts specific values from unified format and reshapes to legacy expectations

### **Parameter Compatibility**
- **Legacy Parameters**: Exam-specific parameter names and optional arguments
- **Unified Parameters**: Standardized parameter names across all exam types
- **Adapter Mapping**: Translates legacy parameter names to unified equivalents

---

## 🔗 Integration Points

**📲 Called By**: 
- Legacy question generators in `GMAT/` and `GRE/` directories
- Existing test suites expecting legacy function signatures
- Backward compatibility layer for gradual migration

**➡️ Calls**: 
- Unified components in `core/components/question_components.py`
- Core utilities for data processing and validation
- Shared system instructions and configuration

**🔄 Data Flow**: 
Legacy Generator Request → Adapter Method → Unified Component → Core Processing → Adapter Format Translation → Legacy Compatible Response

This adapter system enables seamless migration to unified components while maintaining complete backward compatibility with existing exam-specific generators and workflows.