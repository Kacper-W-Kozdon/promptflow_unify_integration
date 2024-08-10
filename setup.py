from setuptools import find_packages, setup

PACKAGE_NAME = "unify_integration"

setup(
    name=PACKAGE_NAME,
    version="0.0.1",
    description="This is my tools package",
    packages=find_packages(),
    entry_points={
        "package_tools": ["unify_llm_tool = unify_integration.unify_llm_tool.tools.utils:list_package_tools"],
    },
    include_package_data=True,  # This line tells setuptools to include files from MANIFEST.in
)
