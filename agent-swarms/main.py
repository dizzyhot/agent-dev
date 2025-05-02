from dotenv import load_dotenv
from typing import Callable
from langchain_core.runnables import RunnableConfig
from langchain_openai import ChatOpenAI
from langchain_core.language_models.chat_models import BaseChatModel
from langgraph_swarm import create_handoff_tool, create_swarm
from langgraph.checkpoint.memory import MemorySaver
from agents.flight_assistant import FlightAssistant
from agents.hotel_assistant import HotelAssistant
from tools.flights import search_flights, book_flight
from tools.hotels import search_hotels, book_hotel
from config import RESERVATIONS
from datetime import datetime
import uuid
import os

load_dotenv()


transfer_to_hotel_assistant = create_handoff_tool(
    agent_name="hotel_assistant",
    description="Transfer user to the hotel-booking assistant that can search for and book hotels",
)

transfer_to_flight_assistant = create_handoff_tool(
    agent_name="flight_assistant",
    description="Transfer user to the flight-booking assistant that can search for and book flights",
)

# Define agent prompt
def make_prompt(base_system_prompt: str) -> Callable[[dict, RunnableConfig], list]:
    def prompt(state: dict, config: RunnableConfig) -> list:
        user_id = config["configurable"].get("user_id")
        current_reservation = RESERVATIONS[user_id]
        system_prompt = (
            base_system_prompt
            + f"\n\nUser's active reservation: {current_reservation}"
            + f"\nToday is: {datetime.now()}"
        )
        return [{"role": "system", "content": system_prompt}] + state["messages"]

    return prompt


def create_model() -> BaseChatModel:
    model = ChatOpenAI(
        model=os.getenv("MODEL"),
        temperature=os.getenv("TEMPERATURE"),
        api_key=os.getenv("OPENAI_API_KEY"),
        base_url=os.getenv("BASE_URL")
    )
    return model

def create_swarm_app():
    model = create_model()
    flight_assistant = FlightAssistant(model, [search_flights, book_flight, transfer_to_hotel_assistant], make_prompt("You are a flight booking assistant."), "flight_assistant").generate_react_agent()
    hotel_assistant = HotelAssistant(model, [search_hotels, book_hotel, transfer_to_flight_assistant], make_prompt("You are a hotel booking assistant."), "hotel_assistant").generate_react_agent()
    checkpointer = MemorySaver()
    builder = create_swarm(
        [flight_assistant, hotel_assistant],
        default_active_agent="flight_assistant"
    )
    # Important: compile the swarm with a checkpointer to remember previous interactions and last active agent
    app = builder.compile(checkpointer=checkpointer)
    return app

def print_stream(stream):
    for ns, update in stream:
        print(f"Namespace '{ns}'")
        for node, node_updates in update.items():
            if node_updates is None:
                continue

            if isinstance(node_updates, (dict, tuple)):
                node_updates_list = [node_updates]
            elif isinstance(node_updates, list):
                node_updates_list = node_updates
            else:
                raise ValueError(node_updates)

            for node_updates in node_updates_list:
                print(f"Update from node '{node}'")
                if isinstance(node_updates, tuple):
                    print(node_updates)
                    continue
                messages_key = next(
                    (k for k in node_updates.keys() if "messages" in k), None
                )
                if messages_key is not None:
                    node_updates[messages_key][-1].pretty_print()
                else:
                    print(node_updates)

        print("\n\n")

    print("\n===\n")

def main():
    app = create_swarm_app()
    config = {"configurable": {"thread_id": str(uuid.uuid4()), "user_id": "1"}}
    print_stream(app.stream({
        "messages": [
            {"role": "user", "content": "i am looking for a flight from boston to ny tomorrow"}
        ]
    }, config, subgraphs=True,))

if __name__ == "__main__":
    main()
