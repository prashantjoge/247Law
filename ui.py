import streamlit as st
import openai

# Set your OpenAI API key here


def send_message(message):
    response = openai.completions.create(
        model="gpt-4.5-turbo",
        prompt="You are a helpful assistant.",
    )
    return response.choices[0].text


# Streamlit app UI
st.title("GPT-3 Assistant")

user_input = st.text_input("Message to the assistant:", "")

if user_input:
    # Send the message to the assistant and get the response
    response = send_message(user_input)
    st.text_area(
        "Assistant Response:", value=response, height=300, max_chars=None, disabled=True
    )
