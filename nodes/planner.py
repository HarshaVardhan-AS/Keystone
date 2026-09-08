from schemas import  KeystoneState
from llm import structured_llm


def planner(state: KeystoneState):
    return {
        "plan": structured_llm.invoke(
            f"""
            You are a planning agent.

            Break the task into the least possible, high impact number of steps.
            Keep each step concrete and outcome-focused.
            Do not over-segment or create open-ended research phases.

            Task:
            {state['task']}
            """
        )
    }