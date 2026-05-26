import json
from mcp.server.fastmcp import FastMCP
import mysql.connector, csv, os
from dotenv import load_dotenv


load_dotenv()
CSV_FILE = "patients.csv"
mcp = FastMCP("PatientServer")
MS_HOST=os.getenv("MS_HOST")
MS_PORT=os.getenv("MS_PORT")
MS_USER=os.getenv("MS_USER")
MS_PASSWORD=os.getenv("MS_PASSWORD")
MS_DATABASE = os.getenv("MS_DBNAME")

def get_patient_from_db(patient_id: str):
    try:
        conn = mysql.connector.connect(host=MS_HOST, port=MS_PORT, database=MS_DATABASE, user=MS_USER, password=MS_PASSWORD)
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM patients WHERE patient_id = %s", (patient_id,))
        result = cursor.fetchone()
        conn.close()
    except Exception as e:
        result = str(e)
    return result

@mcp.tool()
def check_and_process() -> str:
    if not os.path.exists(CSV_FILE):
        return json.dumps({"error": f"CSV file {CSV_FILE} not found"})

    with open(CSV_FILE, "r") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    processed = []
    for row in rows:
        if row["status"].lower() == "new":
            patient_id = row["patient_id"].strip()
            patient_data = get_patient_from_db(patient_id)
            processed.append({"patient_id": patient_id, "data": patient_data})
            row["status"] = "Processed"

    if processed:
        with open(CSV_FILE, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=rows[0].keys())
            writer.writeheader()
            writer.writerows(rows)

    return json.dumps({"processed": processed, "count": len(processed)}, default=str)

@mcp.tool()
def get_patient_status(patient_id: str) -> str:
    data = get_patient_from_db(patient_id)
    return json.dumps({"patient_id": patient_id, "data": data}, default=str)

if __name__ == "__main__":
    mcp.run(transport="stdio")
