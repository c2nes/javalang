
from .ast import Node

# ------------------------------------------------------------------------------


class CompilationUnit(Node):
    attrs = ("package", "imports", "types")


class Import(Node):
    attrs = ("path", "static", "wildcard")


class Documented(Node):
    attrs = ("documentation",)


class Declaration(Documented):
    attrs = ()


class EmptyDeclaration(Declaration):
    attrs = ()


class NonEmptyDeclaration(Declaration):
    attrs = ("modifiers", "annotations")


class TypeDeclaration(NonEmptyDeclaration):
    attrs = ("name", "body")

    @property
    def fields(self):
        return [decl for decl in self.body if isinstance(decl,
                                                         FieldDeclaration)]

    @property
    def methods(self):
        return [decl for decl in self.body if isinstance(decl,
                                                         MethodDeclaration)]

    @property
    def constructors(self):
        return [decl for decl in self.body if isinstance(
          decl, ConstructorDeclaration)]


class PackageDeclaration(NonEmptyDeclaration):
    attrs = ("name",)


class ClassDeclaration(TypeDeclaration):
    attrs = ("type_parameters", "extends", "implements")


class EnumDeclaration(TypeDeclaration):
    attrs = ("implements",)

    @property
    def fields(self):
        return [decl for decl in self.body.declarations if isinstance(
          decl, FieldDeclaration)]

    @property
    def methods(self):
        return [decl for decl in self.body.declarations if isinstance(
          decl, MethodDeclaration)]


class InterfaceDeclaration(TypeDeclaration):
    attrs = ("type_parameters", "extends",)


class AnnotationDeclaration(TypeDeclaration):
    attrs = ()


class StaticInitializer(NonEmptyDeclaration):
    attrs = ("block",)


class InstanceInitializer(NonEmptyDeclaration):
    attrs = ("block",)

# ------------------------------------------------------------------------------


class ArrayDimension(Node):
    attrs = ("dim",)


class Modifier(Node):
    attrs = ("value",)


class Operator(Node):
    attrs = ("operator",)

# ------------------------------------------------------------------------------


class Type(Node):
    attrs = ("name", "dimensions",)


class BasicType(Type):
    attrs = ()


class DiamondType(Type):
    attrs = ("sub_type",)


class ReferenceType(Type):
    attrs = ("arguments", "sub_type",)


class TypeArgument(Node):
    attrs = ("type", "pattern_type")

# ------------------------------------------------------------------------------


class TypeParameter(Node):
    attrs = ("name", "extends")

# ------------------------------------------------------------------------------


class Annotation(Node):
    attrs = ("name", "element")


class NormalAnnotation(Annotation):
    attrs = ()


class MarkerAnnotation(Annotation):
    attrs = ()


class SingleElementAnnotation(Annotation):
    attrs = ()


class ElementValuePair(Node):
    attrs = ("name", "value")


class ElementArrayValue(Node):
    attrs = ("values",)

# ------------------------------------------------------------------------------


class Member(NonEmptyDeclaration):
    attrs = ()


class MethodDeclaration(Member):
    attrs = ("type_parameters", "return_type", "name", "dimensions",
             "parameters", "throws", "body")


class FieldDeclaration(Member):
    attrs = ("type", "declarators")


class ConstructorDeclaration(NonEmptyDeclaration):
    attrs = ("type_parameters", "name", "parameters", "throws", "body")

# ------------------------------------------------------------------------------


class ConstantDeclaration(FieldDeclaration):
    attrs = ()


class VariableInitializer(Node):
    """
    A VariableInitializer is either an expression or an array initializer
    https://docs.oracle.com/javase/specs/jls/se8/html/jls-8.html#jls-8.3
    """
    attrs = ("expression", "array")


class ArrayInitializer(Node):
    attrs = ("initializers", "comma")


class VariableDeclaration(NonEmptyDeclaration):
    attrs = ("type", "declarators")


class LocalVariableDeclaration(VariableDeclaration):
    attrs = ()


class VariableDeclarator(Node):
    attrs = ("name", "dimensions", "initializer")


class FormalParameter(NonEmptyDeclaration):
    attrs = ("type", "name", "dimensions", "varargs")


class InferredFormalParameter(Node):
    attrs = ('expression',)

# ------------------------------------------------------------------------------


class Statement(Node):
    attrs = ("label",)


class LocalVariableDeclarationStatement(Statement):
    attrs = ("variable",)


