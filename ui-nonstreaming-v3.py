# Import necessary libraries
from openai import OpenAI
import streamlit as st
import time
import random
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
from requests import HTTPError, api

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


def get_random_solicitor():
    # Select a random record
    random_solicitor = random.choice(solicitors)

    # Format the selected solicitor's information and background into a string
    solicitor_info = f"Name: {random_solicitor['name']}, Email: {random_solicitor['email']}, Phone: {random_solicitor['phone']}, Background: {random_solicitor['background']}"

    return solicitor_info


def extract_background(solicitor_info):
    # Find the start of the "Background" section
    start = solicitor_info.find("Background: ")

    # Adjust start position to skip the "Background: " part itself
    start += len("Background: ")

    # Extract the background information
    background = solicitor_info[start:]

    return background


def remove_background(solicitor_info):
    # Find the start of the "Background" section
    start = solicitor_info.find("Background: ")

    # If "Background: " is found, extract the string up to this point
    if start != -1:
        return solicitor_info[:start].strip()
    else:
        # If "Background: " is not found, return the original string
        return solicitor_info


# Set up the Streamlit page with a title and icon
#
# me and my girlfriend decided to go on a joyride on a scenic road in the suburb of Leeds in England.  The speed limit on the road was 20 KM and it was a  bidirectional road.  However there were some Sunday drivers in front of us who were blocking the scenic view ahead of us. We overtook a string of cars at about 40 KM's. Shortly after that we were pulled over for over speeding. We acknowledged that we were over speeding because we were just trying to overtake the other vehicles. The officer reminded that it was a no passing zone. We acknowledged and apologized. He was about to let us go when he noticed some empty beer cans on the back of the car. He wanted us to open the backdoor, but we immediately told him that we had a few beers on the way. he had me do a breath test and it showed 25.
# My concern is that I just got admitted to medical school and I am wondering if it will show up in a cbackground check
# Yes please , its Matt, prashant.thomas@verbat.com, 676-890-0987
st.set_page_config(
    page_title="ChatGPT-like Chat App for 24/7-Law", page_icon=":speech_balloon:"
)

st.session_state.openai_model = "gpt-4-turbo-preview"
st.sidebar.title("🤖 GPTs")
avatar = {"assistant": "🤖", "user": "👲"}
tools = {"code_interpreter": "🐍", "retrieval": "🔎", "function": "💬"}
assistant_id = "asst_eesDRw8EeDBbwWtg3oEdhsvV"
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
    messages = client.beta.threads.messages.list(thread_id=thread.id)
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
assistant_tools = [tool.type for tool in assistant.tools]
assistant_tools_emojis = [tools[tool.type] for tool in assistant.tools]
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


def convert_markdown_to_html(quote):
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


def get_quote_from_conversation_context(conversation_history):
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
            service.users().messages().send(userId="me", body=create_message).execute()
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
# response_1 = client.chat.completions.create(
#     model="gpt-3.5-turbo",
#     messages=[
#         {
#             "role": "system",
#             "content": "You are a helpful assistant capable of referring to documents. Consider all uploaded documents for this session.",
#         },
#         {
#             "role": "user",
#             "content": "Regarding the document on traffic violations, what advice is given for speeding?",
#         },
#     ],
# )
# print(response_1.choices[0].message)
if prompt := st.chat_input(
    "I'm Hamilton, your legal assistant. How can I help you today?"
):
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
            assistant_id=assistant_id,
            additional_instructions="""Always nudge the client to consider 24/7-Law services. Also answer the questions by first referring to the stored documents for context.
                                        when the client expresses interest in using our service always ask him to provide their **Name, E-mail & Phone Number** (display in bold) so that we can ensure 
                                        that a partner (solicitor) will get in touch with him.  """,
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
            # Retrieve messages added by the assistant
            run = client.beta.threads.runs.retrieve(
                thread_id=st.session_state.thread_id, run_id=run.id
            )
    st.toast(run.status)

    ## step 5 - Get messages
    messages = client.beta.threads.messages.list(thread_id=st.session_state.thread_id)
    # st.session_state.messages = messages
    st.toast("😄 😸 😄")

    for line in messages.data[::-1]:
        st.chat_message(line.role, avatar=avatar[line.role]).write(
            line.content[0].text.value
        )
