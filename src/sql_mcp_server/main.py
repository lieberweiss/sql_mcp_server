from fastmcp import FastMCP

from sql_mcp_server.tools.query import run_query, run_select
from sql_mcp_server.tools.schema import describe_table, list_tables

mcp = FastMCP("sql-mcp-server")

mcp.tool()(list_tables)
mcp.tool()(describe_table)
mcp.tool()(run_select)
mcp.tool()(run_query)


def run() -> None:
    mcp.run()


if __name__ == "__main__":
    run()
