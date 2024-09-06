"""
Readme generator for ShotGrid frameworks/engines/apps
"""

from pathlib import Path

import yaml

import utils


def generate_general_readme(
    filepath: Path, prepend: str = None, append: str = None
) -> str:
    """
    Generate a readme file for a ShotGrid framework/engine/app

    Args:
        filepath: File path to info.yml
        prepend: File path to Markdown file to prepend in Readme
        append: File path to Markdown file to append in Readme

    Returns:
        Markdown readme
    """
    with open(str(filepath), "r") as file:
        info = yaml.safe_load(file)

    readme = ""

    readme += utils.get_header(info, filepath)

    # Prepend readme file
    if prepend is not None and prepend != "":
        prepend_filepath = Path(prepend)
        if prepend_filepath.is_file():
            with open(prepend_filepath, "r") as prepend_file:
                readme += prepend_file.read()
                readme += "\n\n"

    readme += "## Requirements\n\n"

    readme += utils.get_general_requirements(info)

    if (
        "requires_shotgun_fields" in info
        and info["requires_shotgun_fields"] is not None
    ):
        readme += "### ShotGrid fields:\n\n"
        for key, value in info["requires_shotgun_fields"].items():
            readme += f"**{key}:**\n"
            for field in value:
                readme += f"- {field['system_name']} `{field['type']}`\n"
        readme += "\n"

    if "frameworks" in info and info["frameworks"] is not None:
        readme += "**Frameworks:**\n\n"
        readme += utils.make_table(
            ["Name", "Version", "Minimum version"],
            list(
                map(
                    lambda framework: [
                        framework["name"],
                        framework["version"],
                        framework.get("minimum_version", ""),
                    ],
                    info["frameworks"],
                )
            ),
        )
        readme += "\n\n"

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
        "tank_type": "Tank types",
    }
    if "configuration" in info and info["configuration"] is not None:
        readme += "## Configuration\n\n"

        config = {}
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
                            item.get("description", ""),
                            item.get("default_value", ""),
                            item.get("fields", ""),
                        ],
                        value,
                    )
                )
            else:
                rows = list(
                    map(
                        lambda item: [
                            f"`{item['name']}`",
                            item.get("description", ""),
                            f'{item.get("default_value", "")}',
                        ],
                        value,
                    )
                )
            readme += utils.make_table(cols, rows)
            readme += "\n"

    # Append readme file
    if append is not None and append != "":
        append_filepath = Path(append)
        if append_filepath.is_file():
            with open(append_filepath, "r") as append_file:
                readme += "\n\n"
                readme += append_file.read()

    return readme
