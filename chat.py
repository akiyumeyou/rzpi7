import speech_recognition as sr
from gtts import gTTS
from pydub import AudioSegment
from pydub.playback import play
import requests
import json
import os

# 音声認識用の初期設定
recognizer = sr.Recognizer()
mic = sr.Microphone()

# サーバーURLの設定
server_url = "https://potzapp.sakura.ne.jp/chat/api/get-ai-response"

def recognize_speech_from_mic(recognizer, microphone):
    """音声をテキストに変換する"""
    with microphone as source:
        recognizer.adjust_for_ambient_noise(source)
        print("話してください...")
        audio = recognizer.listen(source)
    try:
        response = recognizer.recognize_google(audio, language="ja-JP")
        print("認識結果: " + response)
    except sr.RequestError:
        response = "APIにアクセスできません"
    except sr.UnknownValueError:
        response = "音声を認識できませんでした"
    return response

def text_to_speech(text):
    """テキストを音声に変換し、再生する"""
    tts = gTTS(text=text, lang='ja')
    tts.save("response.mp3")
    sound = AudioSegment.from_mp3("response.mp3")
    play(sound)
    os.remove("response.mp3")

def send_text_to_server(text):
    """テキストをサーバーに送信し、AIの応答を受け取る"""
    headers = {
        'Content-Type': 'application/json',
    }
    data = {
        "messages": [
            {"role": "user", "content": text}
        ]
    }
    response = requests.post(server_url, headers=headers, data=json.dumps(data))
    
    try:
        response_json = response.json()
        return response_json.get("message")
    except requests.exceptions.JSONDecodeError as e:
        print("JSONデコードエラー:", e)
        print("レスポンステキスト:", response.text)
        return "エラーが発生しました。サーバーの応答を確認してください。"

def main():
    """メイン処理"""
    print("こんにちは！会話を始めましょう。'終了'と言うと会話が終了します。")
    while True:
        user_input = recognize_speech_from_mic(recognizer, mic)
        print(f"ユーザー: {user_input}")

        if user_input == "終了":
            print("会話を終了しました。")
            text_to_speech("会話を終了しました。")
            break

        if user_input:
            ai_response = send_text_to_server(user_input)
            print(f"AI: {ai_response}")
            text_to_speech(ai_response)

if __name__ == "__main__":
    main()

