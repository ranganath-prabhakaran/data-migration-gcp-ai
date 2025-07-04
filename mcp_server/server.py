import asyncio
import mcp.server.stdio as stdio
from mcp.server.fast_mcp import FastMCPServer
from mcp.server.models import InitializationOptions
import mcp.common.types as types
from mcp_tools import MySQLTools
import yaml

# Load configuration
with open('../config.yaml', 'r') as f:
    config = yaml.safe_load(f)

PROJECT_ID = config['gcp_project_id']

# Initialize the server and tools
server = FastMCPServer("mysql-migration-mcp-server", "1.0.0")
mysql_tools = MySQLTools(project_id=PROJECT_ID)

# --- Define MCP Resources ---
@server.resource("db_metadata")
def get_db_metadata() -> types.ToolResult:
    """Gets metadata of the source database including size, tables, and version."""
    try:
        metadata = mysql_tools.get_db_metadata()
        return types.ToolResult.model(metadata)
    except Exception as e:
        return types.ToolResult.error(str(e))

# --- Define MCP Tools ---
@server.tool()
def get_table_schema(table_name: str) -> types.ToolResult:
    """
    Retrieves the schema for a given table name.
    Args:
        table_name: The name of the table to describe.
    """
    try:
        schema = mysql_tools.get_table_schema(table_name)
        return types.ToolResult.model(schema)
    except Exception as e:
        return types.ToolResult.error(str(e))

@server.tool()
def get_table_row_count(table_name: str) -> types.ToolResult:
    """
    Gets the total row count for a given table name.
    Args:
        table_name: The name of the table.
    """
    try:
        count = mysql_tools.get_table_row_count(table_name)
        return types.ToolResult.model({"table": table_name, "row_count": count})
    except Exception as e:
        return types.ToolResult.error(str(e))

@server.tool()
def run_checksum(table_name: str) -> types.ToolResult:
    """
    Runs a checksum operation on a given table.
    Args:
        table_name: The name of the table.
    """
    try:
        checksum = mysql_tools.run_checksum(table_name)
        return types.ToolResult.model({"table": table_name, "checksum": checksum})
    except Exception as e:
        return types.ToolResult.error(str(e))

@server.tool()
def run_gcs_dump(database_name: str, table_name: str, gcs_bucket: str, gcs_path: str) -> types.ToolResult:
    """
    Dumps a specific table to a Google Cloud Storage bucket.
    Args:
        database_name: The name of the database.
        table_name: The name of the table to dump.
        gcs_bucket: The GCS bucket to upload to.
        gcs_path: The path within the bucket.
    """
    try:
        result = mysql_tools.run_gcs_dump(database_name, table_name, gcs_bucket, gcs_path)
        return types.ToolResult.text(result)
    except Exception as e:
        return types.ToolResult.error(str(e))

@server.tool()
def run_mydumper_export(database_name: str, output_path: str, threads: int = 4, chunk_size_mb: int = 64) -> types.ToolResult:
    """
    Exports the entire database using mydumper for parallel processing.
    Args:
        database_name: The name of the database to export.
        output_path: The local directory path to save the dump files.
        threads: Number of threads for mydumper to use.
        chunk_size_mb: Size of file chunks in MB.
    """
    try:
        result = mysql_tools.run_mydumper_export(database_name, output_path, threads, chunk_size_mb)
        return types.ToolResult.text(result)
    except Exception as e:
        return types.ToolResult.error(str(e))

@server.tool()
def get_binlog_position(metadata_file_path: str) -> types.ToolResult:
    """
    Parses the mydumper metadata file to get the binary log position.
    Args:
        metadata_file_path: The path to the mydumper metadata file.
    """
    try:
        position = mysql_tools.get_binlog_position(metadata_file_path)
        return types.ToolResult.model(position)
    except Exception as e:
        return types.ToolResult.error(str(e))


async def main():
    """Main function to run the MCP server."""
    options = InitializationOptions(
        server_name="mysql-migration-mcp-server",
        server_version="1.0.0",
        capabilities=server.capabilities(),
    )
    async with stdio.stdio_server() as (reader, writer):
        await server.run(reader, writer, options)

if __name__ == "__main__":
    asyncio.run(main())