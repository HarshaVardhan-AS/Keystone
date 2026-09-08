from dotenv import load_dotenv
load_dotenv()
from schemas import Plan, StepVerification
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from tools.mcp import tools
llm = ChatGoogleGenerativeAI(
    model="gemini-3.5-flash-lite"
)
llm_with_tools = llm.bind_tools(tools)
structured_llm = llm.with_structured_output(
    Plan,
    method="json_schema"
)
verification_llm = ChatGroq(
    model="openai/gpt-oss-20b"
).with_structured_output(
    StepVerification,
    method="json_schema"
)