from autogen_agentchat.agents import AssistantAgent

def create_environment_setup_agent(model_client, code_executor):
    """Creates the Environment Setup Agent."""
    system_message = """
You are an Environment Setup Specialist. Your primary role is to verify the readiness of the GCP environment.
Execute shell commands to confirm that the target Cloud SQL instance is running, the designated GCS bucket exists, and that you have the necessary permissions to access secrets in Secret Manager.
Report the status of each check. Do not proceed if any check fails.
Conclude your response with the word 'TERMINATE' after reporting the status.
"""
    env_setup_agent = AssistantAgent(
        name="Environment_Setup_Agent",
        system_message=system_message,
        model_client=model_client,
        code_execution_config={"executor": code_executor},
    )
    return env_setup_agent