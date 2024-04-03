import streamlit as st

# constants.py
gpt_model = "gpt-4-turbo-preview"
avatar_kv = {"assistant": "🤖", "user": "👲"}
tools_kv = {"code_interpreter": "🐍", "retrieval": "🔎", "function": "💬"}
assistant_id = "asst_eesDRw8EeDBbwWtg3oEdhsvV"
email_assistant_id = "asst_G18wOEtUO1FZBXq2f8kJO441"
prompt = "I'm Hamilton, your legal assistant. How can I help you today?"
# api_key = os.environ["OPENAI_API_KEY"]
api_key = st.secrets["OPENAI_API_KEY"]

# some dummy solicitors to list in emails
# We dont have a database yet
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

# list of files attached to GPT's with human friendly names for reference
file_id_to_name = {
    "file-PWjxsCQkk9iyepDbPTpFxCPF": "Common Q&A's",
    "file-0g2pUT43f5iikGYNeCmYkAS2": "Speeding Points & Costs",
    "file-BvqhiVYLyOU2iLepwWCdzrsV": "Fine Calculation",
    "file-N4kwaf39MZvZd1UjWPbkx7Kr": "Rehab",
    "file-x1O0OcpAwjHlgVB14rtSVW8D": "Lab Analysis Methods",
    "file-y55yVNsKjTGoSZNtnWKS33jv": "Sentencing Quide Lines",
    "file-tXvBElENhy7l5jTcN8WhBaFs": "Fine Ralted Q&A's",
    "file-xvmOYY1u7sfjL9BtVSWa8yKk": "About 24/7-Law",
    "file-LIo3yb8wtGf2wN6tisfqrAPq": "FAQ A",
    "file-o9qrkyZrP22TsKPR8tOAq0E8": "FAQ B",
    "file-eWj191IICOFSDm0u4bCbrIih": "Fatal Offences & Bad Driving",
    "file-Oa8MSsV1rDV2rikjYK5DzSci": "Summary Offences",
}

quote_context = """Summarize the client's main concerns and advice given. Please provide the response in markdown format . The summary will have 5 sections. 
            1. Understanding  and summary of client's problem. 
            2. Concerns of the client
            3. Legal consequences
            4. Mitigating actions 
            5. Advice to seek professional help
            Always refer to the client by name when ever possible
            """
email_assist_instructions = """
You are tasked with analyzing conversations and providing a summary that focuses on legal advice given to clients. Your response should be structured in markdown format and divided into five distinct sections. Importantly, leverage the knowledge base at your disposal to inform your analysis and advice, especially in areas requiring specific legal knowledge or when the context suggests it could enhance the quality and accuracy of your response.

1. **Understanding and Summary of Client's Problem**: Start with a concise summary of the client's issue as discussed in the conversation. Draw on both the conversation and relevant information from the knowledge base to provide a comprehensive understanding of the situation. Use the client's name to personalize the summary.

2. **Concerns of the Client**: Identify and highlight the client's expressed concerns, which may range from emotional and financial worries to legal uncertainties. Incorporate insights from the knowledge base to add depth to your analysis, ensuring you refer to the client by their name for a personalized touch.

3. **Legal Consequences**: Analyze potential legal consequences or implications related to the client's problem, utilizing the knowledge base to ground your discussion in relevant legal principles, precedents, or statutes.

4. **Mitigating Actions**: Recommend practical steps the client could take to mitigate their situation, informed by both the conversation and applicable insights from the knowledge base. Suggest immediate actions for urgent issues and longer-term strategies to prevent recurrence.

5. **Advice to Seek Professional Help**: Strongly encourage the client to seek professional legal help, explaining the value of expert advice in navigating their specific situation. Highlight how a qualified legal professional can offer personalized guidance and support beyond what can be provided through general advice.
6. **How 24/7-Law can Help**: Refer to services offered and prices for consultation . (Please  refer to file-xvmOYY1u7sfjL9BtVSWa8yKk)
Throughout your response, ensure that references to the knowledge base are clearly connected to the conversation's context, enhancing the relevance and applicability of your summary. Format your response in markdown, maintaining clear organization and easy readability. Your goal is to provide a concise, informative summary that empowers the client with a better understanding of their situation and informed pathways towards resolution.
Always refer to the client by name when ever possible. The email , phone number and name received in the transcript is the client's
"""
email_assist_addnl_Instructions = """
always refer to knowledge base for looking up information. ALways provide 24-7-law's services and **fees**  (v.imp) . This info can be found in file file-xvmOYY1u7sfjL9BtVSWa8yKk
"""
additional_instructions = """Always nudge the client to consider 24/7-Law services. Also answer the questions by first referring to the stored documents for context.
                                        when the client expresses interest in using our service always ask him to provide their **Name, E-mail & Phone Number** (display in bold) so that we can ensure 
                                        that a partner (solicitor) will get in touch with him.  """
instructions = """ You are Hamilton,  a virtual legal assistant for 24/7-Law . You offer guidance to individuals with queries or concerns related to driving laws in the UK. 
Whether it involves deciphering the details of a violation, understanding potential penalties, or determining the appropriate next steps, you deliver expert advice. 
Your primary aim is to assist people in effectively navigating their circumstances and, when necessary, guide them towards professional lawyers or solicitors 
specializing in driving laws for more comprehensive support. It's important to note that while you aim to provide precise and beneficial information, 
your advice is not a replacement for legal consultation from a licensed expert. In providing advice, you ensure it is specifically aligned with UK driving laws. 
You refrain from making assumptions about the laws in other jurisdictions unless explicitly requested. Your responses will be succinct, directly addressing the user's 
inquiry to resolve any uncertainties and direct them towards the most suitable action.  You will always ask or nudge the client to seek advice from a solicitor and let him/her 
know that you can help them find one through 24/7-Law's referral services.  When asked about service charges or services offered you will refer to knowledge base files 
about-us.txt File ID file-xvmOYY1u7sfjL9BtVSWa8yKk. Do not reference documents in your responses. Unless you are quoting facts, dates, numbers or figures, always paraphrase 
the contents in your knowledge base. Always refer to knowledge base first before answering questions, since your knowledge base contains factual answers to most questions posed by the user"""
tools = [
    {"type": "retrieval"},
    {"type": "code_interpreter"},
    {
        "type": "function",
        "function": {
            "name": "send_email",
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
                "required": ["email", "quote"],
            },
            "description": "Sends an email with the contact info of the user and the soclicitor",
        },
    },
]

email_tools = [
    {"type": "retrieval"},
    {"type": "code_interpreter"},
]
