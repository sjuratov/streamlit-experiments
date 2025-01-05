import streamlit as st
from openai import AzureOpenAI
import os
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential

from cosmosdb import get_cosmosdb_info, get_items, update_item, delete_item, create_item, create_unique_id

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

    # Load chat history from Cosmos DB
    if len(history) == 0:
        st.session_state.messages = []
    else:   
        st.session_state.messages = history[0]['chat_history']

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

        # Store chat history to Cosmos DB
        try:
            if len(history) == 0:
                item = {
                    "chat_history": st.session_state.messages,
                    "id": uuid,
                    "userId": uuid
                }
                create_item(container, item)
            else:
                history[0]['chat_history'] = st.session_state.messages
                update_item(container, history[0])
        except Exception as e:
            st.error(f"Error: {e}")

    st.sidebar.divider()

    # Add a "Clear Chat" button to the sidebar
    if st.sidebar.button('Clear Chat'):
        delete_item(container, history[0])
        # Clear chat messages in session state
        st.session_state.messages = []
        st.rerun()

if __name__ == '__main__':

    credential = DefaultAzureCredential()

    load_dotenv()

    accountName = os.getenv("accountName")
    databaseName = os.getenv("databaseName")
    containerName = os.getenv("collection")

    uuid = create_unique_id(credential)

    try:
        client, database, container = get_cosmosdb_info(credential=credential, endpoint=f"https://{accountName}.documents.azure.com:443/", database_name=databaseName, container_name=containerName)
        history = get_items(container, query = f"SELECT * FROM c WHERE c.userId = '{uuid}'")
    except Exception as e:
        st.error(f"Error: {e}")

    main()