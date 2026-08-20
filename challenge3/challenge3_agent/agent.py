from google.adk.agents.llm_agent import Agent
from google.adk.tools import google_search
from google.genai import types
from weather_agent.agent import root_agent as nws_weather_agent

AGENT_INSTRUCTIONS=f"""
You are a general agent that can either use the google_search tool to process requests or
call the nws_weather_agent subagent if the user is asking about weather in the US.
"""

root_agent = Agent(
    model='gemini-3.5-flash',
    name='general_agent',
    description='Agent provides answers to user questions',
    instruction=AGENT_INSTRUCTIONS,
    tools=[google_search],
    sub_agents=[nws_weather_agent],
    generate_content_config=types.GenerateContentConfig(
        tool_config=types.ToolConfig(
            include_server_side_tool_invocations=True,
        )
    ),
)
