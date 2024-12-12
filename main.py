import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()

llm = ChatOpenAI(model_name="gpt-4o-mini")

print(llm.invoke("What is the capital of France?").content)
