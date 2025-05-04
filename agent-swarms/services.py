from fastapi import FastAPI, Request
import uuid
from main import create_swarm_app
app = FastAPI()


graph = create_swarm_app()

@app.post("/ask")
async def ask_agent(request: Request):
    data = await request.json()
    query = data.get("query")

    # Execute the graph
    events = graph.stream({"messages": [{"role": "user", "content": query}]}, config={"configurable": {"thread_id": "1", "user_id": "1"}})

    response = ""
    for event in events:
        # Each event is a dictionary with agent names as keys
        for agent_name, agent_data in event.items():
            if "messages" in agent_data:
                # Get the last message from the messages array
                last_message = agent_data["messages"][-1]
                if "content" in last_message:
                    response += last_message["content"] + "\n"

    return {"response": response.strip()}
