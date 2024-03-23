# Import necessary libraries
import openai
import streamlit as st
import time
import os

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
thread_id = st.session_state.thread_id
# # Display existing messages in the chat
# for message in st.session_state.messages:
#     with st.chat_message(message["role"]):
#         st.markdown(message["content"])
api_key = os.environ["OPENAI_API_KEY"]
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
    "Please tell me what kind of legal troubles you are facing?"
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

    # Show a spinner while the assistant is thinking...
    with st.spinner("Wait... Generating response..."):
        # Poll for the run to complete and retrieve the assistant's messages
        while run.status in ["queued", "in_progress", "cancelling"]:
            time.sleep(1)
            run = client.beta.threads.runs.retrieve(
                thread_id=st.session_state.thread_id, run_id=run.id
            )

    # Retrieve messages added by the assistant
    if run.status == "completed":
        messages = client.beta.threads.messages.list(
            thread_id=st.session_state.thread_id
        )
        for message in messages:
            with st.chat_message("assistant"):
                # st.markdown(st.session_state.thread_id + ":" + run.id)
                st.markdown(
                    messages.data[0].content[0].text.value, unsafe_allow_html=False
                )
