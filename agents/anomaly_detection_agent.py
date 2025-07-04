from autogen_agentchat.agents import AssistantAgent

def create_anomaly_detection_agent(model_client):
    """Creates the Anomaly Detection Agent."""
    system_message = """
You are a Security and Performance Anomaly Detector. You will be provided with the complete execution logs from the migration process.
Your task is to parse these logs and identify any anomalies.
Look for patterns such as an excessive number of connection errors, unusually long query execution times, repeated failed attempts to dump a specific table, or any security warnings.
Report any identified anomalies with the corresponding log excerpts for further investigation.
Conclude your response with the word 'TERMINATE' after generating the report.
"""
    anomaly_detection_agent = AssistantAgent(
        name="Anomaly_Detection_Agent",
        system_message=system_message,
        model_client=model_client,
    )
    return anomaly_detection_agent