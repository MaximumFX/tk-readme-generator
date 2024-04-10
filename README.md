[![Python 3.9](https://img.shields.io/badge/python-3.9-blue.svg)](https://www.python.org/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

# ShotGrid Readme Generator

CLI/GitHub Action README.md generator for ShotGrid frameworks/engines/apps.

## GitHub Action

Add this GitHub Action to a workflow to automatically update the README.md when a change is committed to info.yml.
See an example workflow [here](.github/workflow-templates/update-readme.yml)

## CLI
### Requirements

Requires `pyyaml`

### Usage

`python tk-readme-generator.py <INFO_FILEPATH>`

#### Options

| Argument                        | Description                                                     |
|---------------------------------|-----------------------------------------------------------------|
| -o, --override                  | Override the existing readme.                                   |
| -p FILEPATH, --prepend FILEPATH | Prepend an existing readme file after the name and description. |
| -a FILEPATH, --append FILEPATH  | Append an existing readme file to the end.                      |
