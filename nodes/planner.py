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
            Operational Constraint:
            Plan only the actions necessary for Keystone to produce the requested deliverable (e.g., research, extract, draft, analyze). 
            Do not turn recommendations, user advice, or conceptual prerequisites into execution steps unless the user explicitly told Keystone to perform them.

            Task:
            {state['task']}
            """
        )
    }