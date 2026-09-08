from ddgs import DDGS
from langchain_core.tools import tool

@tool
def web_search(query: str):
    """Search the web for information."""
    try:
        results = DDGS().text(
            query=query,
            max_results=2
        )
    except Exception as e:
        return f"Search failed: {e}"

    if not results:
        return "No results found."

    return [
        {
            "title": result["title"].strip(),
            "body": result["body"].strip()[:500],
            "href": result["href"].strip()
        }
        for result in results
    ]
