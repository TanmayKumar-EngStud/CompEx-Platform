
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from GMAT.Integrated_Reasoning.files.MSR import Generate_MSR
from unittest.mock import Mock

def test_msr_prompt_generation():
    mock_global_state = Mock()
    mock_lock = Mock()
    prompt = "MSR - <total_child_questions: 3> - <Logistics and Supply Chain> - <comparison_table> - <bar_chart> - <bar_chart> - <Critical Reasoning/Logical Reasoning/Data Interpretation> - <Dichotomous Choice(Acceptable/Not Acceptable)/Dichotomous Choice(Inferable/Not Inferable)/Dichotomous Choice(Yes/No)> - <difficulty_level: 2>"
    
    msr_generator = Generate_MSR(
        global_state=mock_global_state,
        lock=mock_lock,
        api_IDX=0,
        prompt=prompt
    )
    
    # This will call the patched generate_SourceInfo
    msr_generator.generate_question()

if __name__ == "__main__":
    test_msr_prompt_generation()
