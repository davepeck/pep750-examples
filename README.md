# pep750-examples

This repository contains the code examples found in [PEP 750: Template Strings](https://github.com/davepeck/peps/blob/pep750-post-sprint-update/peps/pep-0750.rst).

## Running this code

This repository contains a [devcontainer](https://containers.dev) definition that makes it easy to run the examples. The devcontainer includes a [fork of cpython 3.14](https://github.com/lysnikolaou/cpython/tree/tag-strings-rebased) that provides a prototype implementation of PEP 750.

It's easy to use:

1. Make sure you have Docker installed
2. Open this repository with `vscode`
3. When asked, say that you want to re-open _inside_ the devcontainer

After the container is initialized, make sure that everything works by opening up a terminal in vscode. This will open in the running docker instance. Then:

```
/workspaces/pep750-examples# python --version
Python 3.14.0a0
```

Congrats; you're good to go!

The container includes `pytest` and a collection of tests to make sure the examples are correct.


## Examples

### f-string behavior

The code in [`fstring.py`](./pep/fstring.py) implements f-string behavior on _top_ of t-strings, showcasing both how to work with the `Template` and `Interpolation` types, and making clear that t-strings are a generalization of f-strings.

See also [the tests](./pep/test_fstring.py).

### Structured logging

IN PROGRESS

### html templating

IN PROGRESS


