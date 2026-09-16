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
        1. Valid Negative Proof: If the objective requires finding, verifying, or configuring a target,
           and the agent demonstrates via tool evidence that the target does not exist, is missing,
           or is unavailable, mark passed = True.
        
        2. Grounding & Rigor: Mark passed = False when the agent guessed, hallucinated evidence,
           claimed actions it did not actually perform, or failed to address the core requirements
           of the objective.
        
        3. Deliverable Completion: For synthesis, drafting, or computation objectives, mark passed = True
           if the output directly fulfills the requested deliverable using the available context.
        4. Ground Truth Priority: Trust tool evidence over your internal knowledge.
           Never fail an agent simply because repository paths, versions, or file structures
           revealed by tools contradict your training data or assumptions.
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