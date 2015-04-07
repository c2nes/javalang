import unittest

from pkg_resources import resource_string
from .. import parse, parser


def setup_java_class(content_to_add):
    """ returns an example java class with the
        given content_to_add contained within a method.
    """
    template = """
public class Lambda {

    public static void main(String args[]) {
        %s
    }
}
        """
    return template % content_to_add


class LambdaSupportTest(unittest.TestCase):
    """ Contains tests for java 8 lambda syntax. """

    def test_lambda_support_no_parameters_no_body(self):
        """ tests support for lambda with no parameters and no body. """
        parse.parse(setup_java_class("() -> {};"))

    def test_lambda_support_no_parameters_expression_body(self):
        """ tests support for lambda with no parameters and an
            expression body.
        """
        parse.parse(setup_java_class("() -> 3;"))
        parse.parse(setup_java_class("() -> null;"))
        parse.parse(setup_java_class("() -> { return 21; };"))
        parse.parse(setup_java_class("() -> { System.exit(1); };"))

    def test_lambda_support_no_parameters_complex_expression(self):
        """ tests support for lambda with no parameters and a
            complex expression body.
        """
        code = """
                () -> {
            if (true) return 21;
            else
            {
                int result = 21;
                return result / 2;
            }
        };"""
        parse.parse(setup_java_class(code))

    def test_parameter_no_type_expression_body(self):
        """ tests support for lambda with parameters with inferred types. """
        parse.parse(setup_java_class("(bar) -> bar + 1;"))
        parse.parse(setup_java_class("bar -> bar + 1;"))
        parse.parse(setup_java_class("x -> x.length();"))
        parse.parse(setup_java_class("y -> { y.boom(); };"))

    def test_parameter_with_type_expression_body(self):
        """ tests support for lambda with parameters with formal types. """
        parse.parse(setup_java_class("(int foo) -> { return foo + 2; };"))
        parse.parse(setup_java_class("(String s) -> s.length();"))
        parse.parse(setup_java_class("(int foo) -> foo + 1;"))
        parse.parse(setup_java_class("(Thread th) -> { th.start(); };"))
        parse.parse(setup_java_class("(String foo, String bar) -> "
                                     "foo + bar;"))

    def test_parameters_with_no_type_expression_body(self):
        """ tests support for multiple lambda parameters
            that are specified without their types.
        """
        parse.parse(setup_java_class("(x, y) -> x + y;"))

    def test_parameters_with_mixed_inferred_and_declared_types(self):
        """ this tests that lambda type specification mixing is considered
            invalid as per the specifications.
        """
        with self.assertRaises(parser.JavaSyntaxError):
            parse.parse(setup_java_class("(x, int y) -> x+y;"))

    def test_parameters_inferred_types_with_modifiers(self):
        """ this tests that lambda inferred type parameters with modifiers are
            considered invalid as per the specifications.
        """
        with self.assertRaises(parser.JavaSyntaxError):
            parse.parse(setup_java_class("(x, final y) -> x+y;"))

    def test_invalid_parameters_are_invalid(self):
        """ this tests that invalid lambda parameters are are
            considered invalid as per the specifications.
        """
        with self.assertRaises(parser.JavaSyntaxError):
            parse.parse(setup_java_class("(a b c) -> {};"))


class MethodReferenceSyntaxTest(unittest.TestCase):
    """ Contains tests for java 8 method reference syntax. """

    def test_method_reference(self):
        """ tests that method references are supported. """
        parse.parse(setup_java_class("String::length;"))

    @unittest.expectedFailure
    def test_method_reference_explicit_type_arguments_for_generic_type(self):
        """ currently there is no support for method references
            to an explicit type.
        """
        parse.parse(setup_java_class("List<String>::size;"))

    def test_method_reference_explicit_type_arguments(self):
        """ test support for method references with an explicit type.
        """
        parse.parse(setup_java_class("Arrays::<String> sort;"))


def main():
    unittest.main()

if __name__ == '__main__':
    main()
