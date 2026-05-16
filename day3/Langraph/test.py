import os
import pandas as pd
from typing import TypedDict, List
from langgraph.graph import StateGraph, END
import mysql.connector
from dotenv import load_dotenv

load_dotenv()

# Database Connections
host = os.getenv("MS_HOST")
port = os.getenv("MS_PORT")
user = os.getenv("MS_USER")
pwd = os.getenv("MS_PASSWORD")
db = "medical"

print(f"Connecting as user {user} to {host}:{port}/{db}:{pwd}")
CONN = None
CURSOR = None


def ConnectDB():
    try:
        ret = {"status": "", "message": ""}

        global CONN

        CONN = mysql.connector.connect(
            host=host, user=user, password=pwd, database=db)

        ret["status"] = "SUCCESS"
        ret["message"] = "Connected to MySQL"

    except Exception as e:
        ret["status"] = "EXCEPTION"
        ret["message"] = str(e)

    return (ret)

ConnectDB()


# State definition
class PatientState(TypedDict):
    query: str
    values: str
    response: list[dict]  # this should be a list[dict] for conversion


# Run a query in the database
def ExecuteQuery(action, query, values=None):
    ret = {"status": '', "message": "", "record": ""}
    act_msg = ''
    CURSOR = CONN.cursor(dictionary=True,buffered=True)

    try:
        if action == "I":
            act_msg = "Inserted"
        elif action == "U":
            act_msg = "Updated"
        elif action == "D":
            act_msg = "Deleted"
        elif action == "S":
            act_msg = "Retrieved"

        if action in ["I", "U", "D"]:
            CURSOR.execute(query, values)
        else:
            CURSOR.execute(query)

        if action == "S":  # select query
            if values:
                CURSOR.execute(query, values)  # ✅ pass values here
            else:
                data = CURSOR.fetchall()
                ret["status"] = "SUCCESS"
                ret["message"] = f"{len(data)} Record(s) {act_msg} "
                ret["record"] = pd.DataFrame(data)

        elif action in ["I", "U", "D"]:
            CONN.commit()

            if CURSOR.rowcount == 0:
                ret["status"] = "ERROR"
                ret["message"] = "No matching record found"
                ret["record"] = ""
            else:
                ret["status"] = "SUCCESS"
                ret["message"] = f"{CURSOR.rowcount} Record(s) {act_msg}"
                ret["record"] = ''

    except Exception as e:
        ret["status"] = "EXCEPTION"
        ret["message"] = str(e)
        ret["record"] = ''
        CURSOR.close()

    finally:
        CURSOR.close()

    return (ret)

#Agents creation
def agent_selectpatient(state: PatientState) -> PatientState:
    try:
        query = state["query"]
        values = state["values"]
        ret = ExecuteQuery("S", query, values)
        # df = ret["record"]
        # df_dict = df.to_dict(orient="records")
        if isinstance(ret["record"], pd.DataFrame):
            df_dict = ret["record"].to_dict(orient="records")
        else:
            # Return status/message if no DataFrame
            df_dict = [{"status": ret["status"], "msg": ret["message"]}]

    except Exception as e:
        df_dict = {"status": "Exception", "msg": str(e)}

    return ({**state, "query": query, "response": df_dict})

#=================
def agent_updatepatient(state: PatientState) -> PatientState:
    try:
        query = state["query"]
        values = state["values"]
        ret = ExecuteQuery("U", query, values)
        print(ret)
        df_dict = {"status": ret["status"], "msg": ret["message"]}

    except Exception as e:
        df_dict = {"status": "Exception", "msg": str(e)}

    return {**state, "query": query,"values":values,"response": [df_dict]}

def buildgraph():
    graph = StateGraph(PatientState)

    graph.add_node("updatequery", agent_updatepatient)
    graph.add_node("selectquery", agent_selectpatient)

    graph.set_entry_point("updatequery")

    graph.add_edge("updatequery", "selectquery")
    graph.add_edge("selectquery", END)

    graph = graph.compile()
    return (graph)

graph = buildgraph()


#Update Query
query_update = "UPDATE patients SET present_complaint = %s WHERE patient_id = %s;"
values_update = ("Typhoid", "PT0001")

query_select = "select present_complaint from patients where patient_id =\"PT0001\";"

if graph:
    update_result = graph.invoke({"query": query_update, "values": values_update, "response": [{}]})
    select_result = graph.invoke({"query": query_select, "values": None, "response": [{}]})

df = pd.DataFrame(select_result['response'])
print(df)

print(select_result)

# visualise the graph
png_data = graph.get_graph().draw_mermaid_png()

with open("multi_agent.png", "wb") as f:
    f.write(png_data)



