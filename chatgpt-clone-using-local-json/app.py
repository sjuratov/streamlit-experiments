import streamlit as st
from openai import AzureOpenAI
import json
import os


DB_FILE = 'db.json'

def main():
    client = AzureOpenAI(
        api_key=st.secrets["AZURE_OPENAI_KEY"],
        azure_endpoint=st.secrets["AZURE_OPENAI_ENDPOINT"],
        api_version=st.secrets["AZURE_OPENAI_API_VERSION"]
    )

    st.sidebar.title("Chatbot Configuration")
    st.sidebar.divider()

    # List of models
    models = ["gpt-4o-mini", "gpt-4o"]

    # Create a select box for the models
    st.session_state["openai_model"] = st.sidebar.selectbox("Select model", models, index=0)

    # Create a temperature slider in sidebar and save the value in session state
    st.session_state.temperature = st.sidebar.slider("Select model temperature", 0.0, 1.0, 0.7, 0.1)

    # Load chat history from db.json
    with open(DB_FILE, 'r') as file:
        db = json.load(file)
    st.session_state.messages = db.get('chat_history', [])

    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Accept user input
    if prompt := st.chat_input("What is up?"):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        # Display user message in chat message container
        with st.chat_message("user"):
            st.markdown(prompt)

        # Display assistant response in chat message container
        with st.chat_message("assistant"):
            stream = client.chat.completions.create(
                model=st.session_state["openai_model"],
                messages=[
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.messages
                ],
                stream=True,
                temperature=st.session_state.temperature
            )
            response = st.write_stream(stream)
        st.session_state.messages.append({"role": "assistant", "content": response})

        # Store chat history to db.json
        db['chat_history'] = st.session_state.messages
        with open(DB_FILE, 'w') as file:
            json.dump(db, file)

    st.sidebar.divider()

    # Add a "Clear Chat" button to the sidebar
    if st.sidebar.button('Clear Chat'):
        # Clear chat history in db.json
        db['chat_history'] = []
        with open(DB_FILE, 'w') as file:
            json.dump(db, file)
        # Clear chat messages in session state
        st.session_state.messages = []
        st.rerun()


if __name__ == '__main__':

    # if the DB_FILE not exists, create it
    if not os.path.exists(DB_FILE):
        with open(DB_FILE, 'w') as file:
            db = {
                'chat_history': []
            }
            json.dump(db, file)
    # load the database
    else:
        with open(DB_FILE, 'r') as file:
            db = json.load(file)

    main()