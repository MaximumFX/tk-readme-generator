import argparse
from pathlib import Path
import yaml


def table(cols: list[str], rows: list[list[str]]) -> str:
    sizes = list(map(len, cols))
    for row in rows:
        for i, item in enumerate(row):
            if len(item) > sizes[i]:
                sizes[i] = len(item)

    table_md = ""
    for i, col in enumerate(cols):
        table_md += f"| {col}{' ' * (sizes[i] - len(col) + 1)}"
    table_md += "|\n"

    for i, col in enumerate(cols):
        table_md += f"|{'-' * (sizes[i] + 2)}"
    table_md += "|\n"

    for row in rows:
        for i, item in enumerate(row):
            table_md += f"| {item}{' ' * (sizes[i] - len(item) + 1)}"
        table_md += "|\n"
    return table_md + "\n"


parser = argparse.ArgumentParser(
    prog="tk-readme-generator",
    description="Generate a README file from a info.yml file",
)

parser.add_argument("file", help="The info file to use.")
parser.add_argument(
    "-o", "--override", action="store_true", help="Override the existing readme."
)
parser.add_argument(
    "-p",
    "--prepend",
    metavar="FILEPATH",
    help="Prepend an existing readme file after the name and description.",
)
parser.add_argument(
    "-a",
    "--append",
    metavar="FILEPATH",
    help="Append an existing readme file to the end.",
)

args = parser.parse_args()


filepath = Path(args.file)
if not filepath.is_file():
    msg = "The file couldn't be found."
    raise Exception(msg)

with open(args.file, "r") as file:
    info = yaml.safe_load(file)

if info is None:
    msg = "The file couldn't be parsed."
    raise Exception(msg)

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
    if "documentation_url" in info:
        readme += "\n"

if "description" in info:
    readme += f"{info['description']}\n\n"

# Prepend readme file
if args.prepend is not None and args.prepend != "":
    prepend_filepath = Path(args.prepend)
    if prepend_filepath.is_file():
        with open(prepend_filepath, "r") as prepend_file:
            readme += prepend_file.read()
            readme += "\n\n"

if "supported_engines" in info and info["supported_engines"] is not None:
    readme += f"> Supported engines: {', '.join(info['supported_engines'])}\n\n"

readme += "## Requirements\n\n"

requires_shotgun_version = "-"
if "requires_shotgun_version" in info and info["requires_shotgun_version"] is not None:
    requires_shotgun_version = info["requires_shotgun_version"]

requires_core_version = "-"
if "requires_core_version" in info and info["requires_core_version"] is not None:
    requires_core_version = info["requires_core_version"]

requires_engine_version = "-"
if "requires_engine_version" in info and info["requires_engine_version"] is not None:
    requires_engine_version = info["requires_engine_version"]

readme += table(
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

requires_shotgun_fields = "-"
if "requires_shotgun_fields" in info and info["requires_shotgun_fields"] is not None:
    requires_shotgun_fields = info["requires_shotgun_fields"]
readme += f"**ShotGrid fields:** {requires_shotgun_fields}\n\n"

frameworks = "-"
if "frameworks" in info and info["frameworks"] is not None:
    frameworks = ", ".join(info["frameworks"])
readme += f"**Frameworks:** {frameworks}\n\n"

config_names = {
    "str": "Strings",
    "int": "Integers",
    "bool": "Booleans",
    "dict": "Dictionaries",
    "list": "Lists",
    "config_path": "Config paths",
    "template": "Templates",
    "publish_type": "Publish types",
    "hook": "Hooks",
    "shotgun_entity_type": "ShotGrid entity types",
    "shotgun_permission_group": "ShotGrid permission groups",
    "shotgun_filter": "ShotGrid filters",
}
if "configuration" in info and info["configuration"] is not None:
    readme += "## Configuration\n\n"

    config = {}
    configuration = info["configuration"]
    for key, value in info["configuration"].items():
        config_item = {**value, "name": key}

        if "default_value" not in config_item:
            config_item["default_value"] = ""

        if value["type"] not in config:
            config[value["type"]] = [config_item]
        else:
            config[value["type"]] += [config_item]

    for key, value in config.items():
        name = key
        if key in config_names:
            name = config_names[key]
        readme += f"### {name}\n\n"

        cols = ["Name", "Description", "Default value"]
        if key == "template":
            cols.append("Fields")
            rows = list(
                map(
                    lambda item: [
                        f"`{item['name']}`",
                        item["description"],
                        item["default_value"],
                        item["fields"],
                    ],
                    value,
                )
            )
        else:
            rows = list(
                map(
                    lambda item: [
                        f"`{item['name']}`",
                        item["description"],
                        f'{item["default_value"]}',
                    ],
                    value,
                )
            )
        readme += table(cols, rows)
        readme += "\n"

# Append readme file
if args.append is not None and args.append != "":
    append_filepath = Path(args.append)
    if append_filepath.is_file():
        with open(append_filepath, "r") as append_file:
            readme += "\n\n"
            readme += append_file.read()


output_file = Path(filepath.parent) / "README.md"
if output_file.is_file() and not args.override:
    output_file = Path(filepath.parent) / "README_GENERATED.md"

with open(output_file, "w") as text_file:
    text_file.write(readme)
