import streamlit as st
from langchain.schema.messages import AIMessage, HumanMessage
from client import BackendClient
from datetime import datetime

base_url = "http://api:8080"
client = BackendClient(base_url=base_url)

def main():
    st.set_page_config(
        page_title="GuardianBot",
        page_icon="🏦",
    )
    st.title("GuardianBot by Neeraj Sujan")
    st.subheader("Agent Demo")
    display_chat()

def display_chat():
    chat_history = get_chat_history()
    for message in chat_history:
        if isinstance(message, AIMessage):
            with st.chat_message("assistant"):
                st.write(message.content)
        if isinstance(message, HumanMessage):
            with st.chat_message("user"):
                st.write(message.content)

    if prompt := st.chat_input("Say something...", key="UNIQUE_KEY"):
        with st.chat_message("user"):
            st.markdown(prompt)
        st.session_state["chat_history"].append(HumanMessage(content=prompt))
        
        with st.chat_message("assistant"):
            response = react_to_message(prompt)
            st.markdown(response)
            st.session_state["chat_history"].append(AIMessage(content=response))
        st.experimental_rerun()

def react_to_message(message: str) -> str:
    try:
        response = client.make_post("chat", {"input": message})
        return response['response']
    except Exception as e:
        return f"Error communicating with server: {str(e)}"

def get_chat_history():
    if "chat_history" not in st.session_state:
        st.session_state["chat_history"] = [
            AIMessage(content="Hello! I am GuardianBot. How can I help you?")
        ]
    return st.session_state["chat_history"]

if __name__ == "__main__":
    main()
