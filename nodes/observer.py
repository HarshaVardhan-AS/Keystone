from schemas import KeystoneState
from llm import verification_llm

MAX_STEP_RETRIES = 2
def observer(state: KeystoneState):
    current_step = state["plan"].steps[state["current_step"]]
    result = state["messages"][-1].content

    verification = verification_llm.invoke(
        f"""
        Evaluate whether the result successfully achieved the objective.

        Objective:
        {current_step}

        Result:
        {result}
        Evaluation Rules:
        1. If the objective requires locating or extracting information from a specific target,
           and the agent definitively proves that the target does not exist or is not configured,
           this counts as SUCCESS (passed = True).
        2. Only mark passed = False if the agent guessed, gave up without checking tools,
           produced hallucinated evidence, or failed to perform the requested verification.
        """
    )

    if verification.passed:
        return {
            "verification": verification,
            "current_step": state["current_step"] + 1,
            "step_retries": 0,
            "next_action" : "next_step"
        }

    if state["step_retries"] < MAX_STEP_RETRIES:
        return {
            "verification": verification,
            "step_retries": state["step_retries"] + 1,
            "next_action": "retry"
        }

    return {
        "verification": verification,
        "current_step": state["current_step"] + 1,
        "step_retries": 0,
        "next_action": "next_step"
    }