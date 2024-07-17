import speech_recognition as sr
from TTS.api import TTS
import soundfile as sf
import pygame
import os
import subprocess
import json

# グローバル変数としてTTSオブジェクトをロード
tts = TTS(model_name="tts_models/ja/kokoro/tacotron2-DDC")

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
        ['node', 'ap.js', prompt, json.dumps(past_messages)],
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        raise Exception(f"Node.js script error: {result.stderr}")

    response_data = json.loads(result.stdout)
    return response_data['responseMessage'], response_data['pastMessages']

def text_to_speech(text):
    tts.tts_to_file(text=text, file_path="response.wav")

    pygame.mixer.init()
    pygame.mixer.music.load("response.wav")
    pygame.mixer.music.play()

    while pygame.mixer.music.get_busy():
        continue

    os.remove("response.wav")

def main():
    recognizer = sr.Recognizer()
    microphone = sr.Microphone()
    past_messages = []

    # 最初の呼びかけ
    initial_message = "こんにちは、お話しできますか？"
    print(initial_message)
    text_to_speech(initial_message)

    while True:
        print("Say something:")
        speech = recognize_speech_from_mic(recognizer, microphone)
        print(f"You said: {speech}")

        if "終了" in speech:  # Assuming "終了" (Shūryō) means to end the conversation
            print("Stopping conversation.")
            break
        
        response, past_messages = generate_response(speech, past_messages)
        print(f"Response: {response}")
        text_to_speech(response)

if __name__ == "__main__":
    main()
