import os
import logging
from pydantic import BaseModel, Field
from google import genai
from google.genai import types
from types import SimpleNamespace

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("USCityValidator")


class USLocationValidationResult(BaseModel):
    is_valid_us_city: bool = Field(
        description="True if the user's prompt explicitly or implicitly targets a city/location within the United States, or is a general greeting. False if it asks for an international/non-US location."
    )
    detected_location: str = Field(
        description="The city or country name detected in the user prompt, or 'None'."
    )
    rejection_reason: str = Field(
        description="Short explanation if the prompt refers to a non-US location, otherwise empty."
    )


class NonUSLocationException(Exception):
    """Raised when the prompt asks for a non-US city."""
    pass


# Reusable client for the validator
validator_client = genai.Client(api_key=os.environ.get("GOOGLE_API_KEY"))


def extract_user_text(contents) -> str:
    """Extract plain text from user messages."""
    if isinstance(contents, str):
        return contents
    if not isinstance(contents, list):
        contents = [contents]

    user_texts = []
    for content in contents:
        role = getattr(content, "role", "user")
        if role == "user":
            parts = getattr(content, "parts", [])
            for part in parts:
                if hasattr(part, "text") and part.text:
                    user_texts.append(part.text)
    return " ".join(user_texts)


def validate_us_city_callback(callback_context, llm_request) -> None:
    """before_model_call hook that uses Gemini Flash Lite to ensure

    the query targets a US city before proceeding.
    """
    user_prompt = extract_user_text(llm_request.contents)
    if not user_prompt.strip():
        return

    logger.info("Validating location with Gemini Flash Lite...")

    system_instruction = (
        "You are a location validation classifier. Determine if the user's query refers "
        "to a city or region inside the United States (US territories included). "
        "If the user asks for a non-US location (e.g., Paris, Tokyo, London, Toronto), "
        "mark is_valid_us_city as False."
    )

    # Use flash-lite with structured JSON output for fast, low-cost classification
    validation_response = validator_client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=f"Evaluate this user query: '{user_prompt}'",
        config=types.GenerateContentConfig(
            system_instruction=system_instruction,
            response_mime_type="application/json",
            response_schema=USLocationValidationResult,
            temperature=0.0,
        ),
    )

    # Parse structured output
    result: USLocationValidationResult = validation_response.parsed

    if not result.is_valid_us_city:
        err_msg = (
            f"Blocked non-US location '{result.detected_location}': {result.rejection_reason}"
        )
        logger.warning(err_msg)

        raise NonUSLocationException(
            f"The service only supports US cities. Detected location: '{result.detected_location}'."
        )

    logger.info(f"Location validation passed for: '{result.detected_location}'")


# Main Agent Execution
# client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

# def run_agent(prompt: str):
#     print(f"\n--- Testing Prompt: '{prompt}' ---")
#     try:
#         response = client.models.generate_content(
#             model="gemini-2.5-flash",
#             contents=prompt,
#             config=types.GenerateContentConfig(
#                 callbacks=[
#                     types.Callback(
#                         before_model_call=validate_us_city_callback
#                     )
#                 ]
#             ),
#         )
#         print(f"Agent Response:\n{response.text}")
#     except NonUSLocationException as e:
#         print(f"[Guardrail Blocked]: {e}")


# # 1. Valid US city query
# run_agent("What is the weather in Chicago, IL?")

# # 2. Invalid International city query
# run_agent("What is the weather like in Rome, Italy?")