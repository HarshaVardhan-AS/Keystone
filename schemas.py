from pydantic import BaseModel, Field
from typing import TypedDict, Annotated
from langchain_core.messages import AnyMessage
from langgraph.graph.message import add_messages



class Plan(BaseModel):
    steps : list[str]

class StepVerification(BaseModel):
    passed: bool = Field(
        description="Whether the step objective was successfully achieved."
    )
    feedback: str = Field(
        description="Explain what was missing or incorrect if the step failed."
    )

class KeystoneState(TypedDict):
    task: str
    plan: Plan
    result: str
    status: str
    current_step : int
    messages: Annotated[list[AnyMessage], add_messages]
    verification: StepVerification | None
    step_retries : int
    next_action: str | None
