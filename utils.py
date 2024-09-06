"""
Utilities for tk-readme-generator
"""

from pathlib import Path


def get_header(info: dict, filepath: Path) -> str:
    """
    Get the header of the readme file with shields.

    Args:
        info: Info data
        filepath: Info filepath

    Returns:
        Readme header
    """
    readme = ""

    # GitHub shields
    git_file = Path(filepath.parent) / ".git" / "config"
    if git_file.is_file():
        with open(git_file, "r") as git_config_file:
            git_config = git_config_file.read()
            if '[remote "origin"]' in git_config:
                lines = git_config.split("\n")
                url = (
                    lines[lines.index('[remote "origin"]') + 1]
                    .replace("url = ", "")
                    .replace(".git", "")
                    .strip()
                )
                if "github" in url:
                    url_segments = url.split("/")
                    repo = f"{url_segments[-2]}/{url_segments[-1]}"
                    readme += f"[![GitHub release (latest by date including pre-releases)](https://img.shields.io/github/v/release/{repo}?include_prereleases)]({url}) \n"
                    readme += f"[![GitHub issues](https://img.shields.io/github/issues/{repo})]({url}/issues) \n"

    # Python project shields
    pyproject = Path(filepath.parent) / "pyproject.toml"
    if pyproject.is_file():
        with open(pyproject, "r") as pyproject_file:
            pyproject_content = pyproject_file.read()
            if (
                'profile = "black"' in pyproject_content
                or "[tool.black]" in pyproject_content
            ):
                readme += "[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)\n"

    if readme != "":
        readme += "\n\n"

    if "display_name" in info:
        readme += f"# {info['display_name']}"
    else:
        readme = f"# {Path(filepath.parent).name}"

    if (Path(filepath.parent) / "icon_256.png").is_file():
        readme += ' <img src="icon_256.png" alt="Icon" height="24"/>'

    readme += "\n\n"

    if "documentation_url" in info:
        readme += f"[![Documentation](https://img.shields.io/badge/documentation-blue?style=for-the-badge)]({info['documentation_url']})\n"
    if "support_url" in info:
        readme += f"[![Support](https://img.shields.io/badge/support-orange?style=for-the-badge)]({info['support_url']})\n"
    if "documentation_url" in info or "support_url" in info:
        readme += "\n"

    if "description" in info:
        readme += f"{info['description']}\n\n"

    if "supported_engines" in info and info["supported_engines"] is not None:
        readme += f"> Supported engines: {', '.join(info['supported_engines'])}\n\n"

    return readme


def get_general_requirements(info: dict) -> str:
    """
    Get the general requirements included in the info file.

    Args:
        info: Info dict

    Returns:
        Table with requirements
    """
    requires_shotgun_version = "-"
    if (
        "requires_shotgun_version" in info
        and info["requires_shotgun_version"] is not None
    ):
        requires_shotgun_version = info["requires_shotgun_version"]

    requires_core_version = "-"
    if "requires_core_version" in info and info["requires_core_version"] is not None:
        requires_core_version = info["requires_core_version"]

    requires_engine_version = "-"
    if (
        "requires_engine_version" in info
        and info["requires_engine_version"] is not None
    ):
        requires_engine_version = info["requires_engine_version"]

    return make_table(
        [
            "ShotGrid version",
            "Core version",
            "Engine version",
        ],
        [
            [
                requires_shotgun_version,
                requires_core_version,
                requires_engine_version,
            ]
        ],
    )


def capitalize(word: str) -> str:
    """
    Capitalize the first letter of a word.

    Args:
        word: String to capitalize

    Returns:
        Capitalized string
    """
    return word[0].upper() + word[1:]


def yaml_to_nested_dict(yaml_data: dict) -> dict:
    """
    Convert dot separated yaml data to nested dicts.

    Args:
        yaml_data:

    Returns:
        Nested dict
    """
    nested_dict = {}
    for key, value in yaml_data.items():
        keys = key.split(".")
        current_dict = nested_dict
        for k in keys[:-1]:
            current_dict = current_dict.setdefault(k, {})
        current_dict[keys[-1]] = value
    return nested_dict


def make_table(cols: list[str], rows: list[list[str]]) -> str:
    """
    Create a Markdown table

    Args:
        cols: Header names
        rows: Rows

    Returns:
        Markdown table string
    """

    def sanitize(content: str) -> str:
        if content is None:
            return ""
        return content.strip().replace("\n", "<br>").replace("|", "\\|")

    sizes = list(map(len, cols))
    for row in rows:
        for i, item in enumerate(row):
            item = sanitize(item)
            if len(item) > sizes[i]:
                sizes[i] = len(item)

    table_md = ""
    for i, col in enumerate(cols):
        content = sanitize(col)
        table_md += f"| {content}{' ' * (sizes[i] - len(content) + 1)}"
    table_md += "|\n"

    for i, col in enumerate(cols):
        table_md += f"|{'-' * (sizes[i] + 2)}"
    table_md += "|\n"

    for row in rows:
        for i, item in enumerate(row):
            content = sanitize(item)
            table_md += f"| {content}{' ' * (sizes[i] - len(content) + 1)}"
        table_md += "|\n"
    return table_md + "\n"
