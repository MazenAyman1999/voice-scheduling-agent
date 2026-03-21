import tempfile
import speech_recognition as sr
from gtts import gTTS


def speech_to_text(audio_file) -> str:
    """
    Convert uploaded audio file to text using Google Speech Recognition.
    Args:
        audio_file: Audio input file (Streamlit audio object).
    Returns:
        str: Transcribed text, or "[Unclear Audio]" if recognition fails.
    Notes:
        - Temporarily saves audio as a .wav file.
        - Handles unclear or unintelligible speech gracefully.
    """
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as file:
        file.write(audio_file.read())
        audio_path = file.name
    recognizer = sr.Recognizer()
    with sr.AudioFile(audio_path) as source:
        audio_data = recognizer.record(source)
    try:
        return recognizer.recognize_google(audio_data)
    except sr.UnknownValueError:
        return "[Unclear Audio]"

def text_to_speech(text: str) -> str:
    """
    Convert text into speech and save it as an MP3 file.
    Args:
        text (str): Text to convert into speech.
    Returns:
        str: Path to the generated MP3 file.
    Notes:
        - Uses Google Text-to-Speech (gTTS).
        - Temporarily saves audio as an MP3 file.
    """
    tts = gTTS(text)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as file:
        tts.save(file.name)
        return file.name