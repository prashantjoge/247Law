# Import necessary libraries
from openai import OpenAI
import streamlit as st
import time
from tenacity import retry, wait_random_exponential, stop_after_attempt

# from termcolor import colored
import os
import datetime
import json
import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import mailtrap as mt
import base64
from email.mime.text import MIMEText
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from requests import HTTPError

# Set up the Streamlit page with a title and icon
#
#
st.set_page_config(
    page_title="ChatGPT-like Chat App for 24/7-Law", page_icon=":speech_balloon:"
)

st.session_state.openai_model = "gpt-4-turbo-preview"
st.sidebar.title("🤖 GPTs")
avatar = {"assistant": "🤖", "user": "👲"}
tools = {"code_interpreter": "🐍", "retrieval": "🔎", "function": "💬"}
# api_key = st.secrets["OPEN_AI_KEY"]
# Set your OpenAI Assistant ID here
assistant_id = "asst_eesDRw8EeDBbwWtg3oEdhsvV"
# st.write(st.session_state)

api_key = os.environ["OPENAI_API_KEY"]
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
    messages = client.beta.threads.messages.list(thread_id=thread.id)
    st.session_state.messages = []
# messages = st.session_state.messages


# Create a thread once and store its ID in session state
# thread_id = st.session_state.th
# # Display existing messages in the chat
# for message in st.session_state.messages:
#     with st.chat_message("assistant"):
#         print("Message:", message)
#         st.markdown(message)
# #
# Create a sidebar for API key configuration and additional features
st.sidebar.header("Assistants")
list_of_assistants = client.beta.assistants.list()
# st.write(list(list_of_assistants))
assistant = st.sidebar.selectbox(
    "Select Assistant", list_of_assistants, format_func=lambda assistant: assistant.name
)
# st.sidebar.write(assistant)
assistant_tools = [tool.type for tool in assistant.tools]
assistant_tools_emojis = [tools[tool.type] for tool in assistant.tools]
# [tools[tool["type"]] for tool in assistant["tools"]]
# api_key = st.sidebar.text_input("Enter your OpenAI API key", type="password")
if api_key:
    OpenAI.api_key = os.environ["OPENAI_API_KEY"]


st.sidebar.write(f"**ID**:\n{assistant.id}")
# st.sidebar.write(f"**Instructions**:\n{assistant.instructions}")
st.sidebar.write(f"**Model**:\n{assistant.model}")
st.sidebar.write(f"**Tools**:\n{list(zip(assistant_tools, assistant_tools_emojis))}")
# Main chat interface setup
st.title("24/7-Law Legal Advice")
st.write(
    "#### *AI based chat application demo for 24/7-Law*",
)


