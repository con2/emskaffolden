def augment_parser(parser):
    """
    Takes the Emrichen argument parser and makes an Emskaffolden argument
    parser out of it.
    """
    parser.add_argument(
        '--environment-name',
        '-E',
        default="development",
        help=(
            'Name of the environment. Exported as a var called "environment". Also if a '
            'var file called kubernetes/<ENV NAME>.vars.yaml exists, it is included as a var file. '
            'If your environment specific var files are elsewhere, use -f instead.'
        ),
    )

    parser.add_argument(
        '--skaffold-file',
        '-F',
        type=str,
        default='skaffold.in.yaml',
        help="Skaffold configuration file template",
    )

    parser.add_argument(
        'skaffold_args',
        nargs='*',
        type=str,
        help='Arguments to Skaffold',
    )
