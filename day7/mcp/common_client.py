import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import json
 
'''
Step 1: Prepares information about:
Which Python file to run
How to start the MCP server
Nothing runs as of now
'''
 
'''
Step2: First async operation
Python starts the MCP server process
Starts communication pipes as (read,write)
Waits till Server is ready
While waiting, other async tasks can continue
'''
 
'''
Step 3: Create a Session Object over the communication channel
Internally, creates listeners | manage request/response | session state management
'''
 
# Step 4: Initialization Request to the MCP Server
 
# Step 5: Main async call
 
async def call_mcp_tool(server_file: str, tool_name: str, arguments: dict):
    '''
    Step 1: Prepares information about:
    Which Python file to run
    How to start the MCP server
    Nothing runs as of now
    '''
    server_params = StdioServerParameters( command="python", args=[server_file] )
 
    '''
    Step2: First async operation
    Python starts the MCP server process
    Starts communication pipes as (read,write)
    Waits till Server is ready
    While waiting, other async tasks can continue
    '''
    async with stdio_client(server_params) as (read, write):
        # read:     receive data from MCP Server
        # write:    send data to MCP Server
 
        '''
        Step 3: Create a Session Object over the communication channel
        Internally, creates listeners | manage request/response | session state management
        '''
        async with ClientSession(read, write) as session:
            '''
            Step 4: Initialization Request to the MCP Server
            '''
            await session.initialize()
 
            # -----------------------------------------------------------
            # this is not required now. This will only list out the tools
            # -----------------------------------------------------------
            # tools = await session.list_tools()
            # print("Available Tools:")
            # for tool in tools.tools:
            #     print("-", tool.name)
 
            '''
            Step 5: Main async call
            '''
            result = await session.call_tool(tool_name, arguments=arguments)
            return result
 
async def main():
 
    # Ask for input
    print("Menu")
    print("1. Get Stock Price")
    print("2. Get Commodity Price")
    print("3. Get Currency Exchange Rates")
    print("4. Get Geopolitical News of a Country")
    print("5. Quit Application")
 
    choice = 0
    while (choice != 5):
        choice = int(input("Enter choice between 1-4. 5 to Exit/Quit: "))
        if choice == 1:
            ticker = input("Enter Stock Ticker : ")
            if len(ticker.strip()) > 0:
                result = await call_mcp_tool( server_file="financial_server.py",
                                     tool_name="get_bank_financial_info",
                                    arguments={"ticker": ticker} )
                res_type = json.loads(result.content[0].text)
                print(res_type['data'])
        elif choice == 2:
            ticker = input("Enter Commodity Name : ")
            if len(ticker.strip()) > 0:
                result = await call_mcp_tool( server_file="financial_server.py",
                                     tool_name="get_bank_financial_info",
                                    arguments={"ticker": ticker} )
                res_type = json.loads(result.content[0].text)
                print(res_type['data'])
        elif choice == 3:
            from_currency = input("From Currency : ")
            to_currency = input("To Currency : ")
            pair = f"{from_currency.strip()}{to_currency.strip()}=X"
            result =await call_mcp_tool(server_file="financial_server.py",
                                tool_name="get_bank_financial_info",
                                arguments={"ticker": pair})
            res_type = json.loads(result.content[0].text)
            print(res_type['data'])
        elif choice == 4:
            country = input("Country : ")
            result =await call_mcp_tool(server_file="financial_server.py",
                                tool_name="get_geopolitical_news",
                                arguments={"country": country})
            print(result)
 
if __name__ == "__main__":
    asyncio.run(main())
 
# Example
# ticker:
# - HDFCBANK.NS
# - ICICIBANK.NS
# - SBIN.NS
# - JPM
# - BAC
# - MSFT
# - TSLA