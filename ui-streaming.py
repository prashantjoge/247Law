# Import necessary libraries
from openai import OpenAI
from typing_extensions import override
from openai import AssistantEventHandler
from openai.types.beta.threads.runs import tool_calls_step_details
import streamlit as st

# import time
import random

# from termcolor import colored
import os
import datetime
import json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import base64
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
# from streamlit.runtime.state import session_state

# List of fictitious solicitor records
solicitors = [
    {
        "name": "Elena Smith",
        "email": "elena.smith@lawpartners.co.uk",
        "phone": "020 8004 1122",
        "background": "Elena has a decade of experience handling DUI cases and advocating for safer driving practices.",
    },
    {
        "name": "Michael Brown",
        "email": "michael.brown@justiceleague.co.uk",
        "phone": "020 8005 2233",
        "background": "Michael specializes in defending against speeding tickets and has a strong track record in reducing penalties.",
    },
    {
        "name": "Sophia Johnson",
        "email": "sophia.johnson@legalsolutions.co.uk",
        "phone": "020 8006 3344",
        "background": "With a focus on traffic accident claims, Sophia assists her clients in securing fair compensation.",
    },
    {
        "name": "James Wilson",
        "email": "james.wilson@thebarristers.co.uk",
        "phone": "020 8007 4455",
        "background": "James is known for his expertise in cases of reckless driving and has helped numerous clients avoid license suspension.",
    },
    {
        "name": "Isabella Martinez",
        "email": "isabella.martinez@lawcorner.co.uk",
        "phone": "020 8008 5566",
        "background": "Isabella provides legal assistance for disputes over road usage and right-of-way violations.",
    },
    {
        "name": "Oliver Thomas",
        "email": "oliver.thomas@thefirm.co.uk",
        "phone": "020 8009 6677",
        "background": "Oliver has extensive experience in handling cases involving driving without insurance, offering strategic legal advice.",
    },
    {
        "name": "Amelia Rodriguez",
        "email": "amelia.rodriguez@legaladvocates.co.uk",
        "phone": "020 8010 7788",
        "background": "Amelia focuses on cases of driving under the influence of substances, aiming to provide comprehensive defense strategies.",
    },
    {
        "name": "Lucas White",
        "email": "lucas.white@solicitorsuk.co.uk",
        "phone": "020 8011 8899",
        "background": "Lucas is adept at handling cases involving illegal vehicle modifications, ensuring clients receive knowledgeable representation.",
    },
    {
        "name": "Mia Harris",
        "email": "mia.harris@thelawoffice.co.uk",
        "phone": "020 8012 9900",
        "background": "Mia specializes in pedestrian right-of-way cases and works tirelessly to advocate for victims of road negligence.",
    },
    {
        "name": "Benjamin Clark",
        "email": "benjamin.clark@justiceworks.co.uk",
        "phone": "020 8013 0011",
        "background": "Benjamin offers legal counsel on traffic law compliance for commercial driving operations, helping businesses navigate complex regulations.",
    },
]
st.set_page_config(
    page_title="ChatGPT-like Chat App for 24/7-Law", page_icon=":speech_balloon:"
)


def render_custom_css() -> None:
    """
    Applies custom CSS
    """
    st.markdown(
        """
            <style>
            MainMenu {visibility: hidden}
            header {visibility: hidden}
            footer {visibility: hidden}
            .block-container {
                padding-top: 2rem;
                padding-bottom: 2rem;
                padding-left: 3rem;
                padding-right: 3rem;
                }
                
            </style>
            """,
        unsafe_allow_html=True,
    )


render_custom_css()
file_upload_box = st.empty()
upload_btn = st.empty()
text_box = st.empty()
qn_btn = st.empty()
key = "user_input"
if "text_boxes" not in st.session_state:
    st.session_state.text_boxes = []
if "assistant_text" not in st.session_state:
    st.session_state.assistant_text = [""]
st.session_state.openai_model = "gpt-4-turbo-preview"
st.sidebar.title("🤖 GPTs")
st.session_state.disabled = False
avatar = {"assistant": "🤖", "user": "👲"}
tools = {"code_interpreter": "🐍", "retrieval": "🔎", "function": "💬"}
assistant_id = "asst_eesDRw8EeDBbwWtg3oEdhsvV"
api_key = st.secrets["OPENAI_API_KEY"]
# api_key = os.environ["OPENAI_API_KEY"]
OpenAI.api_key = api_key
# Initialize the OpenAI client (ensure to set your API key in the sidebar within the app)
client = OpenAI()
if "thread_id" not in st.session_state:
    thread = client.beta.threads.create()
    st.session_state.thread_id = thread.id
    st.session_state.created_at = thread.created_at

