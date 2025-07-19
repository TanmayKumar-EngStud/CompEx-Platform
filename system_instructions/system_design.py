"""
GMAT/GRE Question Generation System Data Flow Diagram

This script creates a detailed data flow diagram showing how data transforms through
specific functions in each file of the unified question generation system.

The diagram tracks actual data values and their transformations through the system,
with the ability to focus on specific question styles using the question_style variable.

INSTALLATION REQUIREMENTS:
1. Install Graphviz system dependency:
   - macOS: brew install graphviz
   - Ubuntu/Debian: sudo apt-get install graphviz
   - Windows: Download from https://graphviz.org/download/
   
2. Install Python dependencies:
   - pip install diagrams
   - pip install graphviz (Python wrapper)

ALTERNATIVE: If Graphviz is not available, the script will generate a text-based 
data flow representation instead.
"""

import json
import os
import sys

# Try to import diagrams, fall back to text output if not available
try:
    from diagrams import Cluster, Diagram
    from diagrams.generic.storage import Storage
    from diagrams.programming.language import Python
    from diagrams.generic.database import SQL
    DIAGRAMS_AVAILABLE = True
except ImportError:
    DIAGRAMS_AVAILABLE = False
    print("⚠️  diagrams library not available - will generate text-based output")

# Test if Graphviz is available
GRAPHVIZ_AVAILABLE = True
if DIAGRAMS_AVAILABLE:
    try:
        # Test if we can create a simple diagram
        import tempfile
        import shutil
        
        # Create temp directory for test
        temp_dir = tempfile.mkdtemp()
        test_path = os.path.join(temp_dir, "test_diagram")
        
        with Diagram("test", filename=test_path, show=False, direction="TB"):
            test_node = Storage("test")
        
        # Clean up test files
        shutil.rmtree(temp_dir, ignore_errors=True)
        
        print("✅ Graphviz is available and working!")
        
    except Exception as e:
        GRAPHVIZ_AVAILABLE = False
        print(f"⚠️  Graphviz not available: {e}")
        print("📋 Falling back to text-based output")

# Configuration variable to control which question style to display
question_style: str = "data_sufficiency"  # Options: "all", "data_sufficiency", "problem_solving", "reading_comprehension", "critical_reasoning", "graphic_interpretation", "table_analysis", "two_part_analysis", "multi_source_reasoning", "numeric_entry", "text_completion", "sentence_equivalence"

