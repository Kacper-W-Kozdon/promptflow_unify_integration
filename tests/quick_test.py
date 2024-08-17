import importlib
import importlib.metadata


def test() -> None:
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
            except:  # noqa: E722
                print("An error occurred with:\n")
                print(f"----{identifier}\n{tool}")


if __name__ == "__main__":
    test()
