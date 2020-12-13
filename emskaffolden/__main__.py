import os
import sys
from pkg_resources import resource_filename

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


def get_builtin_template(*parts):
    return resource_filename(__name__, os.path.join('builtin-templates', *parts))


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

    var_filenames = [
        "kubernetes/default.vars.yml",
        "kubernetes/default.vars.yaml",
        "kubernetes/{args.environment_name}.vars.yml".format(args=args),
        "kubernetes/{args.environment_name}.vars.yaml".format(args=args),
    ]

    if args.builtin_template:
        var_filenames = [
            get_builtin_template(args.builtin_template, "default.vars.yaml")
        ] + var_filenames

    with var_files_if_exist(*var_filenames) as default_var_files:
        var_files = default_var_files + list(args.var_files)
        print("Using var files:", file=sys.stderr)
        for var_file in var_files:
            print(" - {var_file.name}".format(var_file=var_file))

        variable_sources = [{ "environment": args.environment_name }] + var_files

        if args.include_env:
            variable_sources.append(os.environ)

        context = Context(*variable_sources, **override_variables)

    print("Compiling Skaffold configuration file:", file=sys.stderr)
    skaffold_file = (
        get_builtin_template(args.builtin_template, 'skaffold.in.yaml')
        if args.builtin_template and not os.path.exists(args.skaffold_file)
        else args.skaffold_file
    )
    compiled_skaffold_filename = render(context, skaffold_file,
        template_format=args.template_format,
        output_format=args.output_format,
        output_filename='skaffold.compiled.yaml',
    )
    print(" - {skaffold_file} -> {compiled_skaffold_filename}".format(
        skaffold_file=skaffold_file,
        compiled_skaffold_filename=compiled_skaffold_filename,
    ), file=sys.stderr)

    if args.builtin_template:
        output_mapping = {
            'kubernetes/template.compiled.yaml': get_builtin_template(args.builtin_template, 'template.in.yaml')
        }
    else:
        output_mapping = {
            output_filename: get_template_filename(output_filename)
            for output_filename in discover_output_files(compiled_skaffold_filename)
        }

    print("Compiling template files:", file=sys.stderr)

    for output_filename, template_filename in output_mapping.items():
        render(context, template_filename,
            template_format=args.template_format,
            output_format=args.output_format,
            output_filename=output_filename,
        )
        print(" - {template_filename} -> {output_filename}".format(
            template_filename=template_filename,
            output_filename=output_filename,
        ), file=sys.stderr)

    if args.skaffold_args:
        invoke_skaffold(args.skaffold_args, compiled_skaffold_filename)
    else:
        print("No args to Skaffold provided, not invoking Skaffold")

if __name__ == "__main__":
    main()
