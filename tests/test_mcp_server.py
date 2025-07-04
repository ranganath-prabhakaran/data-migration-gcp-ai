import pytest
from unittest.mock import MagicMock, patch
from mcp_server.mcp_tools import MySQLTools

@pytest.fixture
def mock_mysql_tools():
    """Fixture to create a mocked instance of MySQLTools."""
    with patch('mcp_server.mcp_tools.pymysql.connect') as mock_connect:
        # Mock the connection and cursor
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value.__enter__.return_value = mock_conn
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        
        # Setup mock return values for different queries
        def cursor_execute_effect(query):
            if "information_schema.TABLES" in query:
                mock_cursor.fetchone.return_value = {'db_size_gb': 50.0}
            elif "SHOW TABLES" in query:
                mock_cursor.fetchall.return_value = "SHOW TABLES"
            elif "VERSION()" in query:
                mock_cursor.fetchone.return_value = {'VERSION()': '8.0.32'}
            elif "DESCRIBE" in query:
                mock_cursor.fetchall.return_value = "DESCRIBE"
            elif "COUNT(*)" in query:
                mock_cursor.fetchone.return_value = {'count': 300024}
        
        mock_cursor.execute.side_effect = cursor_execute_effect
        
        tools = MySQLTools(project_id="test-project")
        # Mock secret manager as well
        tools.secret_manager.get_secret = MagicMock(return_value="test_value")
        yield tools

def test_get_db_metadata(mock_mysql_tools):
    """Test the get_db_metadata tool."""
    metadata = mock_mysql_tools.get_db_metadata()
    assert metadata['db_size_gb'] == 50.0
    assert 'employees' in metadata['tables']
    assert metadata['mysql_version'] == '8.0.32'

def test_get_table_schema(mock_mysql_tools):
    """Test the get_table_schema tool."""
    schema = mock_mysql_tools.get_table_schema("employees")
    assert isinstance(schema, list)
    assert schema['Field'] == 'emp_no'

def test_get_table_row_count(mock_mysql_tools):
    """Test the get_table_row_count tool."""
    count = mock_mysql_tools.get_table_row_count("employees")
    assert count == 300024

def test_invalid_table_name_raises_error(mock_mysql_tools):
    """Test that invalid characters in table name raise a ValueError."""
    with pytest.raises(ValueError):
        mock_mysql_tools.get_table_schema("employees; DROP TABLE users;")