class DataFlowDiagram:
    """
    Creates a detailed data flow diagram for the GMAT/GRE question generation system.
    
    This diagram tracks how data transforms through specific functions in each file,
    showing actual data values and their transformations.
    """
    
    def __init__(self, question_style: str = "data_sufficiency"):
        """
        Initialize the data flow diagram generator.
        
        Args:
            question_style: Specific question style to track data flow for
        """
        self.question_style = question_style
        
        # Data transformation steps for each question style
        self.data_flow_steps = {
            'data_sufficiency': {
                'initial_data': {
                    'difficulty': 3,
                    'is_mock': True,
                    'exam_type': 'GMAT'
                },
                'steps': [
                    {
                        'file': 'main.py',
                        'function': '__init__',
                        'input': 'Initial System State',
                        'output': "{'difficulty': 3, 'is_mock': True}",
                        'transformation': 'Sets default values'
                    },
                    {
                        'file': 'main.py',
                        'function': 'generate_paper',
                        'input': "{'difficulty': 3, 'is_mock': True}",
                        'output': 'UnifiedMockGenerator(ExamType.GMAT, 3)',
                        'transformation': 'Creates generator instance'
                    },
                    {
                        'file': 'core/mock/unified_mock_generator.py',
                        'function': '__init__',
                        'input': 'ExamType.GMAT, difficulty=3',
                        'output': 'config = GMATConfig.from_difficulty(3)',
                        'transformation': 'Loads exam configuration'
                    },
                    {
                        'file': 'core/mock/unified_mock_generator.py',
                        'function': '_initialize_prompts_with_factory',
                        'input': 'GMATConfig with quants_total=21',
                        'output': 'prompts["quants"] = ["DS - <topic> - <skill> - <difficulty_level: 3>", ...]',
                        'transformation': 'Generates question prompts'
                    },
                    {
                        'file': 'core/prompts/gmat/gmat_quants_prompts.py',
                        'function': 'generate_question_prompts',
                        'input': 'section_type=QUANTITATIVE, difficulty=3',
                        'output': '"DS - <Arithmetic> - <Logical Reasoning> - <difficulty_level: 3>"',
                        'transformation': 'Creates specific DS prompt'
                    },
                    {
                        'file': 'core/mock/unified_mock_generator.py',
                        'function': 'generate_question_with_retry',
                        'input': 'prompt="DS - <Arithmetic> - <Logical Reasoning> - <difficulty_level: 3>"',
                        'output': 'generator_class = Q_DS_gen',
                        'transformation': 'Maps prompt to generator'
                    },
                    {
                        'file': 'core/factories/question_generator_factory.py',
                        'function': 'create_generator',
                        'input': 'question_type=DATA_SUFFICIENCY, section_type=QUANTITATIVE',
                        'output': 'DataSufficiencyGenerator instance',
                        'transformation': 'Creates specific generator'
                    },
                    {
                        'file': 'core/instructions/instruction_loader.py',
                        'function': 'load_template',
                        'input': 'question_type=DATA_SUFFICIENCY, mode="questionText"',
                        'output': 'Template content from 1-questionText/1-data_sufficiency.txt.template',
                        'transformation': 'Loads DS-specific template'
                    },
                    {
                        'file': 'core/instructions/template_processor.py',
                        'function': 'process_template',
                        'input': 'template + prompt variables',
                        'output': 'Processed instruction with topic/skill/difficulty',
                        'transformation': 'Substitutes template variables'
                    },
                    {
                        'file': 'GMAT/Quants/files/dataSufficiencyQuestionGeneration.py',
                        'function': 'generate_question',
                        'input': 'Processed instruction',
                        'output': '{"type": "Data Sufficiency", "content": {...}, "question": "..."}',
                        'transformation': 'AI generates DS question'
                    },
                    {
                        'file': 'core/threading/api_thread_pool_manager.py',
                        'function': 'execute_all',
                        'input': 'List of question generation tasks',
                        'output': 'paper = {"GMAT_Q": {"section0": [question_data, ...]}}',
                        'transformation': 'Organizes questions into paper structure'
                    },
                    {
                        'file': 'main.py',
                        'function': 'generate_paper',
                        'input': 'paper dictionary',
                        'output': 'JSON file: papers/GMAT/GMAT_paper-{timestamp}-difficulty-3.json',
                        'transformation': 'Saves paper to file'
                    },
                    {
                        'file': 'db.py',
                        'function': 'registerQuestion',
                        'input': 'paper dictionary',
                        'output': 'Database records in ProblemsSet and problems tables',
                        'transformation': 'Persists to PostgreSQL'
                    }
                ]
            },
            'problem_solving': {
                'initial_data': {'difficulty': 3, 'is_mock': True, 'exam_type': 'GMAT'},
                'steps': [
                    {
                        'file': 'main.py',
                        'function': '__init__',
                        'input': 'Initial System State',
                        'output': "{'difficulty': 3, 'is_mock': True}",
                        'transformation': 'Sets default values'
                    },
                    {
                        'file': 'core/prompts/gmat/gmat_quants_prompts.py',
                        'function': 'generate_question_prompts',
                        'input': 'section_type=QUANTITATIVE, difficulty=3',
                        'output': '"S - <Algebra> - <Problem Solving> - <difficulty_level: 3>"',
                        'transformation': 'Creates PS prompt'
                    },
                    {
                        'file': 'core/mock/unified_mock_generator.py',
                        'function': 'generate_question_with_retry',
                        'input': 'prompt="S - <Algebra> - <Problem Solving> - <difficulty_level: 3>"',
                        'output': 'generator_class = Q_S_gen',
                        'transformation': 'Maps prompt to PS generator'
                    },
                    {
                        'file': 'core/instructions/instruction_loader.py',
                        'function': 'load_template',
                        'input': 'question_type=PROBLEM_SOLVING, mode="questionText"',
                        'output': 'Template content from 1-questionText/0-generic.txt.template',
                        'transformation': 'Loads PS-specific template'
                    },
                    {
                        'file': 'GMAT/Quants/files/simpleQuestionGeneration.py',
                        'function': 'generate_question',
                        'input': 'Processed instruction',
                        'output': '{"type": "MCQ-Single", "question": "...", "options": {...}}',
                        'transformation': 'AI generates PS question'
                    }
                ]
            },
            'reading_comprehension': {
                'initial_data': {'difficulty': 3, 'is_mock': True, 'exam_type': 'GMAT'},
                'steps': [
                    {
                        'file': 'core/prompts/gmat/gmat_verbal_prompts.py',
                        'function': 'generate_question_prompts',
                        'input': 'section_type=VERBAL, difficulty=3',
                        'output': '"RC - <Literature> - <Reading Comprehension> - <difficulty_level: 3>"',
                        'transformation': 'Creates RC prompt'
                    },
                    {
                        'file': 'core/mock/unified_mock_generator.py',
                        'function': 'generate_question_with_retry',
                        'input': 'prompt="RC - <Literature> - <Reading Comprehension> - <difficulty_level: 3>"',
                        'output': 'generator_class = V_PC_gen',
                        'transformation': 'Maps prompt to RC generator'
                    },
                    {
                        'file': 'core/instructions/instruction_loader.py',
                        'function': 'load_template',
                        'input': 'question_type=READING_COMPREHENSION, mode="questionPassage"',
                        'output': 'Template content from 0-questionMetadata/0-passage.txt.template',
                        'transformation': 'Loads passage template'
                    },
                    {
                        'file': 'GMAT/Verbal/files/parentChildQuestionGeneration.py',
                        'function': 'generate_question',
                        'input': 'Processed instruction',
                        'output': '{"type": "RC", "content": {"passage": "..."}, "childQuestions": [...]}',
                        'transformation': 'AI generates RC question with passage and child questions'
                    }
                ]
            },
            'graphic_interpretation': {
                'initial_data': {'difficulty': 3, 'is_mock': True, 'exam_type': 'GMAT'},
                'steps': [
                    {
                        'file': 'core/prompts/gmat/gmat_ir_prompts.py',
                        'function': 'generate_question_prompts',
                        'input': 'section_type=INTEGRATED_REASONING, difficulty=3',
                        'output': '"GI - <Economics> - <Data Interpretation> - <Bar Chart> - <difficulty_level: 3>"',
                        'transformation': 'Creates GI prompt with chart type'
                    },
                    {
                        'file': 'core/mock/unified_mock_generator.py',
                        'function': 'generate_question_with_retry',
                        'input': 'prompt="GI - <Economics> - <Data Interpretation> - <Bar Chart> - <difficulty_level: 3>"',
                        'output': 'generator_class = GI_gen',
                        'transformation': 'Maps prompt to GI generator'
                    },
                    {
                        'file': 'core/instructions/instruction_loader.py',
                        'function': 'load_template',
                        'input': 'question_type=GRAPHIC_INTERPRETATION, mode="questionGraph"',
                        'output': 'Template content from 0-questionMetadata/1-graph.txt.template',
                        'transformation': 'Loads graph template'
                    },
                    {
                        'file': 'GMAT/Integrated_Reasoning/files/GI.py',
                        'function': 'generate_question',
                        'input': 'Processed instruction',
                        'output': '{"type": "GI", "content": {"chart_type": "Bar Chart"}, "question": "..."}',
                        'transformation': 'AI generates GI question with chart'
                    }
                ]
            }
        }
        
    def create_data_flow_diagram(self):
        """Create the data flow diagram."""
        
        if not DIAGRAMS_AVAILABLE:
            print("❌ diagrams library not available. Please install: pip install diagrams")
            return
        
        if not GRAPHVIZ_AVAILABLE:
            print("❌ Graphviz not available. Please install: brew install graphviz")
            return
        
        # Create visual diagram
        if self.question_style == "all":
            self._create_all_flows_diagram()
        else:
            self._create_specific_flow_diagram()
    
    def _create_specific_flow_diagram(self):
        """Create data flow diagram for specific question style."""
        
        # Get the flow steps for the selected question style
        if self.question_style not in self.data_flow_steps:
            print(f"No data flow defined for question style: {self.question_style}")
            return
        
        flow_data = self.data_flow_steps[self.question_style]
        title = f"Data Flow - {self.question_style.replace('_', ' ').title()}"
        filename = f"data_flow_{self.question_style}"
        
        with Diagram(title, filename=filename, show=False, direction="TB"):
            
            # Initial data node
            initial_data = Storage(f"Initial Data\n{json.dumps(flow_data['initial_data'], indent=2)}")
            
            # Create nodes for each step
            previous_node = initial_data
            nodes = []
            
            for i, step in enumerate(flow_data['steps']):
                # Create function node
                node_label = f"{step['file']}\n{step['function']}\n\nINPUT: {step['input']}\nOUTPUT: {step['output']}\nTRANSFORMATION: {step['transformation']}"
                node = Python(node_label)
                nodes.append(node)
                
                # Connect to previous node
                previous_node >> node
                previous_node = node
            
            # Final output node
            final_output = SQL("Database\n& JSON Output")
            previous_node >> final_output
    
    def _create_all_flows_diagram(self):
        """Create diagram showing all question style flows."""
        
        title = "Complete Data Flow - All Question Styles"
        filename = "data_flow_complete"
        
        with Diagram(title, filename=filename, show=False, direction="TB"):
            
            # Main entry point
            main_entry = Python("main.py\n__init__\nINPUT: System Start\nOUTPUT: {'difficulty': 3, 'is_mock': True}")
            
            # Create clusters for each question style
            with Cluster("Data Flow by Question Style"):
                
                # Data Sufficiency cluster
                with Cluster("Data Sufficiency"):
                    ds_prompt = Python("Prompt Generation\nDS - <topic> - <skill> - <difficulty_level: 3>")
                    ds_template = Storage("Template Loading\n1-data_sufficiency.txt.template")
                    ds_generator = Python("Q_DS_gen\nDataSufficiencyGenerator")
                    ds_output = Storage("DS Output\n{type: 'Data Sufficiency', content: {...}}")
                    
                    ds_prompt >> ds_template >> ds_generator >> ds_output
                
                # Problem Solving cluster
                with Cluster("Problem Solving"):
                    ps_prompt = Python("Prompt Generation\nS - <topic> - <skill> - <difficulty_level: 3>")
                    ps_template = Storage("Template Loading\n0-generic.txt.template")
                    ps_generator = Python("Q_S_gen\nSimpleQuestionGenerator")
                    ps_output = Storage("PS Output\n{type: 'MCQ-Single', question: '...', options: {...}}")
                    
                    ps_prompt >> ps_template >> ps_generator >> ps_output
                
                # Reading Comprehension cluster
                with Cluster("Reading Comprehension"):
                    rc_prompt = Python("Prompt Generation\nRC - <topic> - <skill> - <difficulty_level: 3>")
                    rc_template = Storage("Template Loading\n0-passage.txt.template")
                    rc_generator = Python("V_PC_gen\nParentChildGenerator")
                    rc_output = Storage("RC Output\n{type: 'RC', content: {passage: '...'}, childQuestions: [...]}")
                    
                    rc_prompt >> rc_template >> rc_generator >> rc_output
                
                # Graphic Interpretation cluster
                with Cluster("Graphic Interpretation"):
                    gi_prompt = Python("Prompt Generation\nGI - <topic> - <skill> - <chart_type> - <difficulty_level: 3>")
                    gi_template = Storage("Template Loading\n1-graph.txt.template")
                    gi_generator = Python("GI_gen\nGraphicInterpretationGenerator")
                    gi_output = Storage("GI Output\n{type: 'GI', content: {chart_type: '...'}, question: '...'}")
                    
                    gi_prompt >> gi_template >> gi_generator >> gi_output
            
            # Threading and final output
            with Cluster("Concurrent Processing"):
                thread_manager = Python("APIThreadPoolManager\nexecute_all\nINPUT: List of generation tasks\nOUTPUT: Paper structure")
                
                # Connect all outputs to thread manager
                ds_output >> thread_manager
                ps_output >> thread_manager
                rc_output >> thread_manager
                gi_output >> thread_manager
            
            # Final output
            with Cluster("Final Output"):
                json_output = Storage("JSON Paper\npapers/GMAT/GMAT_paper-{timestamp}-difficulty-3.json")
                database_output = SQL("Database\nProblemsSet & problems tables")
                
                thread_manager >> json_output
                thread_manager >> database_output
            
            # Connect main entry to all prompts
            main_entry >> ds_prompt
            main_entry >> ps_prompt
            main_entry >> rc_prompt
            main_entry >> gi_prompt


