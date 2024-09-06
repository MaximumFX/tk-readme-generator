"""
Readme generator for ShotGrid configurations, apps, frameworks and engines.
"""

import argparse
from enum import Enum
from pathlib import Path

import yaml

from generator_config import generate_config_readme
from generator_general import generate_general_readme


class Mode(Enum):
    general = "general"
    config = "config"

    def __str__(self):
        return self.value


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
parser.add_argument(
    "-m",
    "--mode",
    type=Mode,
    choices=list(Mode),
    help="Make a readme for a general info file (framework/engine/app) or a config info file.",
)

args = parser.parse_args()


def generate_readme(
    file: str,
    mode: Mode = None,
    override: bool = False,
    prepend: str = None,
    append: str = None,
):
    """
    Generate a readme from an info.yml file.

    Args:
        file: File path to info.yml
        mode: Readme type to create
        override: Override existing README.md (Default is `False`)
        prepend: File path to Markdown file to prepend in Readme
        append: File path to Markdown file to append in Readme
    """

    filepath = Path(file)
    if not filepath.is_file():
        msg = "The file couldn't be found."
        raise Exception(msg)

    with open(file, "r") as file:
        info = yaml.safe_load(file)

    if info is None:
        msg = "The file couldn't be parsed."
        raise Exception(msg)

    # Decide mode if not provided
    if mode is None:
        includes_filepath = filepath.parent / "env" / "includes"
        if includes_filepath.is_dir():
            mode = Mode.config
        else:
            mode = Mode.general

    # Generate readme
    if mode == Mode.general:
        readme = generate_general_readme(filepath, prepend, append)
    else:
        readme = generate_config_readme(
            filepath,
        )

    output_file = Path(filepath.parent) / "README.md"
    if output_file.is_file() and not override:
        output_file = Path(filepath.parent) / "README_GENERATED.md"

    with open(output_file, "w") as text_file:
        text_file.write(readme)


generate_readme(args.file, args.mode, args.override, args.prepend, args.append)
