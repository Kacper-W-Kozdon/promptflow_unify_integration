import os
import unittest
from collections import OrderedDict
from typing import Union

import pytest
from dotenv import load_dotenv
from unify import Unify
from unify_llm_tool.tools.benchmark_llm_tool import benchmark_models
from unify_llm_tool.tools.optimize_llm_tool import optimize_llm

from promptflow.connections import CustomConnection

load_dotenv()
unify_api_key = os.getenv("UNIFY_KEY")


@pytest.fixture
def my_custom_connection() -> Union[Unify, CustomConnection]:
    custom_connection = Unify(api_key=unify_api_key)
    return custom_connection


class TestTool:
    """
    The test class for the Unify integration
    """

    def test_optimize_llm(self, custom_connection: Unify) -> None:
        """
        The method to test optimize_llm_tool
        """
        result = optimize_llm(custom_connection, config={}, input_text="Microsoft")
        assert isinstance(result, tuple)

    def test_benchmark_llm(self) -> None:
        """
        The method to test the benchmar_llm_tool
        """
        models: list = []
        providers: list = []
        result: Union[OrderedDict, object] = benchmark_models(
            models=models,
            providers=providers,
        )
        assert isinstance(result, dict)


# Run the unit tests
if __name__ == "__main__":
    unittest.main()
