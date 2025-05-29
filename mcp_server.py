import os
import json
from mcp.server.fastmcp import FastMCP

mcp = FastMCP(
    name="Internal Knowledge",
    host="0.0.0.0",
    port=8585
)


@mcp.tool()
def retrieve_knowledge(self, kb_path: str = "data/knowledge.json") -> str:
    knowledge = "Retrieved knowledge: \n"
    data = json.load(self.kb_path)

    for i, k_item in enumerate(data):
        knowledge += k_item[f"Q{i + 1}: {k_item['Q']}"]
        knowledge += k_item[f"A{i + 1}: {k_item['A']}"]

    return knowledge


if __name__ == "__main__":
    print("Running Knowledge Server...")
    mcp.run(transport="stdio")