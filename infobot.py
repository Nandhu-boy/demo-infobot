import os
import sqlite3
import pandas as pd
import streamlit as st
import speech_recognition as sr
from gtts import gTTS
from langdetect import detect, LangDetectException
from indic import transliterate_text
from infoai import Gen_Ai

# Set page configuration
st.set_page_config(
    page_title="InfoBot",
    layout="wide",
    
    initial_sidebar_state="expanded",
    page_icon="🤖"
)

# Custom CSS for styling
st.markdown(
    """
    <style>
    .stApp {
        background-color: #001f3f; /* Navy blue background */
        color: white; /* White text */
        display: flex;
        flex-direction: column;
        height: 100vh;
    }
    .css-1d391kg { /* Chat bubble styling */
        background-color: #001f3f;
        color: white;
    }
    .css-184tjsw p { /* Chat text styling */
        color: white;
    }
    .stButton button {
        background-color: #ffffff;
        color: #001f3f;
        border-radius: 5px; 
        display: flex;
        justify-content: flex-end; /* Aligns content to the right */
        padding: 10px;
    }
    .footer {
        position: fixed;
        bottom: 0;
        left: 0;
        width: 100%;
        text-align: center;
        padding: 10px;
        background-color: #001f3f;
        color: white;
    }
    .title{
        text-align: center;
    }
    </style>
    """,
    unsafe_allow_html=True
)

def play_audio(text, lang='en'):
    try:
        tts = gTTS(text=text, lang=lang)
        audio_file = "temp_audio.mp3"
        tts.save(audio_file)
        
        with open(audio_file, "rb") as f:
            audio_bytes = f.read()
            st.audio(audio_bytes, format='audio/mp3')

        os.remove(audio_file)
    except Exception as e:
        st.error(f"Error generating audio: {e}")

def detect_language(text):
    try:
        return detect(text)
    except LangDetectException:
        return 'en'
    except Exception as e:
        st.error(f"Error detecting language: {e}")
        return 'en'

def main():
    st.title("InfoBot 🤖")

    # # Sidebar for uploading CSV files
    # with st.sidebar:
    #     st.subheader("Upload CSV Files")
    #     uploaded_files = st.file_uploader("Upload CSV files", accept_multiple_files=True)
    #     if uploaded_files:
    #         for uploaded_file in uploaded_files:
    #             file_path = os.path(r"C:\Users\ARULMURUGAN M\OneDrive\Desktop\ai\student_details.csv")
    #             with open(file_path, "wb") as f:
    #                 f.write(uploaded_file.getbuffer())
    #         from infocsv import CSV_2_DB
    #         CSV_2_DB()
    #         st.write(":green[DB created]")

    # Initialize conversation history
    if "conversation" not in st.session_state:
        st.session_state.conversation = []

    # Display chat history
    chat_container = st.container()
    for message in st.session_state.conversation:
        with chat_container:
            st.markdown(message)

    # Add search bar at the bottom
    with st.container():
        user_query = st.text_input("Enter your query", key="query_input", label_visibility="collapsed")

    # Button to record voice query
    if st.button("🎙️"):
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            st.write("Listening...")
            audio = recognizer.listen(source)
            try:
                user_query = recognizer.recognize_google(audio)
                detected_language = detect_language(user_query)
                st.write(f"Recorded Query: {user_query}")
                st.write(f"Detected Language: {detected_language}")

            except sr.UnknownValueError:
                st.error("Sorry, I could not understand the audio.")
                return
            except sr.RequestError:
                st.error("Sorry, there was an issue with the speech recognition service.")
                return
    else:
        detected_language = detect_language(user_query) if user_query else 'en'

    # If there is a user query, process it
    if user_query:
        try:
            # Get response from AI model
            result, _ = Gen_Ai(user_query, detected_language)
            st.session_state.conversation.append(f"**You:** {user_query}")
            st.session_state.conversation.append(f"**Bot:** {result}")

            # Display response
            st.write(f":green[{result}]")

            # Play response audio
            play_audio(result, lang=detected_language)
        except Exception as e:
            st.error(f"Error: {e}")

if __name__ == "__main__":
    main()
