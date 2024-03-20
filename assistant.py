import openai
from openai import OpenAI
from typing_extensions import override
from openai import AssistantEventHandler

client = OpenAI()
thread = client.beta.threads.create()

message = client.beta.threads.messages.create(
    thread_id=thread.id,
    role="user",
    content="I was very recently arrested. I was asleep in a layby, on a minor road, when the police tapped on my window. I blew 99 at the station. (actually I blew 103 and 99). I remember nothing about what I said to the arresting officers. I vaguely remember being put in cuffs (but really not 100%). I am a very compliant person and would never back chat a police officer. I probably just fell asleep in their car.When I was released I was not interviewed, but instead bailed with no conditions other than having to go back in a weeks time for an interview.why they are wanting to interview me. If they have enough evidence for a straight conviction they wouldn't need to be asking for an interview. ",
)


# First, we create a EventHandler class to define
# how we want to handle the events in the response stream.


class EventHandler(AssistantEventHandler):
    @override
    def on_text_created(self, text) -> None:
        print(f"\nassistant > ", end="", flush=True)

    @override
    def on_text_delta(self, delta, snapshot):
        print(delta.value, end="", flush=True)

    def on_tool_call_created(self, tool_call):
        print(f"\nassistant > {tool_call.type}\n", flush=True)

    def on_tool_call_delta(self, delta, snapshot):
        if delta.type == "code_interpreter":
            if delta.code_interpreter.input:
                print(delta.code_interpreter.input, end="", flush=True)
            if delta.code_interpreter.outputs:
                print(f"\n\noutput >", flush=True)
                for output in delta.code_interpreter.outputs:
                    if output.type == "logs":
                        print(f"\n{output.logs}", flush=True)


# Then, we use the `create_and_stream` SDK helper
# with the `EventHandler` class to create the Run
# and stream the response.

with client.beta.threads.runs.create_and_stream(
    thread_id=thread.id,
    assistant_id="asst_eesDRw8EeDBbwWtg3oEdhsvV",
    additional_instructions="Always nudge user to consider  247-Law services.",
    event_handler=EventHandler(),
) as stream:
    stream.until_done()