# print("Thread:", st.session_state.thread_id)
if "start_chat" not in st.session_state:
    st.session_state.start_chat = True

if "messages" not in st.session_state:
    messages = client.beta.threads.messages.list(thread_id=st.session_state.thread_id)
    st.session_state.messages = []

if "conversation_history" not in st.session_state:
    st.session_state.conversation_history = []

st.sidebar.header("Assistants")
list_of_assistants = client.beta.assistants.list()
# st.write(list(list_of_assistants))
# assistant = st.sidebar.selectbox(
#     "Select Assistant", list_of_assistants, format_func=lambda assistant: assistant.name
# )
# st.sidebar.write(assistant)
#
assistant_247 = my_assistant = client.beta.assistants.retrieve(assistant_id)
assistant_tools = [tool.type for tool in assistant_247.tools]
assistant_tools_emojis = [tools[tool.type] for tool in assistant_247.tools]
# print(assistant_247.tools)
# print(assistant_247.file_ids)
if api_key:
    OpenAI.api_key = os.environ["OPENAI_API_KEY"]
st.sidebar.write(f"**ID**:\n{assistant_247.id}")
# st.sidebar.write(f"**Instructions**:\n{assistant.instructions}")
st.sidebar.write(f"**Model**:\n{assistant_247.model}")
st.sidebar.write(f"**Tools**:\n{list(zip(assistant_tools, assistant_tools_emojis))}")
# Main chat interface setup


st.sidebar.write("## Thread")
# st.sidebar.write(thread)
st.sidebar.write(f"*{st.session_state.thread_id}*")
st.sidebar.write(
    f"Created at {datetime.datetime.fromtimestamp(st.session_state.created_at)}"
)


