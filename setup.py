from setuptools import find_packages, setup

PACKAGE_NAME = "unify_integration"

setup(
    name=PACKAGE_NAME,
    version="0.1.11",
    description="The Unify tool package gives access to a single sign on client with multiple LLM endpoints and their metadata",  # noqa: E501
    packages=find_packages(),
    extras_require={"dev": ["requests_mock", "python_dotenv"], "build": ["promptflow", "unifyai"]},
    entry_points={
        "package_tools": ["unify_llm = unify_llm_tool.tools.utils:list_package_tools"],
    },
    include_package_data=True,  # This line tells setuptools to include files from MANIFEST.in
)