class TypeDeclarationStatement(Statement):
    attrs = ("declaration",)


class IfStatement(Statement):
    attrs = ("condition", "then_statement", "else_statement")


class WhileStatement(Statement):
    attrs = ("condition", "body")


class DoStatement(Statement):
    attrs = ("condition", "body")


class ForStatement(Statement):
    attrs = ("control", "body")


class AssertStatement(Statement):
    attrs = ("condition", "value")


class BreakStatement(Statement):
    attrs = ("goto",)


class ContinueStatement(Statement):
    attrs = ("goto",)


class ReturnStatement(Statement):
    attrs = ("expression",)


class ThrowStatement(Statement):
    attrs = ("expression",)


class SynchronizedStatement(Statement):
    attrs = ("lock", "block")


class TryStatement(Statement):
    attrs = ("resources", "block", "catches", "finally_block")


class SwitchStatement(Statement):
    attrs = ("expression", "cases")


class BlockStatement(Statement):
    attrs = ("statements",)


class ExpressionStatement(Statement):
    attrs = ("expression",)

# ------------------------------------------------------------------------------


class TryResource(NonEmptyDeclaration):
    attrs = ("type", "name", "value")


class CatchClause(Statement):
    attrs = ("parameter", "block")


class CatchClauseParameter(NonEmptyDeclaration):
    attrs = ("types", "name")

# ------------------------------------------------------------------------------


class SwitchStatementCase(Node):
    attrs = ("case", "statements")


class ForControl(Node):
    attrs = ("init", "condition", "update")


class EnhancedForControl(Node):
    attrs = ("var", "iterable")

# ------------------------------------------------------------------------------


class Expression(Node):
    attrs = ()


class ElementValueArrayInitializer(Expression):
    attrs = ("initializer",)


class ReferenceTypeExpression(Expression):
    attrs = ("type",)


class BlockExpression(Expression):
    attrs = ("block",)


class NoExpression(Expression):
    attrs = ()


class Primary(Expression):
    attrs = ("prefix_operators", "postfix_operators", "qualifier", "selectors")


class ParenthesizedExpression(Primary):
    attrs = ("expression",)


class Assignment(Primary):
    attrs = ("expressionl", "value", "type")


class TernaryExpression(Primary):
    attrs = ("condition", "if_true", "if_false")


class BinaryOperation(Primary):
    attrs = ("operator", "operandl", "operandr")


class MethodReference(Primary):
    attrs = ("expression", "method", "type_arguments")


class LambdaExpression(Primary):
    attrs = ('parameter', 'parameters', 'body')

# ------------------------------------------------------------------------------


class Identifier(Primary):
    attrs = ("id",)


class Literal(Primary):
    attrs = ("value",)


class This(Primary):
    attrs = ()


class Cast(Primary):
    attrs = ("type", "expression")


class FieldReference(Primary):
    attrs = ("field",)


class MemberReference(Primary):
    attrs = ("member",)


class Invocation(Primary):
    attrs = ("type_arguments", "arguments")


class ExplicitConstructorInvocation(Invocation):
    attrs = ()


class SuperConstructorInvocation(Invocation):
    attrs = ()


class MethodInvocation(Invocation):
    attrs = ("member",)


class SuperMethodInvocation(Invocation):
    attrs = ("member",)


class SuperMemberReference(Primary):
    attrs = ("member",)


class ArraySelector(Expression):
    attrs = ("index",)


class ClassReference(Primary):
    attrs = ("type",)


class VoidClassReference(ClassReference):
    attrs = ()

# ------------------------------------------------------------------------------


class Creator(Primary):
    attrs = ("type",)


class ArrayCreator(Creator):
    attrs = ("dimensions", "initializer")


class ClassCreator(Creator):
    attrs = ("constructor_type_arguments", "arguments", "body")


class InnerClassCreator(Creator):
    attrs = ("constructor_type_arguments", "arguments", "body")


class ClassBody(Node):
    attrs = ("declarations",)


class EmptyClassBody(Node):
    attrs = ()

# ------------------------------------------------------------------------------


class EnumBody(Node):
    attrs = ("constants", "separator", "declarations", "comma")


class EnumConstantDeclaration(NonEmptyDeclaration):
    attrs = ("name", "arguments", "body")


class AnnotationMethod(NonEmptyDeclaration):
    attrs = ("name", "return_type", "dimensions", "default")

