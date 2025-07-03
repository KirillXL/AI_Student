from langchain_ollama.llms import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
import os

model = OllamaLLM(model="qwen3:14b", max_tokens=2000)

