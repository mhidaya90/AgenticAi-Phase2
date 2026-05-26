import socket
import csv
import time
import mysql.connector

CSV_FILE = "patients.csv"

def get_patient_from_db(patient_id):
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Pass@123",
        database="medical"
    )
    cursor = conn.cursor()
    print("Patient ID:", patient_id)
    cursor.execute("SELECT * FROM patients WHERE patient_id = %s", (patient_id,))
    result = cursor.fetchone()
    conn.close()
    return result

def check_and_process():
    rows = []
    with open(CSV_FILE, "r") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    updated = False
    messages = []
    for row in rows:
        if row["status"].lower() == "new":
            patient_id = row["patient_id"]
            patient_data = get_patient_from_db(patient_id)
            messages.append(f"Processed patient {patient_id}: {patient_data}")
            row["status"] = "Processed"
            updated = True

    if updated:
        with open(CSV_FILE, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=rows[0].keys())
            writer.writeheader()
            writer.writerows(rows)

    return "\n".join(messages) if messages else "No new patients."

def run_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(("localhost", 65432))
    server_socket.listen(5)
    print("MCP Server running on port 65432...")

    while True:
        client_socket, addr = server_socket.accept()
        print(f"Connection from {addr}")
        request = client_socket.recv(1024).decode()

        if request == "check":
            response = check_and_process()
        else:
            response = "Unknown command"

        client_socket.send(response.encode())
        client_socket.close()

if __name__ == "__main__":
    run_server()
