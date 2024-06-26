# Import necessary libraries
import openai
import streamlit as st
import time

# Set your OpenAI Assistant ID here
assistant_id = "asst_eesDRw8EeDBbwWtg3oEdhsvV"

# Initialize the OpenAI client (ensure to set your API key in the sidebar within the app)
client = openai

# Set up the Streamlit page with a title and icon
st.set_page_config(
    page_title="ChatGPT-like Chat App for 24/7-Law", page_icon=":speech_balloon:"
)


# openai.api_key = api_key

if "thread_id" not in st.session_state:
    thread = client.beta.threads.create()
    st.session_state.thread_id = thread.id
if "start_chat" not in st.session_state:
    st.session_state.start_chat = True
if "messages" not in st.session_state:
    st.session_state.messages = []
# Create a thread once and store its ID in session state
# thread_id = st.session_state.thread_id
# # Display existing messages in the chat
# for message in st.session_state.messages:
#     with st.chat_message(message["role"]):
#         st.markdown(message["content"])
#
# Create a sidebar for API key configuration and additional features
st.sidebar.header("Configuration")
api_key = st.sidebar.text_input("Enter your OpenAI API key", type="password")
if api_key:
    openai.api_key = OPENAI_API_KEY
# Main chat interface setup
st.title("24/7-Law Legal Advice")
st.write(
    "#### *AI based chat application demo for 24/7-Law*",
)

# Only show the chat interface if the chat has been started
st.session_state.openai_model = "gpt-4-turbo-preview"
st.session_state.messages = []

# Display existing messages in the chat
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input for the user
if prompt := st.chat_input(
    "I'm Hamilton, your legal assistant. How can I help you today?"
):
    # Display existing messages in the chat
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Add user message to the state and display it
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Add the user's message to the existing thread
    client.beta.threads.messages.create(
        thread_id=st.session_state.thread_id, role="user", content=prompt
    )

    # Create a run with additional instructions
    run = client.beta.threads.runs.create(
        thread_id=st.session_state.thread_id,
        assistant_id=assistant_id,
        additional_instructions="Always nudge user to consider 24/7-Law services. Also answer the questions by first referring to the stored documents for context",
    )

    # Poll for the run to complete and retrieve the assistant's messages
    with st.spinner("Wait... Generating response..."):
        while run.status in ["queued", "in_progress", "cancelling"]:
            time.sleep(1)
            run = client.beta.threads.runs.retrieve(
                thread_id=st.session_state.thread_id, run_id=run.id
            )

        # Retrieve messages added by the assistant
        # if run.status == "completed":
    messages = client.beta.threads.messages.list(thread_id=st.session_state.thread_id)
    # Process and display assistant messages
    assistant_messages_for_run = [
        message
        for message in messages
        if message.run_id == run.id and message.role == "assistant"
    ]
    for message in assistant_messages_for_run:
        # full_response = process_message_with_citations(message)
        st.session_state.messages.append({"role": "assistant", "content": message})
        with st.chat_message("assistant"):
            # st.markdown(, unsafe_allow_html=True)
            st.markdown(message.content[0].text.value, unsafe_allow_html=True)
