import streamlit as st
import re
import requests
import io
import time
import datetime
import os

FASTAPI_SERVER_URL = st.secrets['FASTAPI_SERVER_URL']

#To set the page configurations
st.set_page_config(page_title="Asn2", page_icon='❷', layout="wide", initial_sidebar_state="auto", menu_items=None)

# Initialize Streamlit
st.title("Q&A Chatbot for PDFs")

# PDF Link Validator
pdf_link_validator = re.compile(r'https?://\S+$')

# PDF Processor Options
pdf_processor = st.radio("Choose the PDF Processor:", ["Nougat", "PyPDF"])

if pdf_processor == "Nougat":
    nougatAPIServerURL = st.text_input("Link to Nougat API Server", help="Enter the link to the Nougat API Server")

# Define an empty list to store PDF links
pdf_links_list = []

# Input PDF links from the user
pdf_links = st.text_area("Enter PDF Links (one per line)", help="Enter the links to the PDFs you want to process, one link per line.")
input_links = pdf_links.split('\n')
duplicate_links = set()
for idx, link in enumerate(input_links, start=1):
    if re.search(pdf_link_validator, link):
        if link in pdf_links_list:
            duplicate_links.add(link)
            if duplicate_links:
                st.warning(f"Duplicate PDF URLs detected: {', '.join(duplicate_links)}. Please correct these URLs before proceeding.")
        else:
            pdf_links_list.append(link)

# Check for empty PDF links
if not pdf_links.strip():
    st.error("Please enter PDF links that you want to process.")
else:
    # Check for empty Nougat API server link
    if pdf_processor == "Nougat" and not nougatAPIServerURL:
        st.error("Please enter the Nougat API Server link.")
    else:
        if pdf_processor=="PyPDF" or pdf_processor=="Nougat":
            # Process PDFs
            if st.button("Process",key="model_success"):
                create_model_api_url = f"{FASTAPI_SERVER_URL}/v1/createFineTuneModel"

                create_model_response = None
                # Create the fine-tuned model
                if pdf_processor=="PyPDF":
                    create_model_response = requests.post(create_model_api_url, json={"referencePDFLinks": pdf_links_list})
                elif pdf_processor=="Nougat":
                    create_model_response = requests.post(create_model_api_url, json={"referencePDFLinks": pdf_links_list, 'nougatAPIServerURL':nougatAPIServerURL})
                
                if create_model_response.status_code == 201:
                    st.success("Fine-tuned model created successfully.")
                else:
                    st.error("Error while creating the fine-tuned model.")
                    
# Chat messages using st.session_state
if "messages" not in st.session_state:
    st.session_state["messages"] = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if user_question:= st.chat_input("Ask a question"):
        # Make a POST request to the FastAPI endpoint for a single question
        chat_answer_api_url = f"{FASTAPI_SERVER_URL}/v1/getChatAnswer"
        st.session_state.messages.append({"role": "user", "content": user_question})
        with st.chat_message("user"):
            st.markdown(user_question)

        # Get an answer for the single question
        with st.chat_message("assistant"):
            chat_response = requests.post(chat_answer_api_url, json={"chatQuestion": user_question})
            if chat_response.status_code == 200:
                chat_answer = chat_response.json()
                message_placeholder = st.empty()
                full_response = ""
                for chunk in chat_answer["chatAnswer"].split():
                    full_response += chunk + " "
                    time.sleep(0.05)
                    message_placeholder.markdown(full_response + "▌")
                    message_placeholder.markdown(full_response)
                # Add assistant response to chat history
                st.session_state.messages.append({"role": "assistant", "content": full_response})
            else:
                st.error("Error while fetching the chat answer")