class EventHandler(AssistantEventHandler):
    @override
    def on_text_created(self, text) -> None:
        # Display initial message from the assistant
        # st.chat_message(
        #     text.value,
        #     avatar=avatar["user"],
        # )
        print("text created:", text)
        # Create a new text box
        st.session_state.text_boxes.append(st.empty())
        # Retrieve the newly created text box and empty it
        st.session_state.text_boxes[-1].empty()
        # Insert the text into the last element in assistant text list
        st.session_state.assistant_text[-1] += (
            "**> " + avatar["assistant"] + "Hamilton:**\n\n "
        )
        # Display the text in the newly created text box
        st.session_state.text_boxes[-1].info(
            "".join(st.session_state["assistant_text"][-1])
        )

    @override
    def on_text_delta(self, delta, snapshot):
        # For updates to the text, append or update the chat message
        # Here, we simply print the delta, but you might want to update
        # the chat dynamically depending on your application's logic
        # st.chat_message(str(delta.value), avatar=avatar["assistant"])
        # print("text_delta", delta.value)
        print(delta.value, end="", flush=True)
        # print(f"\nassistant > ", end="", flush=True)
        # Clear the latest text box
        st.session_state.text_boxes[-1].empty()
        # If there is text written, add it to latest element in the assistant text list
        if delta.value:
            st.session_state.assistant_text[-1] += delta.value
        # Re-display the full text in the latest text box
        st.session_state.text_boxes[-1].info(
            "".join(st.session_state["assistant_text"][-1])
        )

    @override
    def on_text_done(self, text):
        """
        Handler for when text is done
        """
        # Create new text box and element in the assistant text list
        st.session_state.text_boxes.append(st.empty())
        st.session_state.assistant_text.append("\n")
        # if "clear_input" in st.session_state and st.session_state.clear_input:
        #     text_box.text_input(
        #         label="I'm Hamilton, your legal assistant. How can I help you today?",
        #         value=st.empty(),
        #     )  # Clear the input
        #     st.session_state.clear_input = False  # Reset the flag
        #

    def on_tool_call_created(self, tool_call):
        print(tool_call.model_dump())
        print(f"\nassistant > {tool_call.type}\n", flush=True)
        message = f"Received tool call: {tool_call.type}\n\n"
        st.session_state.assistant_text[-1] += tool_call.model_dump_json()
        st.session_state.text_boxes[-1].info(
            "".join(st.session_state["assistant_text"][-1])
        )
        # tool_call.function
        # if tool_call.type == "function":
        # Hypothetically accessing the function details if they're nested
        # function_details = (
        #     tool_call.details
        # )  # This is just an example; use the actual attribute
        # function_name = function_details.get("function_name", "")

        #     if function_name == "send_email":
        #         arguments = json.loads(function_details.get("arguments", "{}"))
        #         self.handle_send_email(arguments)
        #
        # elif tool_call.type == "retrieval":
        #     print("Retrieving data")
        # # Assuming we're not handling deltas differently for simplicity

    def on_tool_call_delta(self, delta, snapshot):
        tool_calls = []

    # # build up the response structs from the streamed response, simultaneously sending message chunks to the browser
    #         for chunk in response:
    #             delta = chunk.choices[0].delta
    #             #app.logger.info(f"chunk: {delta}")
    #
    #             if delta and delta.content:
    #                 # content chunk -- send to browser and record for later saving
    #                 socket.send(json.dumps({'type': 'message response', 'text': delta.content }))
    #                 newsessionrecord["content"] += delta.content
    #
    #             elif delta and delta.tool_calls:
    #                 tcchunklist = delta.tool_calls
    #                 for tcchunk in tcchunklist:
    #                     if len(tool_calls) <= tcchunk.index:
    #                         tool_calls.append({"id": "", "type": "function", "function": { "name": "", "arguments": "" } })
    #                     tc = tool_calls[tcchunk.index]
    #
    #                     if tcchunk.id:
    #                         tc["id"] += tcchunk.id
    #                     if tcchunk.function.name:
    #                         tc["function"]["name"] += tcchunk.function.name
    #                     if tcchunk.function.arguments:
    #                         tc["function"]["arguments"] += tcchunk.function.arguments
    #                 if delta.type == "code_interpreter":
    #             if delta.code_interpreter.input:
    #                 print(delta.code_interpreter.input, end="", flush=True)
    #             if delta.code_interpreter.outputs:
    #                 print(f"\n\noutput >", flush=True)
    #                 for output in delta.code_interpreter.outputs:
    #                     if output.type == "logs":
    #                         print(f"\n{output.logs}", flush=True)
    #
    def handle_send_email(self, arguments):
        # Example function to handle sending an email based on tool call arguments
        recipient = arguments.get("recipient")
        subject = arguments.get("subject")
        body = arguments.get("body")
        # Simulate email sending logic
        message = f"Sending email to {recipient} with subject '{subject}'..."
        st.chat_message(
            message, avatar=avatar["user"]
        )  # Assuming this is executed as a user action

    def on_timeout(self):
        """
        Handler for when the api call times out
        """
        st.error("The api call timed out.")
        st.stop()

    def on_exception(self, exception: Exception):
        """
        Handler for when an exception occurs
        """
        st.error(f"An error occurred: {exception}")
        st.stop()

    def get_random_solicitor(self):
        # Select a random record
        random_solicitor = random.choice(solicitors)

        # Format the selected solicitor's information and background into a string
        solicitor_info = f"Name: {random_solicitor['name']}, Email: {random_solicitor['email']}, Phone: {random_solicitor['phone']}, Background: {random_solicitor['background']}"

        return solicitor_info

    def extract_background(self, solicitor_info):
        # Find the start of the "Background" section
        start = solicitor_info.find("Background: ")

        # Adjust start position to skip the "Background: " part itself
        start += len("Background: ")

        # Extract the background information
        background = solicitor_info[start:]

        return background

    def remove_background(self, solicitor_info):
        # Find the start of the "Background" section
        start = solicitor_info.find("Background: ")

        # If "Background: " is found, extract the string up to this point
        if start != -1:
            return solicitor_info[:start].strip()
        else:
            # If "Background: " is not found, return the original string
            return solicitor_info

    def convert_markdown_to_html(self, quote):
        # Convert markdown bold (**text**) to HTML bold (<b>text</b>)
        quote_html = quote.replace("**", "</b>").replace("<b>", "<b>", 1)
        quote_html = quote.replace("###", "</b>").replace("<b>", "<b>", 1)

        quote_html = quote.replace("'''", "</b>").replace("", "", 1)
        # Ensure opening and closing <b> tags are properly placed
        quote_html = quote_html.replace("</b>", "<b>", 1)

        # Additional step to ensure all '**' are converted to '<b>' and '</b>'
        while "**" in quote_html:
            quote_html = quote_html.replace("**", "<b>", 1)
            quote_html = quote_html.replace("**", "</b>", 1)

        while "###" in quote_html:
            quote_html = quote_html.replace("###", "<b>", 1)
            quote_html = quote_html.replace("###", "</b>", 1)

        # Replace newline characters with <br> tags for HTML line breaks
        quote_html = quote_html.replace("\n", "<br>")

        # Wrap the content in a basic HTML structure
        # html_content = f"""
        # <html>
        # <head></head>
        # <body>
        #     {quote_html}
        # </body>
        # </html>
        # """
        return quote_html

    def get_quote_from_conversation_context(self, conversation_history):
        # Implement the summary generation logic here
        """
        Generates a summary of the conversation history using OpenAI's GPT-4.

        Args:
        - conversation_history (list of str): A list containing the user's statements in the conversation.

        Returns:
        - str: A summary of the conversation.
        """
        # Join the conversation history into a single string, each statement separated by newlines
        # conversation_text = "\n".join(conversation_history)
        # Append a prompt for the AI to generate a summary at the end of the conversation history
        conversation_history.append(
            {
                "role": "system",
                "content": """Summarize the client's main concerns and advice given. Please provide the response in markdown format . The summary will have 5 sections. 
                1. Understanding  and summary of client's problem. 
                2. Concerns the client
                3. Legal consequences
                4. Mitigating actions 
                5. Advice to seek professional help
                Always refer to the client by name when ever possible
                """,
            }
        )
        client = OpenAI()
        print(api_key)
        print("conversation history", conversation_history)
        client.api_key = api_key
        # Prepare the prompt for GPT-3
        #    prompt = f"The following is a conversation with a user seeking legal advice:\n{conversation_text}\n\nSummarize the user's main concerns and advice given:"
        try:
            completion = client.chat.completions.create(
                model="gpt-4-0125-preview", messages=conversation_history
            )

            # Extract the generated summary from the completion response
            summary = completion.choices[0].message.content
            return summary

        except Exception as e:
            print(f"Error generating summary: {e}")
            return "Summary generation failed."

    # Function to send an email with a quote
    def send_email(
        self,
        quote,
        name="name of user",
        email="your@email.com",
        phone="777-777-7777",
        solicitor="adam, adam@247-law.com, 777-777-7777",
    ):
        SCOPES = ["https://www.googleapis.com/auth/gmail.send"]
        flow = InstalledAppFlow.from_client_secrets_file(
            "client_secret-apps.googleusercontent.com.json", SCOPES
        )
        print("Quote: ", quote)
        print("Solicitor:", solicitor)
        creds = flow.run_local_server(port=0)
        if not quote:
            print("Error: 'quote' argument is required but was not provided.")
            return  # Handle the missing argument appropriately
        # Print the quote and recipient for debugging purposes
        # print(f"Generated quote:\n {quote}\n\nSending via email to: {email}")
        sender_email = "sethgofiger@gmail.com"  # Your email
        service = build("gmail", "v1", credentials=creds)
        # Create the email headers and body
        # Create a MIMEMultipart object to hold different parts of the email
        msg = MIMEMultipart()
        html_content = f"""
                        <html>
                        <head></head>
                        <body>
                            <style>
                                    body {{
                                        font-family: 'Arial', sans-serif;
                                        margin: 20px;
                                        padding: 20px;
                                        background-color: #f4f4f4;
                                        color: #333;
                                    }}
                                    p {{
                                        font-size: 16px;
                                    }}
                                    .quote {{
                                        font-style: italic;
                                        color: #555;
                                    }}
                                    .footer {{
                                        margin-top: 20px;
                                        font-size: 12px;
                                        text-align: center;
                                    }}
                                    .link-button {{
                                        display: inline-block;
                                        background-color: #007bff;
                                        color: #ffffff;
                                        padding: 10px 15px;
                                        text-decoration: none;
                                        border-radius: 5px;
                                        margin-top: 20px;
                                    }}
                                </style>
                            <p>Hello, Mr. <b>{name}</b> </p>
                            <p class="quote">{quote} </p>
                            <p>Based on the information you shared, your contact details are.
                            <b>email</b> : {email}  <b>phone</b> : {phone}. Please <b>call us</b> if this is not correct <br></p>
                            <p>For more info you may reach us @ <a href="http://www.247-Law.com">247-Law</a> .</p>
                            <p>You have been assigned to a solicitor.</p><p> <b>{remove_background(solicitor)}.</b>  </p><p> In the next 24 hours, they will get in touch with you. </p>
                            <p><b>{extract_background(solicitor)}</b></p>
                            <div class="footer">
                                    Contact Us: adam@247-law.com | 777-777-7777<br>
                                    Unsubscribe from these emails <a href="#">here</a>.
                            </div>
                            </p>
                        </body>
                        </html>
                        """
        print(html_content)
        html_part = MIMEText(html_content, "html")
        msg.attach(html_part)
        msg["From"] = sender_email
        msg["To"] = email
        msg["Subject"] = "Message from 24/7-Law on your recent enquiry"
        create_message = {"raw": base64.urlsafe_b64encode(msg.as_bytes()).decode()}
        try:
            message = (
                service.users()
                .messages()
                .send(userId="me", body=create_message)
                .execute()
            )
            print(f'sent message to {message} Message Id: {message["id"]}')
            return f"Message sent to {email}"

        except HTTPError as error:
            print(f"Error: {error}")
            return "Failed to send email."


