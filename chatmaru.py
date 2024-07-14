import speech_recognition as sr
from gtts import gTTS
import pygame
import os
import subprocess
import json

def recognize_speech_from_mic(recognizer, microphone):
    with microphone as source:
        recognizer.adjust_for_ambient_noise(source)
        print("Listening...")
        audio = recognizer.listen(source)
        
    try:
        response = recognizer.recognize_google(audio, language='ja-JP')
    except sr.RequestError:
        response = "API unavailable"
    except sr.UnknownValueError:
        response = "Unable to recognize speech"
    
    return response

def generate_response(prompt, past_messages=[]):
    result = subprocess.run(
        ['node', 'api.js', prompt, json.dumps(past_messages)],
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        raise Exception(f"Node.js script error: {result.stderr}")

    response_data = json.loads(result.stdout)
    return response_data['responseMessage'], response_data['pastMessages']

def text_to_speech(text):
    tts = gTTS(text=text, lang='ja')
    filename = "response.mp3"
    tts.save(filename)

    pygame.mixer.init()
    pygame.mixer.music.load(filename)
    pygame.mixer.music.play()

    while pygame.mixer.music.get_busy():
        continue

    os.remove(filename)

def main():
    recognizer = sr.Recognizer()
    microphone = sr.Microphone()
    past_messages = []

    while True:
        print("Say something:")
        speech = recognize_speech_from_mic(recognizer, microphone)
        print(f"You said: {speech}")

        if "???" in speech:
            print("Stopping conversation.")
            break
        
        response, past_messages = generate_response(speech, past_messages)
        print(f"Response: {response}")
        text_to_speech(response)

if __name__ == "__main__":
    main()
