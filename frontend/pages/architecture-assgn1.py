import os
import streamlit as st
from PIL import Image

#To set the page configurations
st.set_page_config(page_title="Asn2", page_icon='❷', layout="wide", initial_sidebar_state="auto", menu_items=None)

image = Image.open(os.getcwd() + '/images/pdf_processing_flow.png')

st.markdown("<h1 style='text-align: center;'>Architecture Diagram (Assignment 1)</h1>", unsafe_allow_html=True)
st.image(image, use_column_width=True)