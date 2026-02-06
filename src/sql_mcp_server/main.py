from fastmcp import FastMCP

from sql_mcp_server.tools.query import run_select
from sql_mcp_server.tools.schema import describe_table, list_tables

mcp = FastMCP("sql-mcp-server")

mcp.tool()(list_tables)
mcp.tool()(describe_table)
mcp.tool()(run_select)


def run() -> None:
    mcp.run()


if __name__ == "__main__":
    run()
