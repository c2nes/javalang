# javalang-plus

`javalang-plus` builds on [javalang](https://github.com/c2nes/javalang), which is a pure Python library for working with Java source
code, providing a lexer and parser targeting Java 8. The
implementation is based on the Java language spec available at
http://docs.oracle.com/javase/specs/jls/se8/html/. The `javalang-plus` library builds upon javalang and
adds quality-of-life updates to make use easier.

If you are already familiar with javalang, the ways `javalang-plus` improves on javalang are:
 * A synactic element-deducing (but potentially slower) parse function. No more do you need to look up the type of the code snippet that you are looking at.
 * More complete location information for AST nodes
 * "Unparsing" or reconstructing code from the AST
 * Pretty printing ASTs

The following gives a very brief introduction to using `javalang-plus`.

## Getting Started

To parse code, one may use the `javalang.parse.parse` function:

```python
>>> import javalang
>>> tree = javalang.parse.parse("package javalang.brewtab.com; class Test {}")
```

In this case, the library will return a `CompilationUnit` instance. While javalang could only
parse `CompilationUnit` code using this function, `javalang-plus` tries to deduce how the given
code snippet should be parsed. For example,

```python
>>> javalang.parse.parse("int counter = 0;")
FieldDeclaration(annotations=[], declarators=[...], ...)
```
fails for javalang, but `javalang-plus` deduces that it is potentially a `FieldDeclaration`
and returns the corresponding node.

Attributes of each `Node` instance can be assessed using the dot (`.`) operator, as showcased below.

```python
>>> tree.package.name
u'javalang.brewtab.com'
>>> tree.types[0]
ClassDeclaration
>>> tree.types[0].name
u'Test'
```

### Working with the syntax tree

AST nodes are represented using `javalang.ast.Node` instances;
the ``javalang.tree`` module defines the different
types of ``Node`` subclasses, each of which represent the different syntaxual
elements you will find in Java code. For more detail on what node types are
available, see the ``javalang/tree.py`` source file until the documentation is
complete.

``Node`` instances support iteration,

```python
>>> for path, node in tree:
...     print path, node
... 
() CompilationUnit
(CompilationUnit,) PackageDeclaration
(CompilationUnit, [ClassDeclaration]) ClassDeclaration
```

which can also be filtered by type.

```python
>>> for path, node in tree.filter(javalang.tree.ClassDeclaration):
...     print path, node
... 
(CompilationUnit, [ClassDeclaration]) ClassDeclaration
```

`javalang-plus` also implements a number of utility functionalities that help program analysis.

One is extracting the _position_ of syntactic elements:

```python
>>> root = javalang.parse.parse('int counter = 0;')
>>> root.type.name
'int'
>>> root.type.position
(Position(line=1, column=1), Position(line=1, column=4))
```

Another is "unparsing", or reconstructing code from the AST (done via the `javalang.unparser.unparse` function):

```python
>>> root = javalang.parse.parse('int counter = 0;')
>>> root.declarators[0].initializer.value = "1"
>>> javalang.unparser.unparse(root)
'int counter = 1;'
```

Further, the AST can be explored using the `Node.pprint()` function. (Output below is truncated for brevity.)

```python
>>> root = javalang.parse.parse('int counter = 0;')
>>> root.pprint()
<class 'javalang.tree.FieldDeclaration'>
| *annotations[]:
| *declarators[]:
| | <class 'javalang.tree.VariableDeclarator'>
| | | *dimensions[]:
| | | *initializer:
[...]
```

## Component Usage

Internally, the ``javalang.parse.parse`` method is a simple method which creates
a token stream for the input, initializes a new ``javalang.parser.Parser``
instance with the given token stream, and then invokes the parser's ``parse()``
method, returning the resulting ``CompilationUnit``. These components may be
also be used individually: for example, one may use the tokenization separately,
as specified below.

### Tokenizer

The tokenizer/lexer may be invoked directly be calling `javalang.tokenizer.tokenize`,

```python
>>> javalang.tokenizer.tokenize('System.out.println("Hello " + "world");')
<generator object tokenize at 0x1ce5190>
```

This returns a generator which provides a stream of ``JavaToken`` objects. Each
token carries position (line, column) and value information,

```python
>>> tokens = list(javalang.tokenizer.tokenize('System.out.println("Hello " + "world");'))
>>> tokens[6].value
u'"Hello "'
>>> tokens[6].position
(1, 19)
```

The tokens are not directly instances of ``JavaToken``, but are instead
instances of subclasses which identify their general type,

```python
>>> type(tokens[6])
<class 'javalang.tokenizer.String'>
>>> type(tokens[7])
<class 'javalang.tokenizer.Operator'>
```


**NOTE:** The shift operators `>>` and `>>>` are represented by multiple
`>` tokens. This is because multiple `>` may appear in a row when closing
nested generic parameter/arguments lists. This ambiguity is instead resolved by
the parser.

### Parser

To parse snippets of code, a specific parsing function (in the example below, `parse_expression`)
may be invoked. This is generally faster than the `parse.parse` function
when one knows what the type of the expression will be beforehand.

```python
>>> tokens = javalang.tokenizer.tokenize('System.out.println("Hello " + "world");')
>>> parser = javalang.parser.Parser(tokens)
>>> parser.parse_expression()
MethodInvocation
```

However, invoking the incorrect parse method will also result in a ``JavaSyntaxError``
exception.

```python
>>> tokens = javalang.tokenizer.tokenize('System.out.println("Hello " + "world");')
>>> parser = javalang.parser.Parser(tokens)
>>> parser.parse_type_declaration()
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "javalang/parser.py", line 336, in parse_type_declaration
    return self.parse_class_or_interface_declaration()
  File "javalang/parser.py", line 353, in parse_class_or_interface_declaration
    self.illegal("Expected type declaration")
  File "javalang/parser.py", line 122, in illegal
    raise JavaSyntaxError(description, at)
javalang.parser.JavaSyntaxError
```

It is also worth noting that
the parse methods are designed for incremental parsing so they will not restart
at the beginning of the token stream. Attempting to call a parse method more
than once will result in a ``JavaSyntaxError`` exception.
