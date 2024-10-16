# pep750-examples

This repository contains the code examples found in [PEP 750: Template Strings](https://peps.python.org/pep-0750/).

The repository includes a suite of tests to make sure the examples are correct.

## Running This Code

This repo has a [devcontainer](https://containers.dev) definition that makes it easy to run the examples. The devcontainer includes a [fork of cpython 3.14](https://github.com/lysnikolaou/cpython/tree/tag-strings-rebased) that provides a prototype implementation of PEP 750.

It's easy to run this code yourself:

1. Make sure you have Docker installed
2. Clone this repository and open it with `vscode`
3. When asked, say that you want to re-open _inside_ the devcontainer

After the container is initialized, make sure that everything works by opening up a terminal in vscode. This will open in the running docker instance. Then:

```
/workspaces/pep750-examples# python --version
Python 3.14.0a0
/workspaces/pep750-examples# pytest
... (hopefully, all tests pass!) ...
```

Congrats; you're good to go!


## A Word About the Code

The current `cpython` implementation that this repository builds on top of tracks an _older_ version of PEP 750 with somewhat different syntax and semantics than the fully up-to-date PEP.

Luckily, we can "smooth over" the important differences in a handful of lines of Python code. That's what's in the [`pep/__init__.py`](./pep/__init__.py) file.

When PEP 750 lands in cpython, you'll be able to simply write a template string with a `t` prefix: `t"This is a template string"`. However, in this example code, because of the divergence between our `cpython` implementation and PEP 750, you first need to `from pep import t` in order to use the `t"Hello, World"` syntax.

Likewise, when PEP 750 lands, you'll be able to `from types import Template, Interpolation`. Right now, those types are _also_ defined in the `pep` module.

If you're just reading the example code and tests, you probably won't have to think about this. We'll update this repository when an updated version of `cpython` is available.

## Examples

### Implementing f-string Behavior

The code in [`fstring.py`](./pep/fstring.py) implements f-string behavior on _top_ of t-strings, showcasing both how to work with the `Template` and `Interpolation` types, and making clear that t-strings are a generalization of f-strings:

```python
name = "World"
value = 42.0
templated = t"Hello {name!r}, value: {value:.2f}"
formatted = f"Hello {name!r}, value: {value:.2f}"
assert f(templated) == formatted
```
See also [the tests](./pep/test_fstring.py).

This [example is described in detail](https://peps.python.org/pep-0750/#example-implementing-f-strings-with-t-strings) in PEP 750.

### Structured Logging

The code in [`logging.py`](./pep/logging.py) implements two separate approaches to structured logging, showcasing how a single `logger.info(t"...")` call can lead to emitting both human-readable _and_ structured (in this case, JSON-formatted) data.

The first approach follows the approach already found in the [Python Logging Cookbook](https://docs.python.org/3/howto/logging-cookbook.html#implementing-structured-logging); the second approach defines custom `Formatter`s that can be used to emit human-readable and structured output to different streams:

```python
import logging
import sys

logger = logging.getLogger(__name__)
message_handler = logging.StreamHandler(sys.stdout)
message_handler.setFormatter(MessageFormatter())
logger.addHandler(handler)

values_handler = logging.StreamHandler(sys.stderr)
values_handler.setFormatter(ValuesFormatter())
logger.addHandler(values_handler)

action, amount, item = "traded", 42, "shrubs"
logger.info(t"User {action}: {amount:.2f} {item}")

# Outputs to sys.stdout:
# User traded: 42.00 shrubs

# At the same time, outputs to sys.stderr:
# {"action": "traded", "amount": 42, "item": "shrubs"}
```

See the tests in [`test_logging.py`](./pep/test_logging.py).

This [example is described in detail](https://peps.python.org/pep-0750/#example-structured-logging) in PEP 750.

### HTML Templating

There are several short "HTML templating" examples in [PEP 750](https://peps.python.org/pep-0750/).

They all use a hypothetical `html()` function that parses template strings to an intermediate type, `Element`, and supports context-dependent processing of interpolations.

A real working implementation of `html()` is found in this repository's [`web.py`](./pep/web.py). Corresponding tests are found in [`test_web.py`](./pep/test_web.py).

Building a full robust HTML templating package on top of template strings is both a noble goal _and_ beyond the scope of this example code. Instead, our goal is to hint at some interesting uses of template strings in the HTML context, and to provide an early roadmap (warts and all) for how a more robust package might be built.

The `Element` class is a simple representation of an HTML element:

```python

from dataclasses import dataclass

@dataclass(frozen=True)
class Element:
    """A simple representation of an HTML element."""

    tag: str  # An empty string indicates a fragment
    attributes: Mapping[str, str | bool]
    children: Sequence[Element | str]

    def __str__(self) -> str:
        ...
```

Elements can be converted to strings:

```python
element = Element(tag="p", attributes={}, children=["hello"])
assert str(element) == "<p>hello</p>"

element2 = Element(tag="div", attributes={"id": "main"}, children=[element])
assert str(element2) == '<div id="main"><p>hello</p></div>'
```

The `html()` function parses PEP 750 template strings to an `Element`:

```python
def html(template: Template) -> Element:
    ...

assert html(t"<p>hello</p>") == Element(tag="p", attributes={}, children=["hello"])
```

The `html()` function supports several features that decide how interpolations are processed based both on their type _and_ their position in the HTML syntax.

Content can be interpolated into the body of an element:

```python
text = "Hello, World!"
element = html(t"<p>{text}</p>")
assert str(element) == "<p>Hello, World!</p>"
```

When content is interpolated, it is also automatically escaped:

```python
evil = "<script>alert('evil')</script>"
element = html(t"<p>{evil}</p>")
assert str(element) == "<p>&lt;script&gt;alert('evil')&lt;/script&gt;</p>"
```

Attribute values can be interpolated:

```python
src = "shrubbery.jpg"
element = html(t'<img src={src} />')
assert str(element) == '<img src="shrubbery.jpg" />'
```

Multiple attributes can be interpolated at once:

```python
attributes = {"src": "shrubbery.jpg", "alt": "A shrubbery"}
element = html(t'<img {attributes} />')
assert str(element) == '<img src="shrubbery.jpg" alt="A shrubbery" />'
```

Boolean attributes are also supported:

```python
attributes = {"type": "text", "required": True}
element = html(t'<input {attributes} />')
assert str(element) == '<input type="text" required />'
```

HTML `Element` instances can be nested:

```python
item1 = html(t"<li>Item 1</li>")
item2 = html(t"<li>Item 2</li>")
element = html(t"<ul>{item1}{item2}</ul>")
assert str(element) == "<ul><li>Item 1</li><li>Item 2</li></ul>"
```

As a convenience, `html()` also supports a simplification for nesting: if an interpolation's value is a `Template`, it is automatically converted to an `Element`:

```python
item1 = t"<li>Item 1</li>"
item2 = t"<li>Item 2</li>"
element = html(t"<ul>{item1}{item2}</ul>")
assert str(element) == "<ul><li>Item 1</li><li>Item 2</li></ul>"
```

Tag names can also be interpolated:

```python
tag = "h1"
element = html(t"<{tag}>Hello, World!</{tag}>")
assert str(element) == "<h1>Hello, World!</h1>"
```

Tag name interpolation allows us to support a simple form of "components". For instance, we can define a `magic()` function that alters both the attributes and children of an element:

```python
def magic(attributes: Mapping[str, str | bool], children: Sequence[Element | str]) -> Element:
    """A simple, but extremely magical, component."""
    magic_attributes = {**attributes, "data-magic": "yes"}
    magic_children = [*children, "Magic!"]
    return Element("div", magic_attributes, magic_children)

element = html(t"<{magic} id="wow"><b>FUN!</b></{magic}>")
assert str(element) == '<div id="wow" data-magic="yes"><b>FUN!</b>Magic!</div>'
```

The `html()` template processing code sees that `magic` is an interpolation, that it occurs in the tag position, and that its value is a `Callable`. As a result, `html()` calls `magic()` with the interpolated children and attributes and uses the result returned _by_ `magic()` as the final `Element`.

**TODO** Tag function "components" aren't implemented... yet!


