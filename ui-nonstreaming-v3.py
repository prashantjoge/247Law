# Import necessary libraries
from openai import OpenAI
import streamlit as st
import time
from constants import (
    assistant_id,
    avatar_kv,
    tools_kv,
    file_id_to_name,
    quote_context,
    tools,
    gpt_model,
    instructions,
    additional_instructions,
    prompt,
)
from helpers import (
    get_random_solicitor,
    extract_background,
    remove_background,
    convert_markdown_to_html,
    get_quote_from_conversation_context,
)

# from termcolor import colored
import os
import datetime
import json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import base64
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.errors import HttpError

# List of fictitious solicitor records

SCOPES = ["https://www.googleapis.com/auth/contacts.readonly"]


# Set up the Streamlit page with a title and icon
#
# me and my girlfriend decided to go on a joyride on a scenic road in the suburb of Leeds in England.  The speed limit on the road was 20 KM and it was a  bidirectional road.  However there were some Sunday drivers in front of us who were blocking the scenic view ahead of us. We overtook a string of cars at about 40 KM's. Shortly after that we were pulled over for over speeding. We acknowledged that we were over speeding because we were just trying to overtake the other vehicles. The officer reminded that it was a no passing zone. We acknowledged and apologized. He was about to let us go when he noticed some empty beer cans on the back of the car. He wanted us to open the backdoor, but we immediately told him that we had a few beers on the way. he had me do a breath test and it showed 25.
# My concern is that I just got admitted to medical school and I am wondering if it will show up in a cbackground check
# Yes please , its Matt, prashant.thomas@verbat.com, 676-890-0987
st.set_page_config(
    page_title="ChatGPT-like Chat App for 24/7-Law", page_icon=":speech_balloon:"
)

st.session_state.openai_model = gpt_model
st.sidebar.title("🤖 GPTs")
# st.write(st.session_state)


# api_key = os.environ["OPENAI_API_KEY"]
api_key = st.secrets["OPENAI_API_KEY"]
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
assistant = st.sidebar.selectbox(
    "Select Assistant", list_of_assistants, format_func=lambda assistant: assistant.name
)
# st.sidebar.write(assistant)
my_assistant = client.beta.assistants.retrieve(assistant_id)
assistant_tools = [tool.type for tool in my_assistant.tools]
assistant_tools_emojis = [tools_kv[tool.type] for tool in my_assistant.tools]
if api_key:
    OpenAI.api_key = os.environ["OPENAI_API_KEY"]


st.sidebar.write(f"**ID**:\n{my_assistant.id}")
# st.sidebar.write(f"**Instructions**:\n{assistant.instructions}")
st.sidebar.write(f"**Model**:\n{my_assistant.model}")
st.sidebar.write(f"**Tools**:\n{list(zip(assistant_tools, assistant_tools_emojis))}")
# Main chat interface setup
st.title("24/7-Law Legal Advice")
st.write(
    "#### *AI based chat application demo for 24/7-Law*",
)

st.sidebar.write("## Thread")
st.sidebar.write(f"*{st.session_state.thread_id}*")
st.sidebar.write(
    f"Created at {datetime.datetime.fromtimestamp(st.session_state.created_at)}"
)
# Assuming 'my_assistant.file_ids' contains a list of file IDs
file_ids = my_assistant.file_ids
# Map file IDs to their human-friendly names
file_names = [
    file_id_to_name[file_id] for file_id in file_ids if file_id in file_id_to_name
]
# Writing file IDs to the sidebar
# Display the human-friendly names in the sidebar
st.sidebar.write("### Files")
for file_id, file_name in file_id_to_name.items():
    tooltip_html = f'<span title="{file_id}">📖 {file_name}</span>'
    st.sidebar.markdown(tooltip_html, unsafe_allow_html=True)