tools = [
    {
        "type": "function",
        "function": {
            "name": "send_email",
            "description": "Sends an email with the contact info of the user and the soclicitor",
            "parameters": {
                "type": "object",
                "properties": {
                    "quote": {
                        "type": "string",
                        "description": "description of user's problem statement and resolution",
                    },
                    "name": {"type": "string", "description": "User's name"},
                    "email": {
                        "type": "string",
                        "description": "User's email address",
                    },
                    "phone": {
                        "type": "string",
                        "description": "User's Phone number",
                    },
                    "solicitor": {
                        "type": "string",
                        "description": "name, email & phone number of solicitor",
                    },
                },
            },
        },
    },
]
# st.title("24/7-Law Legal Advice")
# st.write("#### *AI based chat application demo for 24/7-Law*")

if question := text_box.text_input(
    "I'm Hamilton, your legal assistant. How can I help you today?",
    value="",
    key=key,
):
    # Indicate that the input should be cleared on the next rerun
    st.session_state.clear_input = True
    # print(json.dumps(tools, indent=4))
    # Convert the user input into the expected dictionary format before appending
    # user_message = {"role": "user", "content": prompt}
    st.session_state.text_boxes.append(st.empty())
    st.session_state.text_boxes[-1].success(f"**> 🤔 User:** {question}")
    st.session_state.conversation_history.append(question)
    # print("Looping")
    with st.spinner("Don't ..🍷.. & __🚗__. 🪱 🤸 W0rk1ng 🤸 🪱"):
        # Add the user's message to the existing thread
        message = client.beta.threads.messages.create(
            thread_id=st.session_state.thread_id, role="user", content=question
        )
        # Step: Create a run with additional instructions
        with client.beta.threads.runs.create_and_stream(
            thread_id=st.session_state.thread_id,
            assistant_id=assistant_247.id,
            additional_instructions="""Always nudge the client to consider 24/7-Law services. Also answer the questions by first referring to the stored documents (knowledge base) for context.
                                        when the client expresses interest in using our service always ask him to provide their **Name, E-mail & Phone Number** (display in bold) so that we can ensure 
                                        that a partner (solicitor) will get in touch with him.  """,
            event_handler=EventHandler(),
            tools=[
                {"type": "retrieval"},
                {"type": "code_interpreter"},
                {
                    "type": "function",
                    "function": {
                        "name": "send_email",
                        "description": "Sends an email with the contact info of the user and the soclicitor",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "quote": {
                                    "type": "string",
                                    "description": "description of user's problem statement and resolution",
                                },
                                "name": {
                                    "type": "string",
                                    "description": "User's name",
                                },
                                "email": {
                                    "type": "string",
                                    "description": "User's email address",
                                },
                                "phone": {
                                    "type": "string",
                                    "description": "User's Phone number",
                                },
                                "solicitor": {
                                    "type": "string",
                                    "description": "name, email & phone number of solicitor",
                                },
                            },
                        },
                    },
                },
            ],
        ) as stream:
            stream.until_done()

        messages = client.beta.threads.messages.list(
            thread_id=st.session_state.thread_id
        )
        # st.session_state.messages = messages

# st.toast("😄 😸 😄")
