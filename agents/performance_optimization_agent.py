from autogen_agentchat.agents import AssistantAgent

def create_performance_optimization_agent(model_client, code_executor):
    """Creates the Performance Optimization Agent."""
    system_message = """
You are a GCP Cost and Performance Optimization Expert. You will receive the final migration report and logs.
Based on the total migration time, the resources consumed, and the final configuration of the target Cloud SQL instance, provide a set of actionable recommendations for optimizing the production environment.
Your suggestions should cover right-sizing the Cloud SQL machine type, evaluating the use of SSD vs. HDD storage, recommending an appropriate automated backup schedule, and proposing a suitable High Availability (HA) configuration based on standard business continuity requirements.
Use the code executor to run `gcloud` commands to get the current configuration of the resources if needed.
Conclude your response with the word 'TERMINATE' after providing the recommendations.
"""
    performance_optimization_agent = AssistantAgent(
        name="Performance_Optimization_Agent",
        system_message=system_message,
        model_client=model_client,
        code_execution_config={"executor": code_executor},
    )
    return performance_optimization_agent