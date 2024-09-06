import os
import streamlit as st
import speech_recognition as sr
from gtts import gTTS
from langdetect import detect, LangDetectException
from googletrans import Translator
from infoai import Gen_Ai
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

# Set page configuration
st.set_page_config(
    page_title="InfoBot",
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon="🤖"
)

# Initialize the translator
translator = Translator()

# Custom CSS for styling
st.markdown(
    """
    <style>
    .stApp {
        background-color: #001f3f;
        color: white;
    }
    .right-toolbar {
        position: fixed;
        top: 50%;
        right: 20px;
        transform: translateY(-50%);
        display: flex;
        flex-direction: column;
        gap: 15px;
    }
    .right-toolbar button {
        background-color: white;
        color: #001f3f;
        padding: 10px;
        border: none;
        border-radius: 50%;
        cursor: pointer;
    }
    .icon-container {
        display: flex;
        justify-content: space-around;
        margin-top: 10px;
    }
    .icon-button {
        background-color: white;
        color: #001f3f;
        border: none;
        border-radius: 50%;
        padding: 10px;
        cursor: pointer;
        font-size: 18px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Function to play audio using gTTS
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

# Detect the language of input text
def detect_language(text):
    try:
        return detect(text)
    except LangDetectException:
        return 'en'
    except Exception as e:
        st.error(f"Error detecting language: {e}")
        return 'en'

# Log the user query
def log_user_query(query, detected_language):
    try:
        # Translate the query to English
        translated_query = translator.translate(query, src=detected_language, dest='en').text

        # Create the CSV file if it doesn't exist
        if not os.path.exists("user_queries.csv"):
            with open("user_queries.csv", "w") as file:
                file.write("Query,Detected Language\n")  # Add headers

        # Log the translated query
        with open("user_queries.csv", "a") as file:
            file.write(f"{translated_query},{detected_language}\n")
    except Exception as e:
        st.error(f"Error translating query: {e}")

# Function to send email
def send_email(subject, body, to_email, attachment_path=None):
    from_email = "your_email@example.com"  # Replace with your email
    from_password = "your_password"  # Replace with your password

    # Create message container
    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject

    # Add body to email
    msg.attach(MIMEText(body, 'plain'))

    # Add attachment if provided
    if attachment_path:
        attachment = open(attachment_path, "rb")
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(attachment.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f'attachment; filename= {attachment_path}')
        msg.attach(part)
        attachment.close()

    # Send the email
    try:
        server = smtplib.SMTP('smtp.example.com', 587)  # Replace with your SMTP server and port
        server.starttls()
        server.login(from_email, from_password)
        text = msg.as_string()
        server.sendmail(from_email, to_email, text)
        server.quit()
        st.write("Email sent successfully!")
    except Exception as e:
        st.error(f"Error sending email: {e}")

# Function to export data and send it
def export_and_send_data(email):
    try:
        # Ensure file exists
        if os.path.exists("user_queries.csv"):
            send_email(
                subject="User Queries Data",
                body="Please find the attached user queries data.",
                to_email=email,
                attachment_path="user_queries.csv"
            )
        else:
            st.error("Data file does not exist.")
    except Exception as e:
        st.error(f"Error exporting and sending data: {e}")

# Main function
def main():
    st.title("InfoBot 🤖")

    # Initialize conversation history and liked messages
    if "conversation" not in st.session_state:
        st.session_state.conversation = []
    if "liked_messages" not in st.session_state:
        st.session_state.liked_messages = []

    # Sidebar for CSV file upload
    with st.sidebar:
        st.subheader("Upload CSV Files")
        uploaded_files = st.file_uploader("Upload CSV files", accept_multiple_files=True)
        if uploaded_files:
            for uploaded_file in uploaded_files:
                file_path = os.path.join(r"C:\\Users\\ARULMURUGAN M\\OneDrive\\Desktop\\ai\\demo", uploaded_file.name)
                with open(file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
            from infocsv import CSV_2_DB
            CSV_2_DB()
            st.write(":green[DB created]")

    # Display chat history
    chat_container = st.container()
    for message in st.session_state.conversation:
        with chat_container:
            st.markdown(message)

    # Right toolbar
    st.markdown(
        """
        <div class="right-toolbar">
            <button title="Community">👥</button>
            <button title="Likes" onclick="document.getElementById('liked_messages').style.display='block'">❤️</button>
            <button title="Settings">⚙️</button>
            <button title="Notifications">🔔</button>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Voice input (🎙️ button)
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
        user_query = st.text_input("Enter your query", label_visibility="collapsed", key="query_input")
        detected_language = detect_language(user_query) if user_query else 'en'

    # If user submits the query, process it
    if user_query:
        try:
            # Get response from AI model
            result, _ = Gen_Ai(user_query, detected_language)
            st.session_state.conversation.append(f"*You:* {user_query}")
            st.session_state.conversation.append(f"*INFOBOT:* {result}")

            # Display response
            st.write(f":green[{result}]")

            # Icon buttons under the response
            col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
            if col1.button("👍", key=f"like_{user_query}"):
                st.session_state.liked_messages.append(result)
                st.write(":green[Message liked!]")

            if col2.button("💾", key=f"save_{user_query}"):
                log_user_query(user_query, detected_language)
                st.write(":green[Query saved successfully.]")

            if col3.button("📋", key=f"copy_{user_query}"):
                st.write(":green[Response copied to clipboard.]")

            if col4.button("🔊", key=f"read_{user_query}"):
                play_audio(result, lang=detected_language)

        except Exception as e:
            st.error(f"Error: {e}")

    # Display liked messages
    st.markdown(
        """
        <div id="liked_messages" style="display:none;">
            <h3>Liked Messages:</h3>
            <div id="liked_messages_list"></div>
        </div>
        """,
        unsafe_allow_html=True
    )
    for liked_message in st.session_state.liked_messages:
        st.markdown(f"<div>{liked_message}</div>", unsafe_allow_html=True)

    # Add a text input for the college email
    college_email = st.text_input("Enter college email to send data to")

    # Add a button to export and send data
    if st.button("Send Data to College"):
        if college_email:
            export_and_send_data(college_email)
        else:
            st.error("Please enter a valid email address.")

if __name__ == "__main__":
    main()
