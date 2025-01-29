import os
import json
import dotenv
from openai import OpenAI
from langchain_experimental.openai_assistant import OpenAIAssistantRunnable

dotenv.load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
class generateAssistant:
    def __init__(self):
        self.assistant_id = None
        self.model_name = None
        self.system_prompt = None
        self.output_file_path = os.path.join(os.path.dirname(__file__), "../../assistant_ids.json")
        self.data = {}
        # Load system prompt
    def generateAssistant(self, model_name):
        self.model_name = model_name
        self.system_prompt = open(os.path.join(os.path.dirname(__file__), f"../System_Instructions/{self.model_name}.txt"), "r").read()
        
        # Load existing assistant IDs
        try:
            with open(self.output_file_path, "r") as f:
                content = f.read()
                self.data = json.loads(content) if content else {}
                self.assistant_id = self.data.get(model_name)
        except FileNotFoundError:
            self.data = {}
            self.assistant_id = None

        if self.assistant_id:
            self.assistant = client.beta.assistants.update(
                assistant_id=self.assistant_id,
                instructions=self.system_prompt,
                model="gpt-4o-mini",
            )
            print(f"Assistant with Assistant ID {self.assistant_id} updated successfully")
        else:
            self.assistant = OpenAIAssistantRunnable.create_assistant(
                name=f"GMAT-Q-{self.model_name}",
                instructions=self.system_prompt,
                tools=[],
                model="gpt-4o-mini",
                api_key=os.getenv("OPENAI_API_KEY"),
            )
            self.assistant_id = self.assistant.assistant_id
            print(f"Assistant with Assistant ID {self.assistant_id} created successfully")
            
            # Update data dictionary and save to file
            self.data[self.model_name] = self.assistant_id
            with open(self.output_file_path, "w") as json_file:
                json.dump(self.data, json_file)

generateAssistant = generateAssistant()

generateAssistant.generateAssistant("GRE-Quants-Simple-Questions")
generateAssistant.generateAssistant("GRE-Quants-Parent-Child-Questions")
generateAssistant.generateAssistant("GRE-Quants-Data-Sufficiency-Questions")
generateAssistant.generateAssistant("GRE-Quants-Numeric-Entry")