st.sidebar.write("## Thread")
# st.sidebar.write(thread)
st.sidebar.write(f"*{st.session_state.thread_id}*")
st.sidebar.write(
    f"Created at {datetime.datetime.fromtimestamp(st.session_state.created_at)}"
)


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
    creds = flow.run_local_server(port=0)
    if not quote:
        print("Error: 'quote' argument is required but was not provided.")
        return  # Handle the missing argument appropriately
    # Print the quote and recipient for debugging purposes
    print(f"Generated quote:\n {quote}\n\nSending via email to: {email}")
    sender_email = "sethgofiger@gmail.com"  # Your email
    # sender_password = "Hello65596%%9"  # Your email password
    # clientid= 742057514622-kbv36325hch37c1g09k41ua36hodgvgk.apps.googleusercontent.com
    # vlientsecret= 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
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
                        <p>Based on the information you shared, here are your contact details </p>
                        <p><b>email</b> : {email}  <b>phone</b> : {phone} <br></p>
                        <p>For more info you may reach us @ <a href="http://www.247-Law.com">247-Law</a> <br>.</p>
                        You have been assigned to {solicitor} <br>
                        In the next 24 hours, he will get in touch with you.
                        <div class="footer">
                                Contact Us: adam@247-law.com | 777-777-7777<br>
                                Unsubscribe from these emails <a href="#">here</a>.
                        </div>
                        </p>
                    </body>
                    </html>
                    """
    # .format(quote=quote,name=name, email=email,phone=phone,solicitor=solicitor)
    # quote_part = MIMEText(quote, "html")
    # solicitor_part = MIMEText(solicitor, "html")
    # msg.attach(quote_part)
    # msg.attach(solicitor_part)
    html_part = MIMEText(html_content, "html")
    msg.attach(html_part)
    msg["From"] = sender_email
    msg["To"] = email
    msg["Subject"] = "Message from 24/7-Law on your recent enquiry"
    #
    # body = f"Generated quote:\n {quote}\n\n"
    # msg.attach(MIMEText(body, "plain"))
    # context = ssl.create_default_context()
    # # SMTP server setup (using Gmail's SMTP server as an example)
    # server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
    # server.starttls()
    create_message = {"raw": base64.urlsafe_b64encode(msg.as_bytes()).decode()}
    try:
        message = (
            service.users().messages().send(userId="me", body=create_message).execute()
        )
        print(f'sent message to {message} Message Id: {message["id"]}')
        # mail = mt.Mail(
        #     sender=mt.Address(email=sender_email, name="24/7 Law"),
        #     to=[mt.Address(email=email)],
        #     subject="Your Quote",
        #     text=quote,
        # )
        # create client and send
        # client = mt.MailtrapClient(token="38e1082fbb6bd567bc6466d96c551a29")
        # client.send(mail)

        # server.login(sender_email, sender_password)
        # text = msg.as_string()
        # server.sendmail(sender_email, email, text)
        # server.quit()
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
                    "email": {"type": "string", "description": "User's email address"},
                    "phone": {"type": "string", "description": "User's Phone number"},
                    "solicitor": {
                        "type": "string",
                        "description": "name, email & phone number of solicitor",
                    },
                },
            },
        },
    },
]
# Only show the chat interface if the chat has been started
# st.session_state.messages = []
# print(messages)
# Display existing messages in the chat
# for message in st.session_state.messages:
#     with st.chat_message("user"):
#         st.markdown(message)
#
# print("Before Looping")
# Step Chat input for the user
if prompt := st.chat_input(
    "I'm Hamilton, your legal assistant. How can I help you today?"
):
    # print("Looping")
    with st.spinner("Don't ..🍷.. & __🚗__. 🪱 🤸 W0rk1ng 🤸 🪱"):
        # Display existing messages in the chat
        # for message in st.session_state.messages:
        #     with st.chat_message("user"):
        #         st.markdown(message)
        #
        # with st.chat_message("assistant"):
        # st.markdown(message)

        # Add the user's message to the existing thread
        messages = client.beta.threads.messages.create(
            thread_id=st.session_state.thread_id, role="user", content=prompt
        )
        # Add the user's message to the existing thread
        # client.beta.threads.messages.create(
        #    thread_id=st.session_state.thread_id, role="user", content=prompt
        # )

        # Step: Create a run with additional instructions
        run = client.beta.threads.runs.create(
            thread_id=st.session_state.thread_id,
            assistant_id=assistant_id,
            additional_instructions="""Always nudge user to consider 24/7-Law services. Also answer the questions by first referring to the stored documents for context.
                                        when the user expresses interest in using our service always ask him to provide his name, email & phone number so that we can ensure 
                                        that a partner (solicitor) will get in touch with him. The default contact details of the solicitor to be provided in response email is
                                        'Raj Joshi', 'raj.joshi@greatjames.co.uk>', '020 7440 4949' (*DO NOT PROVIDE THIS TO THE USER ON SCREEN*).  """,
            tools=tools,
        )
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
                name = tool_call.function.name
                arguments = json.loads(tool_call.function.arguments)
                print("Waiting for custom Function:", name)
                print("Function arguments:")
                print(arguments)
                task = send_email(**arguments)
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
            # Retrieve messages added by the assistant
            run = client.beta.threads.runs.retrieve(
                thread_id=st.session_state.thread_id, run_id=run.id
            )
            # assistant_messages_for_run = [message for message in messages]
            # print(assistant_messages_for_run.__str__)

            # st.session_state.run = run
            st.toast(run.status)

            # Add user message to the state and display it
        # st.session_state.messages.append({"role": "user", "content": prompt})

        ## step 5 - Get messages
        messages = client.beta.threads.messages.list(
            thread_id=st.session_state.thread_id
        )
        # st.session_state.messages = messages
    st.toast("😄 😸 😄")

    # messages = client.beta.threads.messages.list(thread_id=st.session_state.thread_id)
    # st.markdown(st.session_state.thread_id + ":" + run.id)
    # with st.chat_message("assistant"):
    #    st.markdown(messages.data[0].content[0].text.value, unsafe_allow_html=True)
    for line in messages.data[::-1]:
        st.chat_message(line.role, avatar=avatar[line.role]).write(
            line.content[0].text.value
        )
