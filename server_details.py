import mysql.connector
import streamlit as st
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from pymongo import MongoClient



# # ###########################################################################################
# #                                      PART: API details
# # ###########################################################################################
def get_youtube_api_build():
    st.set_page_config(layout="wide")   
    st.markdown("<h1 style='text-align: center; color: yellow;'>Welcome to Youtube data migration tool UI</h1><br><br>", unsafe_allow_html=True)
    st.markdown("<span style='color: green;'> API KEY  (Note: Default is entered below, change accordingly!) </span>", unsafe_allow_html=True)    
    
    # Initialize session state variables (cached) 
    if 'API_KEY' not in st.session_state:
        st.session_state.API_KEY = None
    if 'youtube' not in st.session_state:
        st.session_state.youtube = None        
    
    st.session_state.API_KEY = st.text_input("Enter your YouTube API Key", value='AIzaSyBoM0gvt1tFk42z7KQrV6Etsff-15781GE')
    if not st.session_state.API_KEY:
        st.warning("Please enter your YouTube API Key.")        
    else:    
        st.session_state.youtube = build('youtube', 'v3', developerKey=st.session_state.API_KEY)    
    st.write("---")   

# # ###########################################################################################
# #                                      PART: MySQL server details
# # ###########################################################################################
def MySQL_server_details_UI():
    st.markdown("<span style='color: green;'> Enter your MySQL server details (Note: Default is entered below, change accordinly!)</span>", unsafe_allow_html=True)    
    
    if 'localhost' not in st.session_state:
        st.session_state.localhost = None
    if 'root' not in st.session_state:
        st.session_state.root = None      
    if 'passwd' not in st.session_state:
        st.session_state.passwd = None
        
    st.session_state.localhost = st.text_input("Enter hostname", value='localhost')  
    st.session_state.root = st.text_input("Enter username", value='root')
    st.session_state.passwd = st.text_input("Password", value='Vikas@123')   
    return st.session_state.localhost, st.session_state.root, st.session_state.passwd


# # ###########################################################################################
# #                                      PART: MonogoDB server details
# # ###########################################################################################
def mongoDB_server_details_UI():     
    st.markdown("<span style='color: green;'> Enter your MongoDB hostname Note: Default is entered below, change accordingly!</span>", unsafe_allow_html=True)   
    if 'mongoDB_host' not in st.session_state:
        st.session_state.mongoDB_host = []    

    st.session_state.mongoDB_host = st.text_input("Enter hostname", value='mongodb://localhost:27017/')  
    st.write("---")
    return st.session_state.mongoDB_host
        