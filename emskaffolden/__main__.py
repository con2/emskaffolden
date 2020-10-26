import os
import sys

from emrichen.cli import get_parser
from emrichen.context import Context
from emrichen.template import Template, determine_format
from emrichen.output import RENDERERS

from .cli import augment_parser
from .files import var_files_if_exist, get_template_filename, get_output_filename
from .skaffold import discover_output_files, invoke_skaffold


def render(context, template_filename, template_format, output_format, output_filename=None):
    if output_filename is None:
        output_filename = get_output_filename(template_filename, output_format)

    with open(template_filename, "r", encoding="UTF-8") as template_file:
        template = Template.parse(template_file, format=template_format)

    output = template.render(context, format=output_format)

    with open(output_filename, "w", encoding="UTF-8") as output_file:
        output_file.write(output)

    return output_filename


def main(args=None):
    if args is None:
        args = sys.argv[1:]

    parser = get_parser(with_pargs=False)
    augment_parser(parser)
    args = parser.parse_args(args)

    override_variables = dict(item.split('=', 1) for item in args.define)

    args.output_format = args.output_format or determine_format(
        getattr(args.output_file, 'name', None), RENDERERS, 'yaml'
    )

    with var_files_if_exist(
        "kubernetes/default.vars.yml",
        "kubernetes/default.vars.yaml",
        f"kubernetes/{args.environment_name}.vars.yml",
        f"kubernetes/{args.environment_name}.vars.yaml",
    ) as default_var_files:
        var_files = default_var_files + list(args.var_files)
        print("Using var files:", file=sys.stderr)
        for var_file in var_files:
            print(f" - {var_file.name}")

        variable_sources = [{ "environment": args.environment_name }] + var_files

        if args.include_env:
            variable_sources.append(os.environ)

        context = Context(*variable_sources, **override_variables)

    print("Compiling Skaffold configuration file:", file=sys.stderr)
    compiled_skaffold_filename = render(context, args.skaffold_file,
        template_format=args.template_format,
        output_format=args.output_format,
    )
    print(f" - {args.skaffold_file} -> {compiled_skaffold_filename}", file=sys.stderr)

    output_filenames = discover_output_files(compiled_skaffold_filename)

    print("Compiling template files:", file=sys.stderr)
    for output_filename in output_filenames:
        template_filename = get_template_filename(output_filename)
        render(context, template_filename,
            template_format=args.template_format,
            output_format=args.output_format,
            output_filename=output_filename,
        )
        print(f" - {template_filename} -> {output_filename}", file=sys.stderr)

    if args.skaffold_args:
        invoke_skaffold(args.skaffold_args, compiled_skaffold_filename)
    else:
        print("No args to Skaffold provided, not invoking Skaffold")

if __name__ == "__main__":
    main()
