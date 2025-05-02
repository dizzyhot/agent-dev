from langgraph.prebuilt import create_react_agent
from langchain_core.language_models.chat_models import BaseChatModel
from typing import Callable

class FlightAssistant:
    def __init__(self, model: BaseChatModel, tools: list[Callable], prompt: str, name: str):
        self.model = model
        self.tools = tools
        self.prompt = prompt
        self.name = name

    def generate_react_agent(self):
        flight_assistant = create_react_agent(
            model=self.model,
            tools=self.tools,
            prompt=self.prompt,
            name=self.name,
        )
        return flight_assistant
