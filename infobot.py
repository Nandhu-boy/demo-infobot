import os
import streamlit as st
import speech_recognition as sr
from gtts import gTTS
from langdetect import detect, LangDetectException
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
            st.session_state.conversation.append(f"**You:** {user_query}")
            st.session_state.conversation.append(f"**INFOBOT:** {result}")

            # Display response
            st.write(f":green[{result}]")

            # Icon buttons under the response
            st.markdown(
                f"""
                <div class="icon-container">
                    <button class="icon-button" title="Like" id="like_button">👍</button>
                    <button class="icon-button" title="Save">💾</button>
                    <button class="icon-button" title="Copy" id="copy_button">📋</button>
                    <button class="icon-button" title="Read Aloud">🔊</button>
                </div>
                """,
                unsafe_allow_html=True
            )

            # JavaScript for copying response text
            st.write(f"""
                <script>
                document.getElementById("copy_button").addEventListener("click", function() {{
                    navigator.clipboard.writeText("{result}");
                    alert("Copied to clipboard!");
                }});
                document.getElementById("like_button").addEventListener("click", function() {{
                    const message = "{result}";
                    let likedMessages = JSON.parse(localStorage.getItem("liked_messages") || "[]");
                    if (!likedMessages.includes(message)) {{
                        likedMessages.push(message);
                        localStorage.setItem("liked_messages", JSON.stringify(likedMessages));
                        alert("Message liked!");
                    }}
                }});
                </script>
            """, unsafe_allow_html=True)

            # Play response audio if "Read Aloud" button is clicked
            if st.button("🔊", key="play_audio"):
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
    st.write("""
        <script>
        document.querySelector("button[title='Likes']").addEventListener("click", function() {
            const likedMessages = JSON.parse(localStorage.getItem("liked_messages") || "[]");
            const likedMessagesList = document.getElementById("liked_messages_list");
            likedMessagesList.innerHTML = likedMessages.map(message => `<p>${message}</p>`).join("");
        });
        </script>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
