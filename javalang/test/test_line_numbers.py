import unittest

from pkg_resources import resource_string
from .. import parse, tree


class TestLineNumbers(unittest.TestCase):

    def get_ast(self, filename):
        source = resource_string(__name__, filename)
        ast = parse.parse(source)
        return ast

    def test_compilation_unit_with_one_line_code(self):
        source_file = "source/package-info/JavadocOnly.java"
        ast = self.get_ast(source_file)
        self.assertEqual(ast.start_position.line, 4)
        self.assertEqual(ast.package.start_position.line, ast.package.end_position.line)

    def test_compilation_unit_with_several_lines(self):
        source_file = "source/package-info/JavadocAnnotation.java"
        ast = self.get_ast(source_file)
        self.assertEqual(ast.start_position.line, 4)
        self.assertEqual(ast.end_position.line, 5)

    def test_package_in_single_line(self):
        source = """
        package org.javalang.test; // line 2
        """
        ast = parse.parse(source)
        self.assertEqual(ast.package.start_position.line, 2)
        self.assertEqual(ast.package.start_position.line, ast.package.end_position.line)

    def test_package_in_multiple_lines(self):
        source = """
        package
            org.javalang.test; // line 2 and 3
        """
        ast = parse.parse(source)
        self.assertEqual(ast.package.start_position.line, 2)
        self.assertEqual(ast.package.end_position.line, 3)

    def test_imports_in_single_line(self):
        source = """
        import java.util.ArrayList; // line 2
        import java.util.List; // line 3
        """
        ast = parse.parse(source)
        self.assertTrue(len(ast.imports), 2)
        self.assertEqual(ast.imports[0].start_position.line, 2)
        self.assertEqual(ast.imports[0].start_position.line, ast.imports[0].end_position.line)
        self.assertEqual(ast.imports[1].start_position.line, 3)
        self.assertEqual(ast.imports[1].start_position.line, ast.imports[1].end_position.line)

    def test_imports_in_multiple_lines(self):
        source = """
        import
            java.util.ArrayList; // line 2 and 3
        import
            java.util.List; // line 4 and 5
        """
        ast = parse.parse(source)
        self.assertTrue(len(ast.imports), 2)
        self.assertEqual(ast.imports[0].start_position.line, 2)
        self.assertEqual(ast.imports[0].end_position.line, 3)
        self.assertEqual(ast.imports[1].start_position.line, 4)
        self.assertEqual(ast.imports[1].end_position.line, 5)

    def test_empty_abstract_class(self):
        source = """
        public abstract class Foo { // line 2 -- 7
            // empty line 3
            // empty line 4
            // empty line 5
            
        }
        """
        ast = parse.parse(source)
        self.assertTrue(len(ast.types), 1)
        clazz = ast.types[0]
        self.assertTrue(isinstance(clazz, tree.ClassDeclaration))
        self.assertEqual(clazz.start_position.line, 2)
        self.assertEqual(clazz.end_position.line, 7)

    def test_abstract_class_with_abstract_method(self):
        source = """
        public abstract class Foo { // line 2 -- 11
            // empty line 3
            // empty line 4
            // empty line 5
            
            public abstract void
                bar(
                    
                );
        }
        """
        ast = parse.parse(source)
        # class
        self.assertTrue(len(ast.types), 1)
        clazz = ast.types[0]
        self.assertTrue(isinstance(clazz, tree.ClassDeclaration))
        self.assertEqual(clazz.start_position.line, 2)
        self.assertEqual(clazz.end_position.line, 11)
        # method
        method = clazz.body[0]
        self.assertTrue(isinstance(method, tree.MethodDeclaration))
        self.assertEqual(method.start_position.line, 7)
        self.assertEqual(method.end_position.line, 10)

    def test_abstract_class_with_non_abstract_method(self):
        source = """
        public abstract class Foo { // line 2 -- 13
            // empty line 3
            // empty line 4
            // empty line 5
            
            public void
                bar(
                    
                ) {
                return;
            }
        }
        """
        ast = parse.parse(source)
        # class
        self.assertTrue(len(ast.types), 1)
        clazz = ast.types[0]
        self.assertTrue(isinstance(clazz, tree.ClassDeclaration))
        self.assertEqual(clazz.start_position.line, 2)
        self.assertEqual(clazz.end_position.line, 13)
        # method
        method = clazz.body[0]
        self.assertTrue(isinstance(method, tree.MethodDeclaration))
        self.assertEqual(method.start_position.line, 7)
        self.assertEqual(method.end_position.line, 12)

    def test_empty_interface(self):
        source = """
        public interface Foo { // line 2 -- 7
            // empty line 3
            // empty line 4
            // empty line 5
            
        }
        """
        ast = parse.parse(source)
        self.assertTrue(len(ast.types), 1)
        clazz = ast.types[0]
        self.assertTrue(isinstance(clazz, tree.InterfaceDeclaration))
        self.assertEqual(clazz.start_position.line, 2)
        self.assertEqual(clazz.end_position.line, 7)

    def test_empty_interface_with_default_method(self):
        source = """
        public interface Foo { // line 2 -- 11
            // empty line 3
            // empty line 4
            // empty line 5
            
            default void
                bar() {
                // default method implementation
            }
        }
        """
        ast = parse.parse(source)
        # class
        self.assertTrue(len(ast.types), 1)
        clazz = ast.types[0]
        self.assertTrue(isinstance(clazz, tree.InterfaceDeclaration))
        self.assertEqual(clazz.start_position.line, 2)
        self.assertEqual(clazz.end_position.line, 11)
        # method
        method = clazz.body[0]
        self.assertTrue(isinstance(method, tree.MethodDeclaration))
        self.assertEqual(method.start_position.line, 7)
        self.assertEqual(method.end_position.line, 10)

    def test_empty_class(self):
        source = """
        public class
            Foo { // line 2 -- 8
            // empty line 3
            // empty line 4
            // empty line 5
            
        }
        """
        ast = parse.parse(source)
        clazz = ast.types[0]
        self.assertTrue(isinstance(clazz, tree.ClassDeclaration))
        self.assertEqual(clazz.start_position.line, 2)
        self.assertEqual(clazz.end_position.line, 8)

    def test_class_with_constructor(self):
        source = """
        public class Foo { // line 2 -- 11
            // empty line 3
            // empty line 4
            // empty line 5
            
            public Foo() {
                // empty constructor
                
            }
        }
        """
        ast = parse.parse(source)
        # class
        clazz = ast.types[0]
        self.assertTrue(isinstance(clazz, tree.ClassDeclaration))
        self.assertEqual(clazz.start_position.line, 2)
        self.assertEqual(clazz.end_position.line, 11)
        # constructor
        constructor = clazz.body[0]
        self.assertTrue(isinstance(constructor, tree.ConstructorDeclaration))
        self.assertEqual(constructor.start_position.line, 7)
        self.assertEqual(constructor.end_position.line, 10)

    def test_class_with_empty_method(self):
        source = """
        public class Foo { // line 2 -- 13
            // empty line 3
            // empty line 4
            // empty line 5
            
            public void
                bar(
                    
                ) {
                
            }
        }
        """
        ast = parse.parse(source)
        # class
        clazz = ast.types[0]
        self.assertTrue(isinstance(clazz, tree.ClassDeclaration))
        self.assertEqual(clazz.start_position.line, 2)
        self.assertEqual(clazz.end_position.line, 13)
        # method
        method = clazz.body[0]
        self.assertTrue(isinstance(method, tree.MethodDeclaration))
        self.assertEqual(method.start_position.line, 7)
        self.assertEqual(method.end_position.line, 12)

    def test_inner_class(self):
        source = """
        public class Foo { // line 2 -- 11
            // empty line 3
            // empty line 4
            // empty line 5
            
            public class Bar {
                // empty line
                
            }
        }
        """
        ast = parse.parse(source)
        # class Foo
        foo = ast.types[0]
        self.assertTrue(isinstance(foo, tree.ClassDeclaration))
        self.assertEqual(foo.start_position.line, 2)
        self.assertEqual(foo.end_position.line, 11)
        # class Bar
        bar = foo.body[0]
        self.assertTrue(isinstance(bar, tree.ClassDeclaration))
        self.assertEqual(bar.start_position.line, 7)
        self.assertEqual(bar.end_position.line, 10)

    def test_enum(self):
        source = """
        public enum
            Letters {
          A,
          B,
          C
          
        }
        """
        ast = parse.parse(source)
        clazz = ast.types[0]
        self.assertTrue(isinstance(clazz, tree.EnumDeclaration))
        self.assertEqual(clazz.start_position.line, 2)
        self.assertEqual(clazz.end_position.line, 8)


def main():
    unittest.main()

if __name__ == '__main__':
    main()
