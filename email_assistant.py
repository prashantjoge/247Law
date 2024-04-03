from openai import OpenAI
from constants import (
    solicitors,
    assistant_id,
    avatar_kv,
    tools_kv,
    file_id_to_name,
    quote_context,
    tools,
    gpt_model,
    api_key,
    additional_instructions,
    email_assistant_id,
    instructions,
    email_assist_addnl_Instructions,
    email_assist_instructions,
)
import time
import re

email_tools = [
    {"type": "retrieval"},
    {"type": "code_interpreter"},
]


def format_messages_thread_message_list(messages):
    # from client.beta.threads.messages.list(thread_id)

    formatted_messages = []
    messages = reversed(messages)
    for message in messages:
        # Determine the role of the message sender
        role_prefix = f"{message.role}="

        # Extract the message text. Note: This assumes there's always at least one content block and it's of type 'text'.
        message_text = message.content[0].text.value.strip()

        # Format the message
        formatted_message = f'{role_prefix} "{message_text}"'
        formatted_messages.append(formatted_message)

    # Combine all formatted messages into a single string with newline separators
    combined_messages = "\n".join(formatted_messages)
    return combined_messages


# Function to format messages
## Sample messages
# messages = [
#     {'role': 'user', 'content': 'I had a seizure while I was driving. I over sped and hit really hard on the bumper of the car in front of me. By the time everyone arrived my seizure was gone. nobody believes me. I was going at 45 KM on a 25 km road.'},
#     {'role': 'user', 'content': 'I have a diagnosis for seizure and have been ordered not to drive. I do not have a license.'},
#     {'role': 'user', 'content': 'casey, prashant.thomas@verbat.com, 789-098-6789'}
# ]
def format_messages_user_response(messages):
    formatted_messages = []

    # Process all but the last message normally
    for message in messages[:-1]:
        formatted_messages.append(f'"{message["content"]}"')

    # Special handling for the last message
    last_message_content = messages[-1]["content"]

    # Extract name, email, and phone number
    name_match = re.search(r"[\w\s]+(?=,)", last_message_content)
    email_match = re.search(
        r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", last_message_content
    )
    phone_match = re.search(r"\d{3}-\d{3}-\d{4}", last_message_content)

    # Format the extracted information
    if name_match and email_match and phone_match:
        client_name = name_match.group().strip().title()  # Capitalize the name properly
        client_email = email_match.group()
        client_phone = phone_match.group()

        formatted_last_message = f"client_name={client_name}, Client_email: {client_email}, client_phone: {client_phone}"
        formatted_messages.append(f'"{formatted_last_message}"')
    else:
        # If the pattern does not match, append the original last message
        formatted_messages.append(f'"{last_message_content}"')

    # Combine all formatted messages
    combined_message = "\n".join(formatted_messages)
    return combined_message


def call_custom_assistant_with_kb(conversation_history, thread_id):
    """
     Calls a custom OpenAI assistant, ensuring it utilizes its configured knowledge base.

     Args:
     - conversation_history (list of dict): The conversation history.
     - assistant_id (str): The ID of the custom assistant.
    padre, prashant.thomas@verbat.com, 789-098-7890
     Returns:
     - str: The generated response from the assistant.
    """
    print(conversation_history)
    client = OpenAI()
    message_history = ""
    OpenAI.api_key = api_key
    # thread_messages = client.beta.threads.messages.list(thread_id)
    # print(format_messages_for_creation(thread_messages.data))
    # message_history = format_messages_thread_message_list(thread_messages.data)
    message_history = format_messages_user_response(conversation_history)
    print("Message History:", message_history)
    my_assistant = client.beta.assistants.retrieve(email_assistant_id)
    thread = client.beta.threads.create()
    messages = client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=message_history,
    )
    print(messages)
    print("preparing to run")
    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=my_assistant.id,
        # instructions=email_assist_instructions,
        additional_instructions=email_assist_addnl_Instructions,
        tools=email_tools,
    )
    email_run = 0
    while run.status != "completed":
        email_run += 1
        run_steps = client.beta.threads.runs.steps.list(
            thread_id=thread.id, run_id=run.id
        )
        # run = client.beta.threads.runs.submit_tool_outputs(
        #      thread_id=thread.id, run_id=run.id
        #  )
        run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)

        print("email run:", email_run)
        time.sleep(2)

    try:
        r_messages = client.beta.threads.messages.list(thread_id=thread.id)
        content = ""
        print("ret messages", r_messages)
        for line in r_messages.data[:-1]:
            message_content = line.content[0].text
            content += message_content.value
            print("returned message content")
            print(content)
            # response = openai.Assistant(assistant_id).chat(messages=conversation_history)
            return content
    except Exception as e:
        print(f"An error occurred: {e}")
        return "Failed to generate response."
