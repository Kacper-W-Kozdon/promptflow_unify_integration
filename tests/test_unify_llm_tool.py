import importlib
import importlib.metadata
import os
import unittest
from collections import OrderedDict
from typing import Union

import pytest
from dotenv import load_dotenv
from unify import Unify

from promptflow.client import PFClient
from promptflow.connections import CustomConnection
from unify_llm_tool.tools.benchmark_llm_tool import benchmark_models
from unify_llm_tool.tools.optimize_llm_tool import optimize_llm
from unify_llm_tool.tools.single_sign_on_tool import UnifyConnection, create_strong_unify_connection

pf = PFClient()


load_dotenv()
unify_api_key = os.getenv("UNIFY_KEY")


@pytest.fixture
def custom_connection() -> Union[Unify, UnifyConnection, CustomConnection]:
    custom_connection = UnifyConnection(secrets={"api_key": unify_api_key})
    return custom_connection


class TestTool:
    """
    The test class for the Unify integration
    """

    def test_optimize_llm(self, custom_connection) -> None:
        """
        The method to test optimize_llm_tool
        """
        result = optimize_llm(custom_connection, config={}, input_text="Microsoft")
        assert isinstance(result, (tuple, dict))

    def test_benchmark_llm(self) -> None:
        """
        The method to test the benchmar_llm_tool
        """
        models: Union[list, None] = "gpt-4o"
        providers: Union[list, None] = None
        result: Union[OrderedDict, object] = benchmark_models(
            models=models,
            providers=providers,
        )
        assert isinstance(result, dict)

    def test_unify_connection(custom_connection) -> None:  # noqa: E0211
        """
        Tests if the strong type connections is created.
        """
        assert create_strong_unify_connection() is not None
        print(f"---CONNECTION NAME---\n{UnifyConnection._Connection_configs['name']}")
        connections: list = [connection.name for connection in pf.connections.list()]
        print(f"---CONNECTIONS---\n{connections}")
        assert UnifyConnection._Connection_configs["name"] in connections  # noqa: W0212

    def test_installation(custom_connection) -> None:  # noqa: E0211
        """List all package tools information using the `package-tools` entry point.

        This function iterates through all entry points registered under the group "package_tools."
        For each tool, it imports the associated module to ensure its validity and then prints
        information about the tool.

        Note:
        - Make sure your package is correctly packed to appear in the list.
        - The module is imported to validate its presence and correctness.

        Example of tool information printed:
        ----identifier
        {'module': 'module_name', 'package': 'package_name', 'package_version': 'package_version', ...}
        """
        PACKAGE_TOOLS_ENTRY = "package_tools"
        entry_points = importlib.metadata.entry_points()
        if hasattr(entry_points, "select"):
            entry_points = entry_points.select(group=PACKAGE_TOOLS_ENTRY)
        else:
            entry_points = entry_points.get(PACKAGE_TOOLS_ENTRY, [])
        for entry_point in entry_points:
            list_tool_func = entry_point.load()
            package_tools = list_tool_func()

            for identifier, tool in package_tools.items():
                try:
                    importlib.import_module(tool["module"])  # Import the module to ensure its validity
                    print(f"----{identifier}\n{tool}")
                except Exception as e:  # noqa: E722
                    print("An error occurred with:\n")
                    print(f"----{identifier}\n{tool}")
                    print(f"---Error---\n{e}")
                    break


# Run the unit tests
if __name__ == "__main__":
    unittest.main()
