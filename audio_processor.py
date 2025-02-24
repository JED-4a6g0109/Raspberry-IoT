import time

import speech_recognition as sr
from pygame import mixer
import os
from datetime import datetime
from pydub import AudioSegment
import io

mixer.init()

DATA_DIR = "data"
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)


def play_sound():
    file_path = 'music.mp3'
    if os.path.exists(file_path):
        mixer.music.load(file_path)
        mixer.music.play()
        print("正在播放聲音...")
        while mixer.music.get_busy():
            time.sleep(1)
    else:
        print(f"錯誤：'{file_path}' 不存在")


def recognize_speech(mock_data=None):
    recognizer = sr.Recognizer()
    timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
    audio_file = os.path.join(DATA_DIR, f"{timestamp}_recorded_audio.wav")
    text_file = os.path.join(DATA_DIR, f"{timestamp}_speech_text.txt")

    if mock_data:
        audio_file_path = os.path.join(mock_data)
        try:
            with sr.AudioFile(audio_file_path) as source:
                print(f"從文件 '{audio_file_path}' 讀取音頻...")
                audio = recognizer.record(source)
        except Exception as e:
            print(f"無法處理音頻文件：{e}")
            return None
    else:
        with sr.Microphone() as source:
            print("請開始說話（錄音 5 秒）...")
            recognizer.adjust_for_ambient_noise(source, duration=1)
            audio = recognizer.listen(source, timeout=None, phrase_time_limit=5)

        try:
            wav_data = audio.get_wav_data()
            audio_segment = AudioSegment.from_wav(io.BytesIO(wav_data))
            louder_audio = audio_segment + 50
            louder_audio.export(audio_file, format="wav")
            print(f"語音已保存為 '{audio_file}'，大小：{os.path.getsize(audio_file) / 1024:.2f} KB")
        except Exception as e:
            print(f"保存語音檔失敗：{e}")
            return None

    try:
        text = recognizer.recognize_google(audio, language='zh-TW')
        print(f"你說了：{text}")
        with open(text_file, "w", encoding="utf-8") as f:
            f.write(text)
        print(f"文字已保存為 '{text_file}'")
        return text
    except sr.UnknownValueError:
        print("無法識別語音")
        with open(text_file, "w", encoding="utf-8") as f:
            f.write("無法識別語音")
        return None
    except sr.RequestError as e:
        print(f"語音服務錯誤：{e}")
        with open(text_file, "w", encoding="utf-8") as f:
            f.write("語音服務不可用")
        return None
