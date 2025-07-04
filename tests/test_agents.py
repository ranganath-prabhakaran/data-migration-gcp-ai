import pytest
from unittest.mock import MagicMock
from agents.environment_setup_agent import create_environment_setup_agent
from agents.schema_conversion_agent import create_schema_conversion_agent
from agents.data_migration_agent import create_data_migration_agent
from agents.data_validation_agent import create_data_validation_agent
from agents.anomaly_detection_agent import create_anomaly_detection_agent
from agents.performance_optimization_agent import create_performance_optimization_agent

@pytest.fixture
def mock_model_client():
    """Fixture for a mock model client."""
    return MagicMock()

@pytest.fixture
def mock_code_executor():
    """Fixture for a mock code executor."""
    return MagicMock()

def test_create_environment_setup_agent(mock_model_client, mock_code_executor):
    agent = create_environment_setup_agent(mock_model_client, mock_code_executor)
    assert agent.name == "Environment_Setup_Agent"
    assert "verify the readiness of the GCP environment" in agent.system_message

def test_create_schema_conversion_agent(mock_model_client):
    agent = create_schema_conversion_agent(mock_model_client)
    assert agent.name == "Schema_Conversion_Agent"
    assert "Analyze the collected schemas for any potential incompatibilities" in agent.system_message

def test_create_data_migration_agent(mock_model_client, mock_code_executor):
    agent = create_data_migration_agent(mock_model_client, mock_code_executor)
    assert agent.name == "Data_Migration_Agent"
    assert "select one of the three migration strategies" in agent.system_message

def test_create_data_validation_agent(mock_model_client, mock_code_executor):
    agent = create_data_validation_agent(mock_model_client, mock_code_executor)
    assert agent.name == "Data_Validation_Agent"
    assert "ensure perfect data integrity after migration" in agent.system_message

def test_create_anomaly_detection_agent(mock_model_client):
    agent = create_anomaly_detection_agent(mock_model_client)
    assert agent.name == "Anomaly_Detection_Agent"
    assert "parse these logs and identify any anomalies" in agent.system_message

def test_create_performance_optimization_agent(mock_model_client, mock_code_executor):
    agent = create_performance_optimization_agent(mock_model_client, mock_code_executor)
    assert agent.name == "Performance_Optimization_Agent"
    assert "provide a set of actionable recommendations for optimizing" in agent.system_message