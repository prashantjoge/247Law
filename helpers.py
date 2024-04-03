import streamlit as st
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
)

from openai import OpenAI
import random


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

    return quote_html


def list_assistant_files(my_assistant):
    tooltip_html = ""
    # Assuming 'my_assistant.file_ids' contains a list of file IDs
    file_ids = my_assistant.file_ids
    # Map file IDs to their human-friendly names
    file_names = [
        file_id_to_name[file_id] for file_id in file_ids if file_id in file_id_to_name
    ]
    for file_id, file_name in file_id_to_name.items():
        tooltip_html += f'<span title="{file_id}">📖 {file_name}</br></span>'

    return tooltip_html


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
    print("quote context:", quote_context)
    # Prevent duplicate entries
    if conversation_history[-1]["content"] != quote_context:
        conversation_history.append({"role": "system", "content": quote_context})

    client = OpenAI()
    print(api_key)
    print("conversation history", conversation_history)
    client.api_key = api_key
    # Prepare the prompt for GPT-3
    #    prompt = f"The following is a conversation with a user seeking legal advice:\n{conversation_text}\n\nSummarize the user's main concerns and advice given:"
    try:
        completion = client.chat.completions.create(
            model=gpt_model, messages=conversation_history
        )

        # Extract the generated summary from the completion response
        summary = completion.choices[0].message.content
        return summary

    except Exception as e:
        st.toast(f"Error generating summary: {e}")
        return "Summary generation failed."
