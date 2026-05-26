import socket
import time

def send_request(command="check"):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(("localhost", 65432))
    client_socket.send(command.encode())
    response = client_socket.recv(4096).decode()
    client_socket.close()
    return response

if __name__ == "__main__":
    while True:
        print("Sending request to MCP server...")
        result = send_request("check")
        print("Server response:")
        print(result)
        print("Waiting 5 minutes before next check...\n")
        time.sleep(300)  # 300 seconds = 5 minutes
