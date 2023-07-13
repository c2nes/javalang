from .ast import Node
from .tree import *


class JavaVisitor:
    def visit(self, node):
        method = 'visit_' + node.__class__.__name__
        visitor = getattr(self, method, self.generic_visit)
        return visitor(node)
    
    def generic_visit(self, node):
        if node is None:
            return
        if isinstance(node, Node):
            for child in node.children:
                self.visit(child)
        elif isinstance(node, (list,tuple)):
            for item in node:
                self.visit(item)
    
    def visit_CompilationUnit(self, node):
        self.generic_visit(node)
    
    def visit_Import(self, node):
        self.generic_visit(node)

    def visit_Documented(self, node):
        self.generic_visit(node)

    def visit_Declaration(self, node):
        self.generic_visit(node)

    def visit_TypeDeclaration(self, node):
        self.generic_visit(node)

    def visit_PackageDeclaration(self, node):
        self.generic_visit(node)

    def visit_ClassDeclaration(self, node):
        self.generic_visit(node)

    def visit_EnumDeclaration(self, node):
        self.generic_visit(node)

    def visit_InterfaceDeclaration(self, node):
        self.generic_visit(node)

    def visit_AnnotationDeclaration(self, node):
        self.generic_visit(node)

    def visit_Type(self, node):
        self.generic_visit(node)

    def visit_BasicType(self, node):
        self.generic_visit(node)

    def visit_ReferenceType(self, node):
        self.generic_visit(node)

    def visit_TypeArgument(self, node):
        self.generic_visit(node)

    def visit_TypeParameter(self, node):
        self.generic_visit(node)

    def visit_Annotation(self, node):
        self.generic_visit(node)
    
    def visit_ElementValuePair(self, node):
        self.generic_visit(node)
    
    def visit_ElementArrayValue(self, node):
        self.generic_visit(node)
    
    def visit_Member(self, node):
        self.generic_visit(node)

    def visit_MethodDeclaration(self, node):
        self.generic_visit(node)

    def visit_FieldDeclaration(self, node):
        self.generic_visit(node)

    def visit_ConstructorDeclaration(self, node):
        self.generic_visit(node)

    def visit_ConstantDeclaration(self, node):
        self.generic_visit(node)

    def visit_ArrayInitializer(self, node):
        self.generic_visit(node)

    def visit_VariableDeclarator(self, node):
        self.generic_visit(node)

    def LocalVariableDeclaration(self, node):
        self.generic_visit(node)

    def visit_VariableDeclarator(self, node):
        self.generic_visit(node)

    def visit_FormalParameter(self, node):
        self.generic_visit(node)

    def visit_InferredFormalParameter(self, node):
        self.generic_visit(node)

    # ------------------------------------------------------------------------------

    def visit_Statement(self, node):
        self.generic_visit(node)

    def visit_IfStatement(self, node):
        self.generic_visit(node)

    def visit_WhileStatement(self, node):
        self.generic_visit(node)

    def visit_DoStatement(self, node):
        self.generic_visit(node)

    def visit_ForStatement(self, node):
        self.generic_visit(node)

    def visit_AssertStatement(self, node):
        self.generic_visit(node)

    def visit_BreakStatement(self, node):
        self.generic_visit(node)

    def visit_ContinueStatement(self, node):
        self.generic_visit(node)

    def visit_ReturnStatement(self, node):
        self.generic_visit(node)

    def visit_ThrowStatement(self, node):
        self.generic_visit(node)

    def visit_SynchronizedStatement(self, node):
        self.generic_visit(node)

    def visit_TryStatement(self, node):
        self.generic_visit(node)

    def visit_SwitchStatement(self, node):
        self.generic_visit(node)

    def visit_BlockStatement(self, node):
        self.generic_visit(node)

    def visit_StatementExpression(self, node):
        self.generic_visit(node)

    # ------------------------------------------------------------------------------

    def visit_TryResource(self, node):
        self.generic_visit(node)

    def visit_CatchClause(self, node):
        self.generic_visit(node)

    def visit_CatchClauseParameter(self, node):
        self.generic_visit(node)

    # ------------------------------------------------------------------------------

    def visit_SwitchStatementCase(self, node):
        self.generic_visit(node)

    def visit_ForControl(self, node):
        self.generic_visit(node)

    def visit_EnhancedForControl(self, node):
        self.generic_visit(node)

    # ------------------------------------------------------------------------------

    def visit_Expression(self, node):
        self.generic_visit(node)

    def visit_Assignment(self, node):
        self.generic_visit(node)

    def visit_TernaryExpression(self, node):
        self.generic_visit(node)

    def visit_BinaryOperation(self, node):
        self.generic_visit(node)

    def visit_Cast(self, node):
        self.generic_visit(node)

    def visit_MethodReference(self, node):
        self.generic_visit(node)

    def visit_LambdaExpression(self, node):
        self.generic_visit(node)

    # ------------------------------------------------------------------------------

    def visit_Primary(self, node):
        self.generic_visit(node)

    def visit_Literal(self, node):
        self.generic_visit(node)

    def visit_This(self, node):
        self.generic_visit(node)

    def visit_MemberReference(self, node):
        self.generic_visit(node)

    def visit_Invocation(self, node):
        self.generic_visit(node)

    def visit_ExplicitConstructorInvocation(self, node):
        self.generic_visit(node)

    def visit_SuperConstructorInvocation(self, node):
        self.generic_visit(node)

    def visit_MethodInvocation(self, node):
        self.generic_visit(node)

    def visit_SuperMethodInvocation(self, node):
        self.generic_visit(node)

    def visit_SuperMemberReference(self, node):
        self.generic_visit(node)

    def visit_ArraySelector(self, node):
        self.generic_visit(node)

    def visit_ClassReference(self, node):
        self.generic_visit(node)

    def visit_VoidClassReference(self, node):
        self.generic_visit(node)

    # ------------------------------------------------------------------------------

    def visit_Creator(self, node):
        self.generic_visit(node)

    def visit_ArrayCreator(self, node):
        self.generic_visit(node)

    def visit_ClassCreator(self, node):
        self.generic_visit(node)

    def visit_InnerClassCreator(self, node):
        self.generic_visit(node)

    # ------------------------------------------------------------------------------

    def visit_EnumBody(self, node):
        self.generic_visit(node)

    def visit_EnumConstantDeclaration(self, node):
        self.generic_visit(node)

    def visit_AnnotationMethod(self, node):
        self.generic_visit(node)

