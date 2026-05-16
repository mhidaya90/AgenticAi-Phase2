import mysql.connector

# Database Connections
CONN = mysql.connector.connect(host="localhost", user='root', password='Pass@123', database="press")
print(CONN)


def ExecuteQuery(conn, query, values):
    ret = {"status": '', "message": "", "record": ""}
    act_msg = ''
    cursor = conn.cursor(dictionary=True)

    try:
        cursor = conn.cursor()
        cursor.execute(query, values)
        conn.commit()  # this will save the record into the table

        ret["status"] = "SUCCESS"
        ret["message"] = f"{cursor.rowcount} Record(s) {act_msg}"
        ret["record"] = ''

    except Exception as e:
        ret["status"] = "EXCEPTION"
        ret["message"] = str(e)
        ret["record"] = ''
        cursor.close()

    finally:
        cursor.close()

    return (ret)

#sample data
hid = 2
headline = "Scientists unveil autonomous underwater robot for deep-sea environmental monitoring"
category = "science & technology"
email = "tech.editor@globalpressnews.com"
score = 3

query = """ INSERT INTO headline_routing_info (hid,headline,category,email,score) VALUES 
            (%s, %s,%s, %s, %s)
        """
values = (hid, headline, category, email, score)
ret = ExecuteQuery(conn=CONN, query=query, values=values)
print(ret)
