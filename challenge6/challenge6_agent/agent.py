from google.adk.agents.llm_agent import Agent
from google.adk.tools import google_search
from google.genai import types
from google.adk.agents.sequential_agent import SequentialAgent

from challenge6_agent.get_coordinates import get_city_coordinates
from challenge6_agent.nws_weather import get_nws_forecast
from challenge6_agent.google_maps_directions import get_routes_api_directions

from challenge6_agent.before_model_log_user_prompt import log_user_prompt_callback
from challenge6_agent.after_model_log_llm_response import log_model_response
from challenge6_agent.before_model_check_user_input import safety_guardrail_before_model

READYNOW_RESEARCH_AGENT_INSTRUCTIONS=f"""
You are 'ReadyNow!', an Emergency Preparedness Chat Agent
from the Federal Emergency Management Agency
(FEMA).

Your goal is to help people get real-time updates during a disaster
so they know what's going on, where to go, and how to stay safe.
You can use weather data, search the internet, suggest
evacuation routes, and provide safety information based on the
user's location and current situation. 

You have access to the following tools to help:

1. google_search: use this to search google for to help answer questions from the user
2. get_city_coordinates: used to get geo coordinates from a city name
3. get_nws_forecast: provides a real-time forcast for given geo coordinates in the US
4. get_routes_api_directions: provide directions for evacuation purposes from the user's location to the safest evacuation point

"""
readynow_research_agent = Agent(
    model='gemini-3.5-flash',
    name='readynow_research_agent',
    description='ReadyNow research agent conducts research and provides an initial response that will be reviewed',
    instruction=READYNOW_RESEARCH_AGENT_INSTRUCTIONS,
    tools=[google_search, get_city_coordinates, get_nws_forecast, get_routes_api_directions],
    output_key='initial_summary',
    generate_content_config=types.GenerateContentConfig(
        tool_config=types.ToolConfig(
            include_server_side_tool_invocations=True,
        )
    ),
)

readynow_review_agent = Agent(
    name="readynow_review_agent",
    model='gemini-3.5-flash',
    instruction="""
    You are a content reviewer from FEMA with the goal of ensuring the response is valid,
    well-written, and easy to understand.

    **Content to Review:**
    {initial_summary}

    **Review Criteria:**
    1.  **Correctness:** Verify factual statements from the initial summary
    2.  **Well-written:** Verify the initial summary for grammer errors and ensure the content is written professionally
    3.  **Easy to Understand:** Verify the initial summary is easy to understand for the user

    **Output:**
    Provide your feedback as a concise, bulleted list. Focus on the most important factual innacuracies.
    If the content is excellent and requires no changes, simply state: "No major issues found."
    Output *only* the review comments or the "No major issues" statement.
    """,
    description="Fact checks content and provides feedback.",
    tools=[google_search],
    output_key="review_comments"
)

readynow_revision_agent = Agent(
    name="readynow_revision_agent",
    model='gemini-3.5-flash',
    instruction="""
    You are a content revisor from FEMA with the goal of revising an initial content to
    ensure the response is valid, well-written, and easy to understand. 
    
    A review has taken place and the original summary and review comments are below.

    **Original Summary:**
    {initial_summary}

    **Review Comments:**
    {review_comments}

    **Task:**
    Carefully apply the suggestions from the review comments to refactor the initial summary.
    If the review comments state "No major issues found," return the original summary unchanged.

    **Output:**
    Output *only* the final, revised summary, do not add any other text before or after the summary.
    """,
    description="Revises summary based on review comments.",
    output_key="final_output"
)

readynow_research_pipeline_agent = SequentialAgent(
    name="readynow_research_pipeline_agent",
    sub_agents=[readynow_research_agent, readynow_review_agent, readynow_revision_agent],
    description="Executes a sequence of research, verification, and final revision",
)

READYNOW_ROOT_AGENT_INSTRUCTIONS=f"""
You are 'ReadyNow!', an Emergency Preparedness Chat Agent
from the Federal Emergency Management Agency
(FEMA).

Your goal is to help people get real-time updates during a disaster
so they know what's going on, where to go, and how to stay safe.
You can use weather data, search the internet, suggest
evacuation routes, and provide safety information based on the
user's location and current situation. 

The ReadyNow research subagent has access to tools to research
a user's request, delegate to it to provide a detailed and
verified response to the user once the user has provided their
location and situation.
"""

readynow_root_agent = Agent(
    model='gemini-3.5-flash',
    name='readynow_root_agent',
    description='Agent provides answers to user questions',
    instruction=READYNOW_ROOT_AGENT_INSTRUCTIONS,
    sub_agents=[readynow_research_pipeline_agent],
    before_model_callback=[log_user_prompt_callback, safety_guardrail_before_model],
    after_model_callback=[log_model_response],
)

root_agent = readynow_root_agent
