
from ast import Node

# ------------------------------------------------------------------------------

class CompilationUnit(Node):
    attrs = ("package", "imports", "types")

class Import(Node):
    attrs = ("path", "static", "wildcard")

class Declaration(Node):
    attrs = ("modifiers", "annotations")

class PackageDeclaration(Declaration):
    attrs = ("name",)

class ClassDeclaration(Declaration):
    attrs = ("name", "type_parameters", "extends", "implements", "body")

class EnumDeclaration(Declaration):
    attrs = ("name", "implements", "body")

class InterfaceDeclaration(Declaration):
    attrs = ("name", "type_parameters", "extends", "body")

class AnnotationDeclaration(Declaration):
    attrs = ("name", "body")

# ------------------------------------------------------------------------------

class Type(Node):
    attrs = ("name", "dimensions",)

class BasicType(Type):
    attrs = ()

class ReferenceType(Type):
    attrs = ("arguments", "subtype")

class TypeArgument(Node):
    attrs = ("type", "pattern_type")

# ------------------------------------------------------------------------------

class TypeParameter(Node):
    attrs = ("name", "extends")

# ------------------------------------------------------------------------------

class Annotation(Node):
    attrs = ("annotation", "element")

class ElementValuePair(Node):
    attrs = ("name", "value")

class ElementArrayValue(Node):
    attrs = ("values",)

# ------------------------------------------------------------------------------

class TypeBody(Node):
    attrs = ("declarations",)

    @property
    def fields(self):
        return filter(lambda decl: isinstance(decl, FieldDeclaration), self.declarations)

    @property
    def methods(self):
        return filter(lambda decl: isinstance(decl, MethodDeclaration), self.declarations)

    @property
    def constructors(self):
        return filter(lambda decl: isinstance(decl, ConstructorDeclaration), self.declarations)

class Member(Node):
    attrs = ()

class MethodDeclaration(Member, Declaration):
    attrs = ("type_parameters", "return_type", "name", "parameters", "throws", "body")

class FieldDeclaration(Member, Declaration):
    attrs = ("type", "declarators")

class ConstructorDeclaration(Declaration):
    attrs = ("type_parameters", "name", "parameters", "throws", "body")

# ------------------------------------------------------------------------------

class ConstantDeclaration(FieldDeclaration):
    attrs = ()

class ArrayInitializer(Node):
    attrs = ("initializers",)

class VariableDeclaration(Declaration):
    attrs = ("type", "declarators")

class LocalVariableDeclaration(VariableDeclaration):
    attrs = ()

class VariableDeclarator(Node):
    attrs = ("name", "dimensions", "initializer")

class FormalParameter(Declaration):
    attrs = ("type", "name", "varargs")

# ------------------------------------------------------------------------------

class Statement(Node):
    attrs = ("label",)

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

class StatementExpression(Statement):
    attrs = ("expression",)

# ------------------------------------------------------------------------------

class TryResource(Declaration):
    attrs = ("type", "name", "value")

class CatchClause(Statement):
    attrs = ("parameter", "block")

class CatchClauseParameter(Declaration):
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

class Assignment(Expression):
    attrs = ("expressionl", "value", "type")

class TernaryExpression(Expression):
    attrs = ("condition", "if_true", "if_false")

class BinaryOperation(Expression):
    attrs = ("operator", "operandl", "operandr")

class Cast(Expression):
    attrs = ("type", "expression")

# ------------------------------------------------------------------------------

class Primary(Expression):
    attrs = ("prefix_operations", "postfix_operations", "qualifier", "selectors")

class Literal(Primary):
    attrs = ("value",)

class This(Primary):
    attrs = ()

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

# ------------------------------------------------------------------------------

class EnumBody(Node):
    attrs = ("constants", "declarations")

class EnumConstantDeclaration(Declaration):
    attrs = ("name", "arguments", "body")

class AnnotationMethod(Declaration):
    attrs = ("name", "return_type", "dimensions", "default")

