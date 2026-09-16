from langgraph.graph import StateGraph
from langgraph.graph import START, END
from schemas import KeystoneState
from nodes.planner import planner
from nodes.executor import executor
from nodes.observer import observer
from langgraph.prebuilt import ToolNode
from tools.mcp import tools

import logging

logging.getLogger("langchain_google_genai").setLevel(logging.ERROR) #mute Key 'additionalProperties' is not supported log
logging.getLogger("google_genai").setLevel(logging.ERROR) #mute Direct use of automatic function.. log

def route_executor(state: KeystoneState):
    last_message = state["messages"][-1]

    if last_message.tool_calls:
        return "tools"

    return "observer"

def route_observer(state: KeystoneState):
    if (
        state["next_action"] == "next_step"
        and state["current_step"] >= len(state["plan"].steps)
    ):
        return "end"

    return state["next_action"]

tool_node = ToolNode(tools)

graph = StateGraph(KeystoneState)

graph.add_node("planner", planner)
graph.add_node("executor", executor)
graph.add_node("tools", tool_node)
graph.add_node("observer", observer)

graph.add_edge(START, "planner")
graph.add_edge("planner", "executor")
graph.add_conditional_edges(
    "executor",
    route_executor,
    {
        "tools": "tools",
        "observer": "observer",
    }
)
graph.add_conditional_edges(
    "observer",
    route_observer,
    {
        "next_step": "executor",
        "retry": "executor",
        "end": END,
    }
)
graph.add_edge("tools", "executor")

workflow = graph.compile()


initial_state = {
    "task": "Inspect the GitHub repository 'pallets/flask' and determine whether the repository currently contains any open pull requests authored by the repository owner. Report the number found and list their titles. If no such pull requests exist, explicitly state that none were found based on the GitHub tool results.",
    #test task
    "plan": "",
    "result": "",
    "status": "",
    "current_step" : 0,
    "messages" : [],
    "verification": None,
    "next_action": None,
    "step_retries" : 0
}

import asyncio


async def main():
    async for event in workflow.astream(initial_state, stream_mode="updates"):
        for node, values in event.items():
            step_num = values.get("current_step", "in-progress")
            print(f"\n--- [Node: {node} | Step: {step_num}] ---")

            # 1. Planner output
            if "plan" in values:
                print("Generated Plan:")
                for idx, step in enumerate(values["plan"].steps, 1):
                    print(f"  {idx}. {step}")

            # 2. Observer audit result
            elif "verification" in values:
                v = values["verification"]
                action = values.get("next_action", "unknown")
                status_icon = "✅ PASSED" if v.passed else "❌ FAILED"

                print(f"Audit: {status_icon} | Action: {action.upper()}")
                print(f"Feedback: {v.feedback}")

            # 3. Message / Tool outputs
            elif "messages" in values and values["messages"]:
                last_msg = values["messages"][-1]

                if node == "tools":
                    print("✓ Tool execution completed.")
                elif hasattr(last_msg, "content") and last_msg.content:
                    text = (
                        last_msg.content
                        if isinstance(last_msg.content, str)
                        else last_msg.content[0].get("text", "")
                    )
                    print(text)


if __name__ == "__main__":
    asyncio.run(main())