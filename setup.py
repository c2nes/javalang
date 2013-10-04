
from distutils.core import setup

setup(
    name = "javalang",
    packages = ["javalang"],
    version = __import__("javalang").__version__,
    author = "Chris Thunes",
    author_email = "cthunes@brewtab.com",
    url = "http://github.com/c2nes/javalang",
    description = "Pure Python Java parser and tools",
    classifiers = [
        "Programming Language :: Python",
        "Development Status :: 4 - Beta",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: MIT License",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries"
        ],
    long_description = """\
========
javalang
========

javalang is a pure Python library for working with Java source
code. javalang provies a lexer and parser targeting Java 7. The
implementation is based on the Java language spec available at
http://docs.oracle.com/javase/specs/jls/se7/html/.

"""
)
