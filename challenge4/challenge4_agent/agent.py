from google.adk.agents.llm_agent import Agent
from google.adk.tools import google_search
from google.genai import types
from google.adk.agents.sequential_agent import SequentialAgent
from weather_agent.agent import root_agent as nws_weather_agent

SEARCH_AGENT_INSTRUCTIONS=f"""
You are an agent researching a topic provided by the user. Use the google_search tool to search the web for up
to date content and provide a summary to answer the user.
"""

search_and_summarize_agent = Agent(
    model='gemini-3.5-flash',
    name='search_and_summarize_agent',
    description='Agent provides answers to user questions',
    instruction=SEARCH_AGENT_INSTRUCTIONS,
    tools=[google_search],
    output_key='initial_summary'
)

fact_checker_agent = Agent(
    name="fact_checker_agent",
    model='gemini-3.5-flash',
    instruction="""
    You are an expert fact checker.
    Your task is to verify content provided in the initial summary using the google_search tool as necessary.

    **Content to Fact Check:**
    {initial_summary}

    **Review Criteria:**
    1.  **Correctness:** Verify factual statements from the initial summary

    **Output:**
    Provide your feedback as a concise, bulleted list. Focus on the most important factual innacuracies.
    If the content is excellent and requires no changes, simply state: "No major issues found."
    Output *only* the review comments or the "No major issues" statement.
    """,
    description="Fact checks content and provides feedback.",
    tools=[google_search],
    output_key="review_comments"
)

revision_agent = Agent(
    name="revision_agent",
    model='gemini-3.5-flash',
    instruction="""
    You are a content revisor providing a summary of a topic back to the user and a fact checker has reviewed the content.
    Your goal is to improve the given initial summary based on the provided review comments.

    **Original Summary:**
    {initial_summary}

    **Fact Checker Review Comments:**
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


seach_pipeline_agent = SequentialAgent(
    name="seach_pipeline_agent",
    sub_agents=[search_and_summarize_agent, fact_checker_agent, revision_agent],
    description="Executes a sequence of search summarization, fact checking, and final revision",
)

root_agent = seach_pipeline_agent
