import logging

logger = logging.getLogger()

def log_user_prompt_callback(callback_context, llm_request):
    if llm_request.contents:
        last = llm_request.contents[-1]
        if last.role == "user" and last.parts and last.parts[0].text:
            logger.info("[%s] USER » %s", callback_context.agent_name, last.parts[0].text.strip())

    return None