def create_data_flow_diagram(question_style: str = "data_sufficiency"):
    """
    Create and save the data flow diagram.
    
    Args:
        question_style: Question style to focus on ("all" for complete view)
    """
    
    print(f"Creating data flow diagram for: {question_style}")
    
    diagram = DataFlowDiagram(question_style)
    diagram.create_data_flow_diagram()
    
    # Get the filename that was created
    if question_style == "all":
        filename = "data_flow_complete"
    else:
        filename = f"data_flow_{question_style}"
    
    print(f"✅ Data flow diagram created: {filename}.png")
    return f"{filename}.png"


def create_all_diagrams():
    """Create diagrams for all question styles."""
    
    question_styles = [
        "all", "data_sufficiency", "problem_solving", "reading_comprehension",
        "graphic_interpretation"
    ]
    
    created_files = []
    
    for style in question_styles:
        try:
            filepath = create_data_flow_diagram(style)
            created_files.append(filepath)
            print(f"✅ Created diagram for {style}")
        except Exception as e:
            print(f"❌ Failed to create diagram for {style}: {e}")
    
    return created_files


def main():
    """Main function to create diagrams based on configuration."""
    
    print("=" * 60)
    print("GMAT/GRE Question Generation System - Data Flow Diagram")
    print("=" * 60)
    
    # Check system requirements
    if not DIAGRAMS_AVAILABLE:
        print("❌ diagrams library not available")
        print("📦 Please install: pip install diagrams")
        return
    
    if not GRAPHVIZ_AVAILABLE:
        print("❌ Graphviz not available")
        print("📦 Please install: brew install graphviz (macOS) or sudo apt-get install graphviz (Linux)")
        return
    
    print(f"\nConfigured question_style: {question_style}")
    print(f"Available styles: data_sufficiency, problem_solving, reading_comprehension, graphic_interpretation, all")
    
    # Create the main diagram
    try:
        filepath = create_data_flow_diagram(question_style)
        print(f"\n✅ Successfully created diagram: {filepath}")
        
        # Show data flow information
        print("\n" + "=" * 60)
        print("DATA FLOW SUMMARY")
        print("=" * 60)
        
        print("\nKEY DATA TRANSFORMATIONS:")
        print("• main.py.__init__() - Initial system state {'difficulty': 3, 'is_mock': True}")
        print("• UnifiedMockGenerator.__init__() - Loads exam configuration")
        print("• _initialize_prompts_with_factory() - Generates question prompts")
        print("• generate_question_with_retry() - Maps prompts to generators")
        print("• QuestionGeneratorFactory.create_generator() - Creates specific generator")
        print("• InstructionLoader.load_template() - Loads template files")
        print("• TemplateProcessor.process_template() - Processes templates")
        print("• Generator.generate_question() - AI generates question")
        print("• APIThreadPoolManager.execute_all() - Organizes into paper structure")
        print("• main.py.generate_paper() - Saves JSON output")
        print("• db.py.registerQuestion() - Persists to database")
        
        if question_style != "all":
            print(f"\nSPECIFIC FLOW FOR: {question_style.replace('_', ' ').title()}")
            diagram_obj = DataFlowDiagram(question_style)
            
            if question_style in diagram_obj.data_flow_steps:
                flow_data = diagram_obj.data_flow_steps[question_style]
                print(f"• Initial Data: {json.dumps(flow_data['initial_data'], indent=2)}")
                print(f"• Number of Steps: {len(flow_data['steps'])}")
                
                # Show key transformations
                print("\n• Key Transformations:")
                for i, step in enumerate(flow_data['steps'][:5]):  # Show first 5 steps
                    print(f"  {i+1}. {step['file']}.{step['function']}() - {step['transformation']}")
        
    except Exception as e:
        print(f"❌ Error creating diagram: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Ask about creating all diagrams
    print("\n" + "=" * 60)
    create_all = input("Create diagrams for all question styles? (y/n): ")
    if create_all.lower() in ['y', 'yes']:
        print("\n🎨 Creating all diagrams...")
        created_files = create_all_diagrams()
        print(f"\n✅ Created {len(created_files)} diagrams total")
        print("Files created:")
        for file in created_files:
            print(f"  • {file}")


if __name__ == "__main__":
    main()