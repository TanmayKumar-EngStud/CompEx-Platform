# 📜 README.md and Interaction Rules

This document outlines the conventions and expectations for all `README.md` files within this project, as well as the protocol for interaction with the Gemini CLI agent. Adhering to these rules ensures clarity, consistency, and efficient collaboration.

---

## 📁 `README.md` File Conventions

Every single folder and subfolder in this project **must** contain a `README.md` file. These files serve as the **single source of truth** for understanding the codebase.

### 📄 Low-Level `README.md` (Next to Files)

When a `README.md` file is placed directly within a folder containing code files (and no further subfolders that would have their own `README.md`), it must provide granular detail for each function/class within those files.

*   **Data Manipulation**: Clearly explain *how* data is being manipulated, stored, or fetched by the functions/classes.
*   **Function/Class Details**: For each significant function or class:
    *   **Name**: Explicitly state the name of the function or class.
    *   **🎯 Purpose**: A concise description of what the function/class does.
    *   **📥 Inputs**:
        *   Data type of each input parameter.
        *   Concrete example values for each input parameter.
        *   **All cases**: If there are different scenarios or edge cases for inputs, list them all with corresponding example values.
    *   **↩️ Returns**:
        *   Data type of the output.
        *   Concrete example values for the output.
        *   **All cases**: If there are different scenarios or edge cases for outputs, list them all with corresponding example values.
    *   **📲 Called By**: List the specific functions (and their respective files) that call this function/class.
    *   **➡️ Calls**: List the specific functions (and their respective files) that this function/class calls.
*   **Completeness**: Always list *all* relevant names (e.g., all enum values, all class methods), avoiding generalizations like "and many more" or "etc."

### 🌳 High-Level `README.md` (In Folders with Subfolders)

When a `README.md` file is placed in a folder that contains multiple subfolders (each with their own `README.md`), it should provide a more abstract overview.

*   **Abstracted Functionality**: Describe the higher-order functionality present within the folder.
*   **Data Flow Overview**: Explain how various types of data flow *between* the subfolders, rather than detailing internal manipulation within individual files.
*   **Subfolder Summaries**: Briefly summarize the purpose of each subfolder.

---

## 🤖 Interaction Protocol with Gemini CLI Agent

When requesting the Gemini CLI agent to perform tasks, especially code modifications or documentation creation, the following protocol will be strictly followed:

1.  **Understanding the Change**: The agent will first read the relevant `README.md` files to understand the current implementation and context.
2.  **Plan Proposal**: The agent will then propose a detailed plan for how it intends to resolve the task, including:
    *   What changes will be made.
    *   Which files will be affected.
    *   How the changes align with existing conventions.
    *   Any necessary updates to tests or documentation.
3.  **User Approval**: The agent will present the plan to the user for approval.
    *   The user will either approve the plan or provide corrections/alternative instructions.
    *   The agent **must wait for explicit approval** before proceeding with any file modifications.
4.  **Test Modification**: If applicable, the agent will first modify the relevant testing files (in the `/.testing` folder or sub-directory specific `.testing` folders) to properly test the new or modified functionality.
5.  **Code Modification**: The agent will then modify the actual code files.
6.  **Test Execution**: After code modification, the agent will run the relevant tests (unit and/or integration) to verify the changes.
7.  **Documentation Update**: If tests are successful, the agent will update the respective `README.md` file(s) to reflect the new functionality, adhering to the detailed content rules above.
8.  **Integration Testing**: If the change is significant (e.g., impacts multiple modules or core logic), the agent will propose running integration tests.

---

## 🎨 Emoji Usage Guidelines

To enhance readability and quick comprehension, the following emojis will be used consistently in `README.md` files and agent interactions:

*   **🎯 Purpose**: Used to denote the primary goal or function.
*   **📥 Inputs**: Used to indicate input parameters or data.
*   **↩️ Returns**: Used to indicate return values or output data.
*   **📲 Called By**: Used to indicate which functions or modules invoke the current function/class.
*   **➡️ Calls**: Used to indicate which functions or modules the current function/class calls.
*   **📦 Wraps**: Used to indicate that a class or function is an adapter or wrapper around another.
*   **✨ Key Attributes**: Used to highlight important properties or characteristics.
*   **Example**: Used to introduce code examples or data flow examples.
*   **Flow**: Used to illustrate the sequence of operations or data movement.

---

## 💬 Chat Flow Management

*   The agent will focus on completing one `README.md` file per chat interaction.
*   Before concluding a chat interaction, the agent will inform the user which folder it intends to document next, allowing the user to prioritize.
