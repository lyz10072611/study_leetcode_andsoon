from dataclasses import dataclass
from langchain.agents import create_agent,create_openai_tools_agent
from langchain.agents.middleware import dynamic_prompt, ModelRequest
from langgraph.runtime import Runtime

@dataclass
class Context:
    user_role: str = "user"

@dynamic_prompt
def dynamic_prompt(request: ModelRequest) -> str:
    user_role = request.runtime.context.user_role
    base_prompt = "You are a helpful assistant."

    if user_role == "expert":
        prompt = f"{base_prompt} Provide detailed technical responses."
    elif user_role == "beginner":
        prompt = f"{base_prompt} Explain concepts simply and avoid jargon."
    else:
        prompt = base_prompt

    return prompt

agent = create_agent(
    model="openai:gpt-4o",
    tools=tools,
    middleware=[dynamic_prompt],
    context_schema=Context
)

agent.invoke(
    {"messages": [{"role": "user", "content": "Explain async programming"}]},
    context=Context(user_role="expert")
)