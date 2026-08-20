import logging

logger = logging.getLogger()

def log_model_response(callback_context, llm_response):

    if llm_response.content and llm_response.content.parts:
        txt = llm_response.content.parts[0].text
        if txt:
            logger.info("[%s] MODEL » %s", callback_context.agent_name, txt.strip())

    return None