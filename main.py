import asyncio
import yaml
import argparse
from autogen_agentchat.agents import UserProxyAgent, CodeExecutorAgent
from autogen_agentchat.teams import DiGraphBuilder
from autogen_agentchat.conditions import MaxMessageTermination
from autogen_ext.models.openai import OpenAIChatCompletionClient # Using as a placeholder for Gemini client structure
from google.cloud import secretmanager

# Import agent creation functions
from agents.environment_setup_agent import create_environment_setup_agent
from agents.schema_conversion_agent import create_schema_conversion_agent
from agents.data_migration_agent import create_data_migration_agent
from agents.data_validation_agent import create_data_validation_agent
from agents.anomaly_detection_agent import create_anomaly_detection_agent
from agents.performance_optimization_agent import create_performance_optimization_agent

def get_secret(project_id, secret_id):
    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/{project_id}/secrets/{secret_id}/versions/latest"
    response = client.access_secret_version(request={"name": name})
    return response.payload.data.decode("UTF-8")

async def main(task, encryption_method):
    with open('config.yaml', 'r') as f:
        config = yaml.safe_load(f)

    # Fetch API key from Secret Manager
    api_key = get_secret(config['gcp_project_id'], config['llm_config']['api_key_secret_name'])

    # In a real scenario, you would use a Gemini client. We use OpenAI client structure for compatibility demo.
    model_client = OpenAIChatCompletionClient(model=config['llm_config']['model'], api_key=api_key)
    
    # Create a code executor in a docker environment
    code_executor = CodeExecutorAgent(
        "code_executor",
        code_executor=autogen.coding.DockerCommandLineCodeExecutor(work_dir="coding")
    )

    # Create Agents
    env_agent = create_environment_setup_agent(model_client, code_executor)
    schema_agent = create_schema_conversion_agent(model_client)
    migration_agent = create_data_migration_agent(model_client, code_executor)
    validation_agent = create_data_validation_agent(model_client, code_executor)
    anomaly_agent = create_anomaly_detection_agent(model_client)
    optimization_agent = create_performance_optimization_agent(model_client, code_executor)

    # User Proxy Agent to kick off the process
    user_proxy = UserProxyAgent(name="User_Proxy")

    # Build the GraphFlow
    builder = DiGraphBuilder()
    builder.add_node(user_proxy)
    builder.add_node(env_agent)
    builder.add_node(schema_agent)
    builder.add_node(migration_agent)
    builder.add_node(validation_agent)
    builder.add_node(anomaly_agent)
    builder.add_node(optimization_agent)

    # Define the workflow sequence
    builder.add_edge(user_proxy, env_agent)
    builder.add_edge(env_agent, schema_agent)
    builder.add_edge(schema_agent, migration_agent)
    builder.add_edge(migration_agent, validation_agent)
    builder.add_edge(validation_agent, anomaly_agent)
    builder.add_edge(anomaly_agent, optimization_agent)

    graph = builder.build()
    team = autogen_agentchat.teams.GraphFlow(
        participants=graph.nodes,
        graph=graph,
        termination_condition=MaxMessageTermination(15)
    )

    # Formulate the initial task message
    initial_task = f"""
    Start the MySQL migration process.
    Task: {task}
    Encryption Preference: {encryption_method}
    Follow the defined workflow precisely.
    """
    
    # Run the team
    await user_proxy.run_team(team, task=initial_task)
    
    await model_client.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--task", type=str, required=True, help="The migration task description.")
    parser.add_argument("--encryption-method", type=str, choices=['gcp-default', 'legacy'], default='gcp-default', help="Encryption method preference.")
    args = parser.parse_args()
    
    asyncio.run(main(args.task, args.encryption_method))