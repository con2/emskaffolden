import re
import os
from contextlib import contextmanager, ExitStack


TEMPLATE_FILENAME_RE = re.compile(r'.in.(?P<extension>yml|yaml)$')
COMPILED_FILENAME_RE = re.compile(r'.compiled.(?P<extension>yml|yaml|json)$')


def get_output_filename(template_filename, output_format):
    if TEMPLATE_FILENAME_RE.search(template_filename):
        return TEMPLATE_FILENAME_RE.sub(f".compiled.{output_format}", template_filename)
    else:
        raise ValueError(f"template filename does not end in .in.yml or in.yaml: {template_filename}")


def get_template_filename(compiled_filename):
    if match := COMPILED_FILENAME_RE.search(compiled_filename):
        extension = match.group("extension")
        extension = "yaml" if extension == "json" else extension
        return COMPILED_FILENAME_RE.sub(f".in.{extension}", compiled_filename)
    else:
        raise ValueError(f"compiled filename does not end in .compiled.yml or compiled.yaml: {compiled_filename}")


@contextmanager
def var_files_if_exist(*filenames):
    filenames = [filename for filename in filenames if os.path.exists(filename)]
    with ExitStack() as stack:
        yield [
            stack.enter_context(open(filename, "r", encoding="UTF-8"))
            for filename in filenames
        ]
