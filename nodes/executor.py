from schemas import KeystoneState
from llm import llm_with_tools, llm
from langchain_core.messages import HumanMessage, ToolMessage, SystemMessage

def executor(state: KeystoneState):
    current_step = state["plan"].steps[state["current_step"]]
    messages = list(state["messages"])
    new_messages = []
    tools_in_cur_step = 0
    for msg in reversed(messages):
        if isinstance(msg, HumanMessage):
            break
        if isinstance(msg, ToolMessage):
            tools_in_cur_step += 1

    if not messages or not isinstance(messages[-1], ToolMessage): # if a fresh step append step, else send conversation history back to agent
        feedback = ""

        if state["next_action"] == "retry" and state["verification"]:
            feedback = f"""
                Previous attempt failed the Observer's evaluation.

                Observer feedback:
                {state["verification"].feedback}

                Adjust your approach based on this feedback. Do not simply repeat
                the previous attempt.
                """
        prompt = HumanMessage(
            content=f"""Execute this plan step:
        {current_step}
        
        {feedback}

        Guidelines:
        - Use at most 2 targeted searches for this step.
        - Do not repeat searches for information you already have.
        - Once you have sufficient information, synthesize the result and stop using tools."""
        )
        messages.append(prompt)
        new_messages.append(prompt)

    if tools_in_cur_step >= 2:
        synthesis_instruction = SystemMessage(
            content=(
                "The tool budget for this step has been exhausted. "
                "Do not request or use any more tools. "
                "Synthesize the answer for this step using only the "
                "information already available in the conversation."
            )
        )

        response = llm.invoke(
            [synthesis_instruction] + messages
        )
    else:
        response = llm_with_tools.invoke(messages)
    new_messages.append(response)
    return {
        "messages": new_messages
    }


