from setuptools import setup


setup(
    name = "javalang",
    packages = ["javalang"],
    version = "0.14.1",
    author = "Nevil Macwan",
    author_email = "macnev2013@gmail.com",
    url = "http://github.com/macnev2013/javalang",
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
code. javalang provies a lexer and parser targeting Java 8. The
implementation is based on the Java language spec available at
http://docs.oracle.com/javase/specs/jls/se8/html/.

""",
    zip_safe = False,
    install_requires = ['six',],
    tests_require = ["nose",],
    test_suite = "nose.collector",
)
