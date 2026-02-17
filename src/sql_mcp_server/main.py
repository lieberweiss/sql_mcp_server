import logging

from fastmcp import FastMCP

from sql_mcp_server.logging_utils import setup_logging
from sql_mcp_server.tools.query import run_query, run_select
from sql_mcp_server.tools.schema import describe_table, list_tables

setup_logging()
logger = logging.getLogger("sql_mcp_server")

mcp = FastMCP("sql-mcp-server")

mcp.tool()(list_tables)
mcp.tool()(describe_table)
mcp.tool()(run_select)
mcp.tool()(run_query)


def run() -> None:
    logger.info("sql-mcp-server starting on stdio transport")
    try:
        mcp.run(transport="stdio")
        logger.info("sql-mcp-server stopped")
    except BaseException:
        logger.exception("sql-mcp-server crashed")
        raise


if __name__ == "__main__":
    run()
