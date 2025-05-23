#  Copyright (c) ZenML GmbH 2020. All Rights Reserved.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at:
#
#       https://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
#  or implied. See the License for the specific language governing
#  permissions and limitations under the License.

import json
from pathlib import Path
from typing import Any, Dict
from uuid import UUID

import yaml

import zenml.io.utils
from zenml.io import fileio


def write_yaml(file_path: str, contents: Dict[Any, Any]) -> None:
    """Write contents as YAML format to file_path.

    Args:
        file_path: Path to YAML file.
        contents: Contents of YAML file as dict.

    Raises:
        FileNotFoundError: if directory does not exist.
    """
    if not fileio.is_remote(file_path):
        dir_ = str(Path(file_path).parent)
        if not fileio.is_dir(dir_):
            raise FileNotFoundError(f"Directory {dir_} does not exist.")
    zenml.io.utils.write_file_contents_as_string(file_path, yaml.dump(contents))


def append_yaml(file_path: str, contents: Dict[Any, Any]) -> None:
    """Append contents to a YAML file at file_path."""
    file_contents = read_yaml(file_path) or {}
    file_contents.update(contents)
    if not fileio.is_remote(file_path):
        dir_ = str(Path(file_path).parent)
        if not fileio.is_dir(dir_):
            raise FileNotFoundError(f"Directory {dir_} does not exist.")
    zenml.io.utils.write_file_contents_as_string(
        file_path, yaml.dump(file_contents)
    )


def read_yaml(file_path: str) -> Any:
    """Read YAML on file path and returns contents as dict.

    Args:
        file_path: Path to YAML file.

    Returns:
        Contents of the file in a dict.

    Raises:
        FileNotFoundError: if file does not exist.
    """
    if fileio.file_exists(file_path):
        contents = zenml.io.utils.read_file_contents_as_string(file_path)
        # TODO: [LOW] consider adding a default empty dict to be returned
        # instead of None
        return yaml.safe_load(contents)
    else:
        raise FileNotFoundError(f"{file_path} does not exist.")


def is_yaml(file_path: str) -> bool:
    """Returns True if file_path is YAML, else False

    Args:
        file_path: Path to YAML file.

    Returns:
        True if is yaml, else False.
    """
    if file_path.endswith("yaml") or file_path.endswith("yml"):
        return True
    return False


def write_json(file_path: str, contents: Dict[str, Any]) -> None:
    """Write contents as JSON format to file_path.

    Args:
        file_path: Path to JSON file.
        contents: Contents of JSON file as dict.

    Returns:
        Contents of the file in a dict.

    Raises:
        FileNotFoundError: if directory does not exist.
    """
    if not fileio.is_remote(file_path):
        dir_ = str(Path(file_path).parent)
        if not fileio.is_dir(dir_):
            # If it is a local path and it doesn't exist, raise Exception.
            raise FileNotFoundError(f"Directory {dir_} does not exist.")
    zenml.io.utils.write_file_contents_as_string(
        file_path, json.dumps(contents)
    )


def read_json(file_path: str) -> Any:
    """Read JSON on file path and returns contents as dict.

    Args:
        file_path: Path to JSON file.
    """
    if fileio.file_exists(file_path):
        contents = zenml.io.utils.read_file_contents_as_string(file_path)
        return json.loads(contents)
    else:
        raise FileNotFoundError(f"{file_path} does not exist.")


class UUIDEncoder(json.JSONEncoder):
    def default(self, obj: Any) -> Any:
        if isinstance(obj, UUID):
            # if the obj is uuid, we simply return the value of uuid
            return obj.hex
        return json.JSONEncoder.default(self, obj)
