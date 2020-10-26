# Emskaffolden = Emrichen + Skaffold

[Emrichen](https://github.com/con2/emrichen) is a template engine that takes in templates written in YAML or JSON, processes tags that do things like variable substitution, and outputs YAML or JSON. Emrichen is especially powerful for templating Kubernetes manifests.

[Skaffold](https://skaffold.dev/) is a developer tool that handles the workflow for building, pushing and deploying your application, allowing you to focus on what matters most: writing code. Skaffold is especially good at three things: doing everyday development with Kubernetes, providing a coherent way to do image tagging in CI and watching for Kubernetes deployments to complete in CD.

**Emskaffolden** combines Emrichen and Skaffold by compiling the Skaffold config file and Kubernetes templates with Emrichen and then invoking Skaffold.

Emskaffolden is opinionated: it may not suit everyone's workflow. If you find Emskaffolden's way of working unsuitable for your needs, you can try to make your case in the issues, but we try to keep the core very small.

### Why wrap Skaffold instead of implementing Emrichen support for Skaffold?

1. Emrichen is a relatively unknown templating tool, so they'd probably never accept a PR integrating Emrichen into Skaffold.
2. This way we can support any of the Skaffold deploy methods using Emrichen, not just `kubectl`. You can even go wild and generate Kustomize or even Helm YAML using Emrichen! Err, not sure why you'd want to. But you can.

## Installation

Install [Skaffold](https://skaffold.dev/docs/install/) and [Python 3.6+](https://wiki.python.org/moin/BeginnersGuide/Download). Then install `emskaffolden` using Pip:

    python3 -m pip install emskaffolden

## Usage

When you invoke `emskaffolden` (or the shorthand `emsk`), it does the following steps:

1. Compiles `skaffold.in.yaml` to `skaffold.compiled.yaml` (change with `-F`)
2. Reads `skaffold.compiled.yaml`, discovers all `*.compiled.yaml` files referenced there, locates a corresponding `*.in.yaml` template and compiles it to `*.compiled.yaml`
3. Invokes Skaffold with `-f skaffold.compiled.yaml` and any other parameters you passed to the Emskaffolden command line after `--`.

### Use `--` to separate Emrichen and Skaffold options

As a general rule, options before `--` go to Emrichen and options after `--` go to `skaffold`. The Skaffold subcommand (or basically any _positional_ arguments) can go on either side of `--`.

So eg. these two are interchangeable:

    emskaffolden run -f kubernetes/staging.vars.yaml -- --default-repo=harbor.con2.fi/con2
    emskaffolden -f kubernetes/staging.vars.yaml -- run --default-repo=harbor.con2.fi/con2

are interchangeable and both tell Emrichen to use the `kubernetes/staging.vars.yaml` var file, and invokes Skaffold with `run -f skaffold.compiled.yaml --default-repo=harbor.con2.fi/con2`.

On the other hand, if you were to leave out the `--`, Emskaffolden would complain about `--default-repo`, which is understood by Skaffold but not Emrichen/Emskaffolden.

Tip: You can use the short form `emsk` for all commands instead of `emskaffolden`.

### Default and environment-specific var files

A `kubernetes/default.vars.yaml` var file is loaded from if present.

Environment-specific files are loaded from `kubernetes/` if present. The default environment is called `development`, corresponding to `kubernetes/development.vars.yaml`, and the environment can be switched with `-E <env name>`.

If your environment specific var files are elsewhere, use `-f path/to/foo.vars.yaml` instead.

### Workflow

There is no `emskaffolden init`. Just copy over files from `example/` and edit them to your liking. For a real-world example, see [Kompassi](https://github.com/tracon/kompassi) or [Edegal](https://github.com/con2/edegal).

Use `emskaffolden dev` as your everyday development environment – either locally using Docker Desktop, or in the Kubernetes environment of your choice.

Use `emskaffolden run` in your CI/CD pipeline, or split it into `emskaffolden build -- --output-file=build.json` and `emskaffolden deploy -- -a build.json`.

`*.compiled.yaml` files should not be committed into Git. The `.gitignore` in `example/` excludes them.

## License

    The MIT License (MIT)

    Copyright © 2020 Santtu Pajukanta

    Permission is hereby granted, free of charge, to any person obtaining a copy
    of this software and associated documentation files (the "Software"), to deal
    in the Software without restriction, including without limitation the rights
    to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
    copies of the Software, and to permit persons to whom the Software is
    furnished to do so, subject to the following conditions:

    The above copyright notice and this permission notice shall be included in
    all copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
    OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
    THE SOFTWARE.
