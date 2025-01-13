from concurrent.futures import ThreadPoolExecutor
from typing import List, Dict, Any
import json
from GMAT.Integrated_Reasoning.IR import GMAT_IR
from GMAT.Quants.Quants import GMAT_Q
from GMAT.Verbal.Verbal import GMAT_V
from GRE.Quants.Quants import GRE_Q
from GRE.Verbal.Verbal import GRE_V

class QuestionGenerator:
    def __init__(self):
        self.GMAT_IR = GMAT_IR()
        self.GMAT_Q = GMAT_Q()
        self.GMAT_V = GMAT_V()
        self.GRE_Q = GRE_Q()
        self.GRE_V = GRE_V()
        
    def generate_question_with_retry(self, generator) -> Dict[str, Any]:
        max_retries = 3
        for attempt in range(max_retries):
            try:
                if isinstance(generator, (GMAT_IR, GMAT_Q, GMAT_V, GRE_Q, GRE_V)):
                    return generator.generate_questions()
                else:
                    raise ValueError(f"Unsupported generator type: {type(generator)}")
            except Exception as e:
                if attempt == max_retries - 1:
                    print(f"Failed to generate question after {max_retries} attempts: {str(e)}")
                    return {"error": str(e)}
                print(f"Attempt {attempt + 1} failed, retrying...")
                continue
        return {"error": "Max retries exceeded"}

    def generate_questions(self) -> Dict[str, List[Dict[str, Any]]]:
        results = {
            "GMAT_IR": [],
            "GMAT_Q": [],
            "GMAT_V": [], 
            "GRE_Q": [],
            "GRE_V": []
        }

        with ThreadPoolExecutor() as executor:
            # Generate GMAT IR questions
            ir_futures = [
                executor.submit(self.generate_question_with_retry, self.GMAT_IR)
            ]
            
            # Generate GMAT Quant questions
            gmat_q_futures = [
                executor.submit(self.generate_question_with_retry, self.GMAT_Q)
            ]

            # Generate GMAT Verbal questions  
            gmat_v_futures = [
                executor.submit(self.generate_question_with_retry, self.GMAT_V)
            ]

            # Generate GRE Quant questions
            gre_q_futures = [
                executor.submit(self.generate_question_with_retry, self.GRE_Q)
            ]

            # Generate GRE Verbal questions
            gre_v_futures = [
                executor.submit(self.generate_question_with_retry, self.GRE_V)
            ]

            # Collect results
            results["GMAT_IR"] = [f.result() for f in ir_futures]
            results["GMAT_Q"] = [f.result() for f in gmat_q_futures]
            results["GMAT_V"] = [f.result() for f in gmat_v_futures]
            results["GRE_Q"] = [f.result() for f in gre_q_futures]
            results["GRE_V"] = [f.result() for f in gre_v_futures]

        return results

def main():
    generator = QuestionGenerator()
    results = generator.generate_questions()
    print("Question generation completed")
    return results

if __name__ == "__main__":
    questions = main()
    print(f"Here are the list of questions that are generated: \n {json.dumps(questions, indent=2)}")
