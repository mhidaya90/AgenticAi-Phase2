# import asyncio, json, time
# from mcp import ClientSession, StdioServerParameters
# from mcp.client.stdio import stdio_client
#
# async def call_mcp_tool(server_file: str, tool_name: str, arguments: dict):
#     server_params = StdioServerParameters(command="python", args=[server_file])
#     async with stdio_client(server_params) as (read, write):
#         async with ClientSession(read, write) as session:
#             await session.initialize()
#             result = await session.call_tool(tool_name, arguments=arguments)
#             return result
#
# async def main():
#     choice = 0
#     while choice != 3:
#         print("Menu")
#         print("1. Check and Process CSV")
#         print("2. Get Patient Status")
#         print("3. Quit Application")
#         choice = int(input("Enter choice: "))
#         if choice == 1:
#             # result = await call_mcp_tool(
#             #     server_file="patient_server.py",
#             #     tool_name="check_and_process",
#             #     arguments={}
#             # )
#             # print("Raw result:", result.content)
#             # res_type = json.loads(result.content[0].text)
#             # print(json.dumps(res_type, indent=2))
#             print("Starting auto-check every 5 minutes...")
#             while True:
#                 result = await call_mcp_tool(
#                     server_file="patients_server.py",
#                     tool_name="check_and_process",
#                     arguments={}
#                 )
#                 if result.content and result.content[0].text:
#                     try:
#                         res_type = json.loads(result.content[0].text)
#                         print("Processed:", json.dumps(res_type, indent=2))
#                     except json.JSONDecodeError:
#                         print("Invalid JSON:", result.content[0].text)
#                 else:
#                     print("Empty response from server:", result)
#
#                 print("Waiting 5 minutes before next check...\n")
#                 await asyncio.sleep(300)
#         elif choice == 2:
#             patient_id = input("Enter Patient ID: ")
#             result = await call_mcp_tool(
#                 server_file="patient_server.py",
#                 tool_name="get_patient_status",
#                 arguments={"patient_id": patient_id}
#             )
#             res_type = json.loads(result.content[0].text)
#             print(json.dumps(res_type, indent=2))
#
# if __name__ == "__main__":
#     asyncio.run(main())
import asyncio
import json
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def main():
    # Start the MCP server process once
    server_params = StdioServerParameters(command="python", args=["patient_server.py"])

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            print("Menu")
            print("1. Auto-check CSV every 5 minutes")
            print("2. Get Patient Status")
            print("3. Quit Application")

            choice = 0
            while choice != 3:
                choice = int(input("Enter choice: "))
                if choice == 1:
                    print("Starting auto-check every 5 minutes... Press Ctrl+C to stop.")
                    try:
                        while True:
                            result = await session.call_tool("check_and_process", arguments={})
                            if result.content and result.content[0].text:
                                try:
                                    res_type = json.loads(result.content[0].text)
                                    print("Processed:", json.dumps(res_type, indent=2))
                                except json.JSONDecodeError:
                                    print("Invalid JSON:", result.content[0].text)
                            else:
                                print("Empty response:", result)

                            await asyncio.sleep(60)
                    except KeyboardInterrupt:
                        print("Stopped auto-check loop.")

                elif choice == 2:
                    patient_id = input("Enter Patient ID: ")
                    result = await session.call_tool("get_patient_status", arguments={"patient_id": patient_id})
                    if result.content and result.content[0].text:
                        try:
                            res_type = json.loads(result.content[0].text)
                            print(json.dumps(res_type, indent=2))
                        except json.JSONDecodeError:
                            print("Invalid JSON:", result.content[0].text)
                    else:
                        print("Empty response:", result)

if __name__ == "__main__":
    asyncio.run(main())
