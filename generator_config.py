"""
Readme generator for ShotGrid configurations
"""

import subprocess
from pathlib import Path

import semver
import yaml

import utils


def _get_include(base_filepath: Path, filename: str, info_key: str) -> str:
    """
    Get the information for an env/include file.

    Args:
        base_filepath: Filepath to info.yml
        filename: Filename to look for
        info_key: Key to use for info in file

    Returns:
        Include section with version status table
    """
    filepath = base_filepath.parent / "env" / "includes" / f"{filename}.yml"

    if not filepath.is_file():
        return ""

    with open(str(filepath), "r") as file:
        info = yaml.safe_load(file)

    if info is None:
        return ""

    info = utils.yaml_to_nested_dict(info)[info_key]

    items = []
    rows = []

    for key, value in info.items():
        item = {**value["location"], "key": key}

        if item["type"] == "app_store":
            item["repo"] = f"ShotGunSoftware/{item['name']}"
        elif item["type"] == "github_release":
            item["repo"] = f"{item['organization']}/{item['repository']}"
        else:
            continue

        print(
            f"[{utils.capitalize(info_key)}] Getting latest version for {item['repo']}..."
        )

        repo_url = f"https://github.com/{item['repo']}.git"
        output_lines = subprocess.check_output(
            [
                "git",
                "ls-remote",
                "--tags",
                "--refs",
                "--sort=version:refname",
                repo_url,
            ],
            encoding="utf-8",
        ).splitlines()
        latest_version = output_lines[-1].rpartition("/")[-1]

        source_version = None

        if item["type"] == "github_release":
            try:
                source_lines = subprocess.check_output(
                    [
                        "git",
                        "ls-remote",
                        "--tags",
                        "--refs",
                        "--sort=version:refname",
                        f"https://github.com/ShotGunSoftware/{item['repository']}.git",
                    ],
                    encoding="utf-8",
                ).splitlines()
                source_version = source_lines[-1].rpartition("/")[-1]
            except:
                pass

        item["latest"] = latest_version
        if source_version is not None:
            compare_version = source_version
        else:
            compare_version = latest_version
        version = item["version"]

        if version.startswith("v"):
            version = version[1:]
        if compare_version.startswith("v"):
            compare_version = compare_version[1:]

        version_count = version.count(".")
        compare_count = compare_version.count(".")
        if version_count != compare_count:
            if version_count > 2:
                parts = version.split(".")
                version = ".".join(parts[0:3])

            if compare_count > 2:
                parts = compare_version.split(".")
                compare_version = ".".join(parts[0:3])
        else:
            if version_count > 2:
                parts = version.split(".")
                version = ".".join(parts[-3:])

                parts = compare_version.split(".")
                compare_version = ".".join(parts[-3:])

        try:
            item["compared"] = semver.compare(version, compare_version)
        except:
            item["compared"] = None

        items.append(item)

        color = "blue"
        if item["compared"] == -1:
            if source_version is None:
                color = "red"
            else:
                color = "orange"
        if item["compared"] == 1:
            color = "green"

        if source_version is None:
            rows.append(
                [
                    item["key"],
                    f"![{item['version']}](https://img.shields.io/badge/{item['version']}-{color})",
                    "",
                    f"[![{item['repo']}](https://img.shields.io/github/v/tag/{item['repo']})](https://github.com/{item['repo']})",
                ]
            )
        else:
            rows.append(
                [
                    item["key"],
                    f"![{item['version']}](https://img.shields.io/badge/{item['version']}-{color})",
                    f"[![{item['repo']}](https://img.shields.io/github/v/tag/{item['repo']})](https://github.com/{item['repo']})",
                    f"[![ShotGunSoftware/{item['repository']}](https://img.shields.io/github/v/tag/ShotGunSoftware/{item['repository']})](https://github.com/ShotGunSoftware/{item['repository']})",
                ]
            )

    title = utils.capitalize(info_key)

    return f"## {title}\n\n" + utils.make_table(
        ["Name", "Current", "Fork", "Latest"], rows
    )


def generate_config_readme(
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

    print("Getting framework info...")
    readme += _get_include(filepath, "frameworks", "frameworks")
    readme += "\n\n"
    print("Getting engine info...")
    readme += _get_include(filepath, "engine_locations", "engines")
    readme += "\n\n"
    print("Getting app info...")
    readme += _get_include(filepath, "app_locations", "apps")

    # Append readme file
    if append is not None and append != "":
        append_filepath = Path(append)
        if append_filepath.is_file():
            with open(append_filepath, "r") as append_file:
                readme += "\n\n"
                readme += append_file.read()

    return readme
