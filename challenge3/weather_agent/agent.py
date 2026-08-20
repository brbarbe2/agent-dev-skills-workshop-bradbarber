from google.adk.agents.llm_agent import Agent
from weather_agent.tools.get_coordinates import get_city_coordinates
from weather_agent.tools.nws_weather import get_nws_forecast
from weather_agent.callbacks.before_model_log_user_prompt import log_user_prompt_callback
from weather_agent.callbacks.after_model_log_llm_response import log_model_response
from weather_agent.callbacks.before_model_validate_us_city import validate_us_city_callback

WEATHER_AGENT_INSTRUCTIONS="You are a weather agent designed to help a user get weather forcasts based on the city. Use the get_city_coordinates tool to \
    get the location of the city and use the get_nws_forcast tool to get the forcast"


root_agent = Agent(
    model='gemini-3.5-flash',
    name='root_agent',
    description='Pat the friendly weather agent',
    instruction=WEATHER_AGENT_INSTRUCTIONS,
    tools=[get_city_coordinates, get_nws_forecast],
    before_model_callback=[log_user_prompt_callback, validate_us_city_callback],
    after_model_callback=[log_model_response],
)
