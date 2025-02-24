import time
from audio_processor import recognize_speech, play_sound
from camera_processor import count_people_in_camera, count_people_in_camera_rpi
from utils import match_command
import os


def main():
    while True:
        user_input = recognize_speech()
        command = match_command(user_input)

        if command == "play_sound":
            play_sound()
        elif command == "count_people":
            if os.name == "posix":
                count_people_in_camera_rpi()
            else:
                count_people_in_camera()
        elif command is None:
            print("請再試一次或說得更清楚！")
        time.sleep(1)


if __name__ == "__main__":
    main()