def google_autorization():
    # If modifying these scopes, delete the file token.json.
    """Shows basic usage of the People API.
    Prints the name of the first 10 connections.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "client_secret-apps.googleusercontent.com", SCOPES
            )
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    # try:
    #     service = build("people", "v1", credentials=creds)
    #
    #     # Call the People API
    #     print("List 10 connection names")
    #     results = (
    #         service.people()
    #         .connections()
    #         .list(
    #             resourceName="people/me",
    #             pageSize=10,
    #             personFields="names,emailAddresses",
    #         )
    #         .execute()
    #     )
    #     connections = results.get("connections", [])
    #
    #     for person in connections:
    #         names = person.get("names", [])
    #         if names:
    #             name = names[0].get("displayName")
    #             print(name)
    # except HttpError as err:
    #     print(err)

    return creds


# Function to send an email with a quote
def send_email(
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
    # creds = google_autorization()
    creds = flow.run_local_server(port=0)
    print("Quote: ", quote)
    print("Solicitor:", solicitor)
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
                    <head><style>
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
</head>
                    <body>
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
            service.users().messages().send(userId="me", body=create_message).execute()
        )
        print(f'sent message to {message} Message Id: {message["id"]}')
        return f"Message sent to {email}"

    except HttpError as error:
        print(f"Error: {error}")
        return "Failed to send email."


if prompt := st.chat_input(prompt):
    if prompt:
        # Convert the user input into the expected dictionary format before appending
        user_message = {"role": "user", "content": prompt}
        st.session_state.conversation_history.append(user_message)
    # print("Looping")
    with st.spinner("Don't ..🍷.. & __🚗__. 🪱 🤸 W0rk1ng 🤸 🪱"):
        # Add the user's message to the existing thread
        messages = client.beta.threads.messages.create(
            thread_id=st.session_state.thread_id, role="user", content=prompt
        )
        # Step: Create a run with additional instructions
        run = client.beta.threads.runs.create(
            thread_id=st.session_state.thread_id,
            assistant_id=my_assistant.id,
            instructions=instructions,
            additional_instructions=additional_instructions,
            tools=tools,
        )
        # The default contact details of the solicitor to be provided in response email is 'Raj Joshi', 'raj.joshi@greatjames.co.uk', '020 7440 4949' (*DO NOT PROVIDE THIS TO THE USER ON SCREEN*).
        st.toast(run.status)

        ## Step: Get run's status and steps
        # Poll for the run to complete and retrieve the assistant's messages
        # with st.spinner("Wait... Generating response..."):

        while run.status != "completed":
            # time.sleep(1)
            run_steps = client.beta.threads.runs.steps.list(
                thread_id=st.session_state.thread_id, run_id=run.id
            )
            if run.status == "requires_action":
                tool_call = run.required_action.submit_tool_outputs.tool_calls[0]
                action_name = (
                    tool_call.function.name
                )  # This gets the name of the function to be called
                # print("Tool Call:", tool_call)
                name = tool_call.function.name
                arguments = json.loads(tool_call.function.arguments)
                # print("Waiting for custom Function:", name)
                print("Function name:", name)
                # print(arguments)
                # Check if the required action is 'send_email' before proceeding
                if action_name == "send_email":
                    # if "quote" not in arguments:
                    quote = get_quote_from_conversation_context(
                        st.session_state.conversation_history
                    )
                    html_quote = convert_markdown_to_html(quote)
                    arguments["quote"] = html_quote
                    print("Quote Generated: ", arguments["quote"])
                    random_solicitor = get_random_solicitor()
                    arguments["solicitor"] = random_solicitor
                    task = send_email(**arguments)
                else:
                    # Handle other actions as needed
                    print(
                        f"Action required is not to send an email, but to: {action_name}"
                    )
                run = client.beta.threads.runs.submit_tool_outputs(
                    thread_id=st.session_state.thread_id,
                    run_id=run.id,
                    tool_outputs=[
                        {
                            "tool_call_id": tool_call.id,
                            "output": "done",
                        }
                    ],
                )
            # print(run_steps)
            st.toast(run_steps)
            time.sleep(1)
            # Retrieve run status
            run = client.beta.threads.runs.retrieve(
                thread_id=st.session_state.thread_id, run_id=run.id
            )
    st.toast(run.status)

    ## step 5 - Get messages
    messages = client.beta.threads.messages.list(thread_id=st.session_state.thread_id)

    # st.session_state.messages = messages
    st.toast(messages)
    st.toast("😄 😸 😄")

    for line in messages.data[::-1]:
        message_content = line.content[0].text
        annotations = message_content.annotations
        content = message_content.value
        citations = []
        # Iterate over the annotations and add footnotes
        for index, annotation in enumerate(annotations):
            # Replace the text with a footnote
            message_content.value = message_content.value.replace(
                annotation.text, f" [{index}]"
            )

            # Gather citations based on annotation attributes
            if file_citation := getattr(annotation, "file_citation", None):
                cited_file = client.files.retrieve(file_citation.file_id)
                citations.append(
                    f"[{index}] {file_citation.quote} from {cited_file.filename}"
                )
            elif file_path := getattr(annotation, "file_path", None):
                cited_file = client.files.retrieve(file_path.file_id)
                citations.append(
                    f"[{index}] Click <here> to download {cited_file.filename}"
                )
            content += "\n" + "\n".join(citations)

            # Note: File download functionality not implemented above for brevity
        st.chat_message(line.role, avatar=avatar_kv[line.role]).write(content)
