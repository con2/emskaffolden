import os
import sys
from collections.abc import Sequence, Mapping

import yaml

from .files import COMPILED_FILENAME_RE


def discover_output_files(compiled_skaffold_filename):
    stack = []
    found = []

    print(f"Discovering output files from {compiled_skaffold_filename}:", file=sys.stderr)

    with open(compiled_skaffold_filename, "r", encoding="UTF-8") as config_file:
        stack.extend(yaml.safe_load_all(config_file))

    while stack:
        current = stack.pop()

        if isinstance(current, str):
            if COMPILED_FILENAME_RE.search(current):
                print(f" - {current}", file=sys.stderr)
                found.append(current)
        elif isinstance(current, Mapping):
            stack.extend(current.values())
        elif isinstance(current, Sequence):
            stack.extend(current)

    return found


def invoke_skaffold(skaffold_args, skaffold_config_file):
    skaffold_args = ["skaffold", "-f", skaffold_config_file] + skaffold_args

    print("Invoking skaffold with:", skaffold_args, file=sys.stderr)
    print("", file=sys.stderr)

    os.execvp("skaffold", skaffold_args)
