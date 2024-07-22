import speech_recognition as sr

recognizer = sr.Recognizer()
microphone = sr.Microphone()

print("Microphone initialized.")
with microphone as source:
    recognizer.adjust_for_ambient_noise(source)
    print("Listening for speech...")
    audio = recognizer.listen(source)
    print("Audio captured.")

try:
    recognized_text = recognizer.recognize_google(audio, language="ja-JP")
    print(f"Recognized: {recognized_text}")
except sr.UnknownValueError:
    print("Google Speech Recognition could not understand audio")
except sr.RequestError as e:
    print(f"Could not request results from Google Speech Recognition service; {e}")

