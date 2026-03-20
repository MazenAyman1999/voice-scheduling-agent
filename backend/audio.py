import tempfile
import speech_recognition as sr
from gtts import gTTS


def speech_to_text(audio_file) -> str:
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
    tts = gTTS(text)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as file:
        tts.save(file.name)
        return file.name