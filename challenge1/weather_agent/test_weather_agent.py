from vertexai.preview import reasoning_engines
from agent import root_agent
from IPython.display import Markdown, display

app = reasoning_engines.AdkApp(
 agent=root_agent,
 enable_tracing=False,
)

user_id = "test-user-id"
session = app.create_session(user_id=user_id)
print(session.id)

for event in app.stream_query(
 user_id=user_id,
 session_id=session.id,
 message="Write a function to reverse the bits of an integer",
):
 lastevent = event

display(Markdown(lastevent["content"]["parts"][0]["text"]))