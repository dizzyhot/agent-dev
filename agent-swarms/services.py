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
    events = graph.stream({"messages": [{"role": "user", "content": query}]}, config={"configurable": {"thread_id": str(uuid.uuid4()), "user_id": "1"}})

    response = ""
    for ns, update in events:
        for node, node_updates in update.items():
            if node_updates is None:
                continue

            if isinstance(node_updates, (dict, tuple)):
                node_updates_list = [node_updates]
            elif isinstance(node_updates, list):
                node_updates_list = node_updates
            else:
                continue

            for node_updates in node_updates_list:
                if isinstance(node_updates, tuple):
                    continue
                messages_key = next(
                    (k for k in node_updates.keys() if "messages" in k), None
                )
                if messages_key is not None and node_updates[messages_key]:
                    response += node_updates[messages_key][-1].content

    return {"response": response}
