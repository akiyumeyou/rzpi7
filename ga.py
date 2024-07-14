import os
import json
import subprocess
import asyncio
import pygame
from google.cloud import texttospeech
import sys
import threading
import random
import csv
from datetime import datetime
import speech_recognition as sr

# Google Cloud Text-to-Speech API の初期化
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/home/potz/potzftc/POTZ.json"
client = texttospeech.TextToSpeechClient()

# VOSKのログレベルを抑制
os.environ['VOSK_LOG_LEVEL'] = '0'

# ALSAのエラーメッセージを抑制
os.environ['PYTHONWARNINGS'] = 'ignore:ResourceWarning'
os.environ['PULSE_LOG'] = '0'
os.environ['SDL_AUDIODRIVER'] = 'alsa'

# ALSAのエラーメッセージを非表示にする
stderr_fileno = sys.stderr.fileno()
null_fileno = os.open(os.devnull, os.O_RDWR)
os.dup2(null_fileno, stderr_fileno)

def recognize_speech_from_mic():
    recognizer = sr.Recognizer()
    microphone = sr.Microphone()

    with microphone as source:
        recognizer.adjust_for_ambient_noise(source)
        print("Listening...")
        audio = recognizer.listen(source)

    try:
        recognized_text = recognizer.recognize_google(audio, language="ja-JP")
        print(f"Recognized: {recognized_text}")
    except sr.UnknownValueError:
        print("Google Speech Recognition could not understand audio")
        recognized_text = ""
    except sr.RequestError as e:
        print(f"Could not request results from Google Speech Recognition service; {e}")
        recognized_text = ""

    return recognized_text

async def generate_response(prompt, past_messages=[]):
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
    synthesis_input = texttospeech.SynthesisInput(text=text)

    voice = texttospeech.VoiceSelectionParams(
        language_code="ja-JP",
        name="ja-JP-Standard-C",  # 男性の声
        ssml_gender=texttospeech.SsmlVoiceGender.MALE
    )

    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3
    )

    response = client.synthesize_speech(
        input=synthesis_input, voice=voice, audio_config=audio_config
    )

    filename = "response.mp3"
    with open(filename, "wb") as out:
        out.write(response.audio_content)

    pygame.mixer.init()
    pygame.mixer.music.load(filename)
    pygame.mixer.music.play()

    while pygame.mixer.music.get_busy():
        continue

    os.remove(filename)

def save_conversation_to_csv(conversations):
    now = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"conversation_{now}.csv"
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["User", "AI"])
        writer.writerows(conversations)

async def main():
    past_messages = []
    conversations = []

    initial_message = "こんにちは、お話しできますか？"
    print(initial_message)
    text_to_speech(initial_message)
    conversations.append(("システム", initial_message))

    while True:
        print("Say something:")
        speech = recognize_speech_from_mic()
        print(f"You said: {speech}")
        conversations.append(("ユーザー", speech))

        if "終了" in speech:
            print("Stopping conversation.")
            break
        
        response, past_messages = await generate_response(speech, past_messages)
        print(f"Response: {response}")
        text_to_speech(response)
        conversations.append(("AI", response))

    save_conversation_to_csv(conversations)

if __name__ == "__main__":
    asyncio.run(main())
