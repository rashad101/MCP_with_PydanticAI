import json
from mcp.server.fastmcp import FastMCP

# for SSE transport the server needs to be running for stdio transport host and port are not  required
mcp = FastMCP(
    name="Internal Knowledge",
    host="0.0.0.0",  # used for SSE transport
    port=8585  # used for SSE transport
)


@mcp.tool(
    description="The knowledge_retriever tool retrieves internal knowledge that includes a set of frequently asked "
                "questions about various sports."
)
def knowledge_retriever(kb_path: str = "data/knowledge.json") -> str:
    knowledge = "Retrieved knowledge: \n\n"
    data = json.load(open(kb_path))
    print("I am here: ")
    for i, k_item in enumerate(data):
        knowledge += f"Q{i + 1}: {k_item['Q']}\n"
        knowledge += f"A{i + 1}: {k_item['A']}\n\n"

    return knowledge


if __name__ == "__main__":
    print("Running Knowledge Server...")
    mcp.run(transport="sse")
