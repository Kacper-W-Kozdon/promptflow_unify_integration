import os
import unittest
from typing import Union

import pytest
from dotenv import load_dotenv
from unify import Unify

from promptflow.connections import CustomConnection
from unify_integration.unify_llm_tool.tools.evaluate_llm_tool import benchmark_models
from unify_integration.unify_llm_tool.tools.optimize_llm_tool import optimize_llm

load_dotenv()
unify_api_key = os.getenv("UNIFY_KEY")


@pytest.fixture
def my_custom_connection() -> Union[Unify, CustomConnection]:
    my_custom_connection = Unify(api_key=unify_api_key)
    return my_custom_connection


class TestTool:
    def test_optimize_llm(self, my_custom_connection):
        result = optimize_llm(my_custom_connection, config={}, input_text="Microsoft")
        assert isinstance(result, tuple)

    def test_evaluate_llms(self, my_custom_connection):
        models = []
        prompt_set = []
        result = benchmark_models(models=models, prompt_set=prompt_set)
        assert isinstance(result, dict)


# Run the unit tests
if __name__ == "__main__":
    unittest.main()
