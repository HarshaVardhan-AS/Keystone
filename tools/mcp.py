import os
from langchain_mcp_adapters.client import MultiServerMCPClient
import asyncio
from dotenv import load_dotenv
load_dotenv()
api_key = os.getenv("TAVILY_API_KEY")
github_token = os.getenv("GITHUB_TOKEN")

client = MultiServerMCPClient({
        "tavily": {
            "transport": "http",
            "url": f"https://mcp.tavily.com/mcp/?tavilyApiKey={api_key}",
        },
        "github": {
            "transport": "http",
            "url": "https://api.githubcopilot.com/mcp/",
            "headers": {
                "Authorization": f"Bearer {github_token}",
                "X-MCP-Toolsets": "repos,issues,pull_requests",
                "X-MCP-Readonly": "true",
            },
},
})




tools = asyncio.run(client.get_tools())