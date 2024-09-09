import os
import pytest
import requests
import requests_mock
from collections import OrderedDict
from unittest.mock import patch, MagicMock
from dotenv import load_dotenv
from unify_llm_tool.tools.benchmark_llm_tool import benchmark_models, get_benchmarks
from unify_llm_tool.tools.optimize_llm_tool import optimize_llm
from unify_llm_tool.tools.single_sign_on_tool import single_sign_on, UnifyConnection

load_dotenv()



# Mock the API key for the tests
@pytest.fixture
def mock_api_key(monkeypatch):
    monkeypatch.setenv("UNIFY_API_KEY", "fake-api-key")
    monkeypatch.setenv("UNIFY_KEY", "fake-unify-key")



# Test for benchmark_llm_tool.py
def test_get_benchmarks(mock_api_key, requests_mock):
    url = "https://api.unify.ai/v0/benchmarks"
    mock_response = [{"model": "gpt-4", "provider": "openai"}]
    requests_mock.get(url, json=mock_response)

    endpoints = ["gpt-4@openai"]
    result = get_benchmarks(endpoints, api_key=os.getenv("UNIFY_API_KEY"))

    assert isinstance(result, OrderedDict)
    assert result["gpt-4@openai"] == mock_response



def test_benchmark_models(mock_api_key, requests_mock):
    url = "https://api.unify.ai/v0/endpoints"
    mock_response_endpoints = ["gpt-4@openai"]
    requests_mock.get(url, json=mock_response_endpoints)

    url_benchmarks = "https://api.unify.ai/v0/benchmarks?model=gpt-4&provider=openai"
    mock_response_benchmarks = {"model": "gpt-4", "provider": "openai"}
    requests_mock.get(url_benchmarks, json=mock_response_benchmarks)

    result = benchmark_models(models=["gpt-4"], providers=["openai"])

    assert isinstance(result, OrderedDict)
    assert "gpt-4@openai" in result

# Test for optimize_llm_tool.py
def test_optimize_llm(mock_api_key):
    mock_connection = MagicMock()
    mock_connection.get_credit_balance.return_value = 100.0
    mock_connection.generate.return_value = "Generated text"

    config = {
        "quality": "1",
        "cost": "4.65e-03",
        "time_to_first_token": "2.08e-05",
        "inter_token_latency": "2.07e-03",
        "model": "gpt-4",
        "provider": "openai",
    }



    result = optimize_llm(connection=mock_connection, config=config, input_text="Test input")

    assert isinstance(result, dict)
    assert "optimal_endpoint" in result
    assert result["response"] == "Generated text"



# Test for single_sign_on_tool.py
@patch("unify_llm_tool.tools.single_sign_on_tool.pf.connections.create_or_update", autospec=True)
@patch("unify_llm_tool.tools.single_sign_on_tool.UnifyConnection", autospec=True)
def test_single_sign_on(MockUnifyConnection, MockCreateUpdate, mock_api_key):
    mock_connection_instance = MockUnifyConnection.return_value
    mock_connection_instance.endpoint = "gpt-4@openai"

    result = single_sign_on(endpoint="gpt-4@openai", model=None, provider=None, unify_api_key="fake-api-key")

    MockCreateUpdate.assert_called_once()
    assert isinstance(result, UnifyConnection)  
    assert result.endpoint == "gpt-4@openai"



# Test for single_sign_on_tool.py 
@patch("unify_llm_tool.tools.single_sign_on_tool.pf.connections.create_or_update", autospec=True)
@patch("unify_llm_tool.tools.single_sign_on_tool.UnifyConnection", autospec=True)
def test_single_sign_on_with_model_provider(MockUnifyConnection, MockCreateUpdate, mock_api_key):
    mock_connection_instance = MockUnifyConnection.return_value
    mock_connection_instance.endpoint = "gpt-4@openai"

    result = single_sign_on(endpoint=None, model="gpt-4", provider="openai", unify_api_key="fake-api-key")

    MockCreateUpdate.assert_called_once()
    assert isinstance(result, UnifyConnection) 
    assert result.endpoint == "gpt-4@openai"


#