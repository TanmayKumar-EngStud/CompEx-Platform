import asyncio
from deepseek_utils import DeepseekSession
from question_manager import ManageComponentTemplates

async def test():
    session = DeepseekSession("Data Sufficiency")
    session.set_system_instruction("You are a helpful assistant.")
    
    instruction = "Generate a question for Data Sufficiency."
    expected_output = {"question": "str"}
    
    print("Testing generate_component for QuestionText...")
    parsed_data, stats = await session.generate_component(
        instruction_statement=instruction,
        expected_output=expected_output,
        context={"component_type": "QuestionText"}
    )
    
    print("\n--- RESULTS ---")
    print("TYPE:", type(parsed_data))
    print("DATA:", parsed_data)

if __name__ == "__main__":
    asyncio.run(test())
