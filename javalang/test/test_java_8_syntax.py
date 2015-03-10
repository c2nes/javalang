import unittest

from pkg_resources import resource_string
from .. import parse, parser


class LambdaSupportTest(unittest.TestCase):
    """ Contains tests for java 8 lambda syntax. """

    def _class_template(self, content_to_add):
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

    def test_lambda_support_no_parameters_no_body(self):
        """ tests support for lambda with no parameters and no body. """
        parse.parse(self._class_template("() -> {};"))

    def test_lambda_support_no_parameters_expression_body(self):
        """ tests support for lambda with no parameters and an
            expression body.
        """
        parse.parse(self._class_template("() -> 3;"))
        parse.parse(self._class_template("() -> null;"))
        parse.parse(self._class_template("() -> { return 21; };"))
        parse.parse(self._class_template("() -> { System.exit(1); };"))

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
        parse.parse(self._class_template(code))

    def test_parameter_no_type_expression_body(self):
        """ tests support for lambda with parameters with inferred types. """
        parse.parse(self._class_template("(bar) -> bar + 1;"))
        parse.parse(self._class_template("bar -> bar + 1;"))
        parse.parse(self._class_template("x -> x.length();"))
        parse.parse(self._class_template("y -> { y.boom(); };"))

    def test_parameter_with_type_expression_body(self):
        """ tests support for lambda with parameters with formal types. """
        parse.parse(self._class_template("(int foo) -> { return foo + 2; };"))
        parse.parse(self._class_template("(String s) -> s.length();"))
        parse.parse(self._class_template("(int foo) -> foo + 1;"))
        parse.parse(self._class_template("(Thread th) -> { th.start(); };"))
        parse.parse(self._class_template("(String foo, String bar) -> "
                                         "foo + bar;"))

    @unittest.expectedFailure
    def test_parameters_with_no_type_expression_body(self):
        """ currently there is no support for multiple lambda parameters
            that are specified without their types.
        """
        parse.parse(self._class_template("(x, y) -> x+y;"))

    def test_parameters_with_mixed_inferred_and_declared_types(self):
        """ this tests that lambda type specification mixing is considered
            invalid as per the specifications.
        """
        with self.assertRaises(parser.JavaSyntaxError):
            parse.parse(self._class_template("(x, int y) -> x+y;"))

    def test_parameters_inferred_types_with_modifiers(self):
        """ this tests that lambda inferred type parameters with modifiers are
            considered invalid as per the specifications.
        """
        with self.assertRaises(parser.JavaSyntaxError):
            parse.parse(self._class_template("(x, final y) -> x+y;"))


class MethodReferenceSyntaxTest(unittest.TestCase):
    """ Contains tests for java 8 method reference syntax. """

    def _class_template(self, content_to_add):
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

    def test_method_reference(self):
        """ tests that method references are supported. """
        parse.parse(self._class_template("String::length;"))

    @unittest.expectedFailure
    def test_method_reference_explicit_type_arguments_for_generic_type(self):
        """ currently there is no support for method references
            to an explicit type.
        """
        parse.parse(self._class_template("List<String>::size;"))

    @unittest.expectedFailure
    def test_method_reference_explicit_type_arguments(self):
        """ currently there is no support for method references
            to an explicit type.
        """
        parse.parse(self._class_template("Arrays::<String> sort;"))


def main():
    unittest.main()

if __name__ == '__main__':
    main()
