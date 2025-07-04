from autogen_agentchat.agents import AssistantAgent

def create_data_validation_agent(model_client, code_executor):
    """Creates the Data Validation Agent."""
    system_message = """
You are a Data Validation Auditor. Your mission is to ensure perfect data integrity after migration.
For every table identified by the Schema Agent, you will perform two checks.
First, use the `get_table_row_count` tool on the source (via MCP) and run a script to get the row count on the target (via code executor) and compare the results.
Second, use the `run_checksum` tool on the source (via MCP) and run a script to get the checksum on the target (via code executor) and compare the checksums.
Compile a detailed validation report, clearly marking each table as 'VALIDATED' or 'MISMATCH' with the corresponding values.
Conclude your response with the word 'TERMINATE' after generating the report.
"""
    data_validation_agent = AssistantAgent(
        name="Data_Validation_Agent",
        system_message=system_message,
        model_client=model_client,
        code_execution_config={"executor": code_executor},
    )
    return data_validation_agent