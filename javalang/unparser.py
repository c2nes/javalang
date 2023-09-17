import six

from .ast import Node
from . import util
from . import tree

INDENT_SIZE = 4

def _get_prefix_str(prefix_operators):
    if prefix_operators is None:
        return ''
    else:
        return ''.join(prefix_operators)

def _get_postfix_str(postfix_operators):
    if postfix_operators is None:
        return ''
    else:
        return ''.join(postfix_operators)

def _get_selector_str(selectors):
    if selectors is None or len(selectors) == 0:
        return ""
    else:
        base_str = ""
        for e in selectors:
            if isinstance(e, tree.ArraySelector):
                base_str += unparse(e)
            else:
                base_str += '.' + unparse(e)
        return base_str

def _get_modifier_str(modifiers, trailing_space=False):
    if modifiers is None:
        return ''
    else:
        return ' '.join(modifiers) + (' ' if trailing_space and len(modifiers) > 0 else '')

def _get_type_arguments_str(type_arguments, leading_space=False, trailing_space=False):
    if type_arguments is None or len(type_arguments) == 0:
        return ''
    else:
        leading_str = ' ' if leading_space else ''
        trailing_str = ' ' if trailing_space else ''
        return leading_str + '<' + ', '.join(unparse(e) for e in type_arguments) + '>' + trailing_str

def _get_annotation_str(annotations, indent_str):
    if annotations is None or len(annotations) == 0:
        return ''
    else:
        return indent_str + ' '.join(unparse(e) for e in annotations) + '\n'

def _get_label_str(label, indent_str):
    if label is None:
        return ''
    else:
        return indent_str + label + ':\n'

def _get_body_str(elements, indent):
    indent_str = ' ' * INDENT_SIZE * indent
    if elements is None:
        return ""
    elif isinstance(elements, tree.Node):
        assert isinstance(elements, tree.EnumBody)
        body_statements = unparse(elements, indent=indent+1)
        return " {\n" + body_statements + "\n" + indent_str + "}"
    elif isinstance(elements, list):
        body_statements = "\n".join(unparse(e, indent=indent+1) for e in elements)
        return " {\n" + body_statements + "\n" + indent_str + "}"
    else:
        raise ValueError(f"Invalid body type {type(elements)}")

def _get_qualifier_str(qualifier):
    if qualifier is None or len(qualifier) == 0:
        return ''
    else:
        return qualifier + '.'

def unparse(node, indent=0):
    indent_str = ' ' * INDENT_SIZE * indent
    if isinstance(node, tree.CompilationUnit):
        package_str = indent_str + "package %s;" % node.package.name if node.package else ""
        imports_str = "\n".join(indent_str + unparse(imp, indent=indent) for imp in node.imports)
        types_str = "\n".join(unparse(typ, indent=indent) for typ in node.types)
        return "%s\n\n%s\n\n%s" % (package_str, imports_str, types_str)
    elif isinstance(node, tree.Import):
        if node.static:
            import_prefix = "import static "
        else:
            import_prefix = "import "
        import_prefix = indent_str + import_prefix
        if node.wildcard:
            return import_prefix + node.path + ".*;"
        else:
            return import_prefix + node.path + ";"
    elif isinstance(node, tree.PackageDeclaration):
        return indent_str + "package %s;" % node.name
    elif isinstance(node, tree.ClassDeclaration):
        annotation_str = _get_annotation_str(node.annotations, indent_str)
        modifier_str = indent_str + _get_modifier_str(node.modifiers)
        name = node.name
        typep_str = _get_type_arguments_str(node.type_parameters)
        extends = " extends " + unparse(node.extends) if node.extends else ""
        implements = " implements " + ", ".join(map(unparse, node.implements)) if node.implements else ""
        body_str = _get_body_str(node.body, indent)
        return "%s%s class %s%s%s%s" % (annotation_str, modifier_str, name, typep_str, extends, implements) + body_str
    elif isinstance(node, tree.EnumDeclaration):
        annotation_str = _get_annotation_str(node.annotations, indent_str)
        modifier_str = indent_str + _get_modifier_str(node.modifiers)
        name = node.name
        implements = " implements " + ", ".join(map(unparse, node.implements)) if node.implements else ""
        body_str = _get_body_str(node.body, indent)
        return "%s%s enum %s%s%s" % (annotation_str, modifier_str, name, implements, body_str)
    elif isinstance(node, tree.InterfaceDeclaration):
        annotation_str = _get_annotation_str(node.annotations, indent_str)
        modifier_str = indent_str + _get_modifier_str(node.modifiers)
        name = node.name
        typep_str = _get_type_arguments_str(node.type_parameters)
        extends = " extends " + ", ".join(map(unparse, node.extends)) if node.extends else ""
        body_str = _get_body_str(node.body, indent)
        return "%s%s interface %s%s%s" % (annotation_str, modifier_str, name, typep_str, extends) + body_str
    elif isinstance(node, tree.AnnotationDeclaration):
        annotation_str = _get_annotation_str(node.annotations, indent_str)
        modifier_str = indent_str + _get_modifier_str(node.modifiers)
        name = node.name
        body_str = _get_body_str(node.body, indent)
        return "%s%s @interface %s" % (annotation_str, modifier_str, name) + body_str

    elif isinstance(node, tree.BasicType):
        if node.dimensions is not None:
            return node.name + "".join("[]" for _ in range(len(node.dimensions)))
        else:
            return node.name
    elif isinstance(node, tree.ReferenceType):
        if node.sub_type is not None:
            subtype_str = '.' + unparse(node.sub_type)
        else:
            subtype_str = ''
        if node.arguments is not None:
            args_str = '<' + ', '.join(unparse(a) for a in node.arguments) + '>'
        else:
            args_str = ''
        name_str = node.name + args_str + subtype_str
        if node.dimensions is None:
            return name_str
        else:
            return name_str + "".join("[]" for _ in range(len(node.dimensions)))
    elif isinstance(node, tree.TypeArgument):
        if node.pattern_type is None:
            return unparse(node.type)
        elif node.pattern_type == '?':
            assert node.type is None, 'what does this look like?'
            return '?'
        elif node.pattern_type == 'extends':
            return '? extends ' + unparse(node.type)
        elif node.pattern_type == 'super':
            return '? super ' + unparse(node.type)
        else:
            raise ValueError('Unknown pattern type: %s' % node.pattern_type)
    
    elif isinstance(node, tree.TypeParameter):
        extends_str = (" extends " + " & ".join(unparse(e) for e in node.extends)) if node.extends else ""
        return node.name + extends_str

    elif isinstance(node, tree.Annotation):
        if isinstance(node.element, list):
            return "@%s(%s)" % (node.name, ", ".join(unparse(arg) for arg in node.element))
        elif isinstance(node.element, Node):
            return "@%s(%s)" % (node.name, unparse(node.element))
        elif node.element is None:
            return "@%s" % node.name
    elif isinstance(node, tree.ElementValuePair):
        return "%s = %s" % (node.name, unparse(node.value))
    elif isinstance(node, tree.ElementArrayValue):
        return "{%s}" % ", ".join(unparse(v) for v in node.values)

    elif isinstance(node, tree.MethodDeclaration):
        annotation_str = _get_annotation_str(node.annotations, indent_str)
        modifier_str = indent_str + _get_modifier_str(node.modifiers, trailing_space=True)
        typep_str = _get_type_arguments_str(node.type_parameters, trailing_space=True)
        return_type = unparse(node.return_type) if node.return_type is not None else "void"
        method_name = node.name
        params = ", ".join(unparse(p) for p in node.parameters)
        throws = " throws " + ", ".join(t for t in node.throws) if node.throws is not None else ""
        body_str = _get_body_str(node.body, indent)
        body_str = body_str if body_str != "" else " { ; }"
        return "%s%s%s%s %s(%s)%s%s" % (annotation_str, modifier_str, typep_str, return_type, method_name, params, throws, body_str)
    elif isinstance(node, tree.FieldDeclaration):
        annotation_str = _get_annotation_str(node.annotations, indent_str)
        modifier_str = annotation_str + indent_str + _get_modifier_str(node.modifiers, trailing_space=True)
        all_dec_str = modifier_str + unparse(node.type) + " "
        for var in node.declarators:
            dec_str = unparse(var)
            all_dec_str += dec_str + ', '
        all_dec_str = all_dec_str[:-2] + ';'
        return all_dec_str
    elif isinstance(node, tree.ConstructorDeclaration):
        annotation_str = _get_annotation_str(node.annotations, indent_str)
        modifier_str = indent_str + _get_modifier_str(node.modifiers)
        typep_str = _get_type_arguments_str(node.type_parameters, leading_space=True)
        name = node.name
        params = ", ".join(unparse(p) for p in node.parameters)
        throws = " throws " + ", ".join(t for t in node.throws) if node.throws is not None else ""
        body_str = _get_body_str(node.body, indent)
        return "%s%s%s %s(%s)%s%s" % (annotation_str, modifier_str, typep_str, name, params, throws, body_str)

    elif isinstance(node, tree.ArrayInitializer):
        return "{%s}" % ", ".join(unparse(e) for e in node.initializers)
    elif isinstance(node, tree.VariableDeclaration) and not isinstance(node, tree.LocalVariableDeclaration):
        modifier_str = _get_modifier_str(node.modifiers, trailing_space=True)
        all_dec_str = indent_str + modifier_str + unparse(node.type) + " " 
        for var in node.declarators:
            dec_str = unparse(var)
            all_dec_str += dec_str + ', '
        all_dec_str = all_dec_str[:-2] + ';'
        return all_dec_str
    elif isinstance(node, tree.LocalVariableDeclaration):
        annotation_str = _get_annotation_str(node.annotations, indent_str)
        modifier_str = _get_modifier_str(node.modifiers, trailing_space=True)
        all_dec_str = annotation_str + indent_str + modifier_str + unparse(node.type) + " " 
        for var in node.declarators:
            dec_str = unparse(var)
            all_dec_str += dec_str + ', '
        all_dec_str = all_dec_str[:-2] + ';\n'
        return all_dec_str
    elif isinstance(node, tree.VariableDeclarator):
        if node.initializer is not None:
            return "%s = %s" % (node.name, unparse(node.initializer))
        else:
            return node.name
    elif isinstance(node, tree.FormalParameter):
        annotation_str = _get_annotation_str(node.annotations, indent_str).strip()
        annotation_str += " " if annotation_str != "" else ""
        modifier_str = _get_modifier_str(node.modifiers, trailing_space=True)
        vararg_str = " ... " if node.varargs else " "
        return annotation_str + modifier_str + unparse(node.type) + vararg_str + node.name

    elif isinstance(node, tree.IfStatement):
        label_str = _get_label_str(node.label, indent_str)
        preamble = label_str + indent_str + "if (%s)" % unparse(node.condition)
        then_statement = unparse(node.then_statement, indent=indent).strip()
        else_statement = unparse(node.else_statement, indent=indent).strip() if node.else_statement is not None else ""
        if len(else_statement) > 0:
            return "%s %s else %s" % (preamble, then_statement, else_statement)
        else:
            return "%s %s" % (preamble, then_statement)
    elif isinstance(node, tree.WhileStatement):
        label_str = _get_label_str(node.label, indent_str)
        preamble = label_str + indent_str + "while (%s) " % unparse(node.condition)
        statement = unparse(node.body, indent=indent)
        return "%s %s" % (preamble, statement)
    elif isinstance(node, tree.DoStatement):
        label_str = _get_label_str(node.label, indent_str)
        preamble = label_str + indent_str + "do "
        condition = unparse(node.condition)
        statement = unparse(node.body, indent=indent)
        return "%s%s while (%s);" % (preamble, statement, condition)
    elif isinstance(node, tree.ForStatement):
        label_str = _get_label_str(node.label, indent_str)
        preamble = label_str + indent_str
        forcontrol = unparse(node.control)
        statement = unparse(node.body, indent=indent).strip()
        return "%sfor (%s) %s" % (preamble, forcontrol, statement)
    elif isinstance(node, tree.AssertStatement):
        value_str = " : " + unparse(node.value) if node.value is not None else ""
        return indent_str + "assert(%s)%s;" % (unparse(node.condition), value_str)
    elif isinstance(node, tree.BreakStatement):
        goto_str = " %s" % node.goto if node.goto is not None else ""
        return indent_str + "break%s;" % goto_str
    elif isinstance(node, tree.ContinueStatement):
        goto_str = " %s" % node.goto if node.goto is not None else ""
        return indent_str + "continue%s;" % goto_str
    elif isinstance(node, tree.ReturnStatement):
        return indent_str + "return %s;" % unparse(node.expression) if node.expression is not None else "return;"
    elif isinstance(node, tree.ThrowStatement):
        return indent_str + "throw %s;" % unparse(node.expression)
    elif isinstance(node, tree.SynchronizedStatement):
        label_str = _get_label_str(node.label, indent_str)
        body_str = _get_body_str(node.block, indent)
        return label_str + indent_str + "synchronized (%s) %s" % (unparse(node.lock), body_str)
    elif isinstance(node, tree.TryStatement):
        preamble = _get_label_str(node.label, indent_str) + indent_str
        block_str = _get_body_str(node.block, indent)
        if node.resources is not None:
            # assert len(node.resources) == 1, "I don't know what more than one resource looks like"
            preamble += "try (%s)" % '; '.join([unparse(e) for e in node.resources])
        else:
            preamble += "try"
        if node.catches is not None:
            catch_clauses = [unparse(catch, indent=indent) for catch in node.catches]
        else:
            catch_clauses = []
        if node.finally_block is None:
            return "%s%s %s" % (preamble, block_str, " ".join(catch_clauses))
        else:
            finally_block_str = _get_body_str(node.finally_block, indent)
            return "%s%s %s finally {%s}" % (preamble, block_str, " ".join(catch_clauses), finally_block_str)
    elif isinstance(node, tree.SwitchStatement):
        label_str = _get_label_str(node.label, indent_str)
        expression_str = unparse(node.expression)
        block_str = _get_body_str(node.cases, indent)
        return "%s%sswitch (%s)%s" % (label_str, indent_str, expression_str, block_str)
    elif isinstance(node, tree.BlockStatement):
        label_str = _get_label_str(node.label, indent_str)
        block_str = _get_body_str(node.statements, indent).strip()
        static_str = "static " if hasattr(node, 'static') and node.static else ""
        return label_str + indent_str + static_str + block_str
    elif isinstance(node, tree.StatementExpression):
        return indent_str + unparse(node.expression) + ";"
    
    elif isinstance(node, tree.TryResource):
        modifier_str = _get_modifier_str(node.modifiers, trailing_space=True)
        type_str = unparse(node.type)
        name_str = node.name
        value_str = " = %s" % unparse(node.value) if node.value is not None else ""
        return modifier_str + type_str + " " + name_str + value_str
    elif isinstance(node, tree.CatchClause):
        block_str = _get_body_str(node.block, indent)
        return "catch (%s)%s" % (unparse(node.parameter), block_str)
    elif isinstance(node, tree.CatchClauseParameter):
        modifier_str = _get_modifier_str(node.modifiers, trailing_space=True)
        type_collation = " | ".join(node.types)
        return "%s%s %s" % (modifier_str, type_collation, node.name)

    elif isinstance(node, tree.SwitchStatementCase):
        indiv_cases = [unparse(case) if isinstance(case, Node) else case for case in node.case]
        if len(indiv_cases) > 0:
            cases_str = '\n'.join([indent_str + ("case %s:" % c if c is not None else "default:")
                                   for c in indiv_cases])
        else:
            cases_str = indent_str + "default:"
        statements_str = "\n".join(unparse(stmt, indent=indent+1) for stmt in node.statements)
        return "%s\n%s" % (cases_str, statements_str)
    elif isinstance(node, tree.ForControl):
        if node.init is not None:
            if type(node.init) == list:
                init = ", ".join(unparse(init) for init in node.init) + ";"
            else:
                init = unparse(node.init)
        else:
            init = ""
        if node.condition is not None:
            cond = unparse(node.condition)
        else:
            cond = ""
        if node.update is not None:
            update = ", ".join(unparse(u) for u in node.update)
        else:
            update = ""
        return "%s %s; %s" % (init, cond, update)
    elif isinstance(node, tree.EnhancedForControl):
        var_dec_without_semicolon = unparse(node.var)[:-1]
        return "%s : %s" % (var_dec_without_semicolon, unparse(node.iterable))

    elif isinstance(node, tree.Assignment):
        if hasattr(node, 'selectors'):
            selectors_str = _get_selector_str(node.selectors)
            template_str = '(%s %s %s)' + selectors_str
        else:
            template_str = '%s %s %s'
        return template_str % (unparse(node.expressionl), node.type, unparse(node.value))
    elif isinstance(node, tree.TernaryExpression):
        base_str = "%s ? %s : %s" % (unparse(node.condition), unparse(node.if_true), unparse(node.if_false))
        if hasattr(node, 'selectors') or hasattr(node, 'prefix_operators'):
            prefix_str = _get_prefix_str(node.prefix_operators)
            selector_str = _get_selector_str(node.selectors)
            return "%s(%s)%s" % (prefix_str, base_str, selector_str)
        else:
            return base_str
    elif isinstance(node, tree.BinaryOperation):
        if hasattr(node, 'prefix_operators') or hasattr(node, 'selectors'): # prefixes in binary operations aren't documented but exist
            prefix_str = _get_prefix_str(node.prefix_operators)
            selector_str = _get_selector_str(node.selectors)
            return "%s(%s %s %s)%s" % (prefix_str, unparse(node.operandl), node.operator, unparse(node.operandr), selector_str)
        else:
            return "%s %s %s" % (unparse(node.operandl), node.operator, unparse(node.operandr))
    elif isinstance(node, tree.Cast):
        if hasattr(node, 'prefix_operators'): # prefixes in Cast operators are something I made up...
            prefix_str = _get_prefix_str(node.prefix_operators)
        else:
            prefix_str = ""
        if hasattr(node, 'selectors'): # casts can have selectors
            selector_str = _get_selector_str(node.selectors)
        else:
            selector_str = ""
        if len(prefix_str) > 0 or len(selector_str) > 0:
            return "%s((%s) %s)%s" % (prefix_str, unparse(node.type), unparse(node.expression), selector_str)
        else:
            return "(%s) %s" % (unparse(node.type), unparse(node.expression))
    elif isinstance(node, tree.LambdaExpression):
        param_str = "(" + ", ".join(unparse(param) for param in node.parameters) + ")"
        if isinstance(node.body, tree.Node):
            body_str = unparse(node.body)
        else:
            assert type(node.body) == list
            body_str = "{" + "; ".join(unparse(stmt) for stmt in node.body) + "}"
        return "%s -> %s" % (param_str, body_str)

    elif isinstance(node, tree.Literal):
        prefix_str = _get_prefix_str(node.prefix_operators)
        postfix_str = _get_postfix_str(node.postfix_operators)
        selector_str = _get_selector_str(node.selectors)
        return prefix_str + node.value + selector_str + postfix_str
    elif isinstance(node, tree.This):
        prefix_str = _get_prefix_str(node.prefix_operators)
        postfix_str = _get_postfix_str(node.postfix_operators)
        qualifier_str = _get_qualifier_str(node.qualifier)
        selector_str = _get_selector_str(node.selectors)
        return prefix_str + qualifier_str + "this" + selector_str + postfix_str
    elif isinstance(node, tree.MemberReference):
        if node.qualifier is not None:
            core_name = node.member if len(node.qualifier) == 0 else node.qualifier + "." + node.member
        else:
            core_name = node.member
        prefix_str = _get_prefix_str(node.prefix_operators)
        postfix_str = _get_postfix_str(node.postfix_operators)
        selector_str = _get_selector_str(node.selectors)
        return prefix_str + core_name + postfix_str + selector_str
    elif isinstance(node, tree.ExplicitConstructorInvocation):
        return "this(%s)" % (", ".join(unparse(e) for e in node.arguments))
    elif isinstance(node, tree.SuperConstructorInvocation):
        qualifier_str = _get_qualifier_str(node.qualifier)
        return "%ssuper(%s)" % (qualifier_str, ", ".join(unparse(e) for e in node.arguments))
    elif isinstance(node, tree.MethodInvocation):
        prefix_str = _get_prefix_str(node.prefix_operators)
        postfix_str = _get_postfix_str(node.postfix_operators)
        qualifier_str = _get_qualifier_str(node.qualifier)
        if node.type_arguments is not None and len(node.type_arguments) > 0:
            # assert node.qualifier is not None and len(node.qualifier) > 0
            typep_str = "<%s>" % ", ".join(unparse(t) for t in node.type_arguments) # generic method handling
        else:
            typep_str = ""
        mname = qualifier_str + typep_str + node.member
        args = ", ".join(unparse(arg) for arg in node.arguments)
        selector_str = _get_selector_str(node.selectors)
        return prefix_str + mname + "(" + args + ")" + selector_str + postfix_str
    elif isinstance(node, tree.SuperMethodInvocation):
        prefix_str = _get_prefix_str(node.prefix_operators)
        args = ", ".join(unparse(arg) for arg in node.arguments)
        selector_str = _get_selector_str(node.selectors)
        return prefix_str + "super." + node.member + "(" + args + ")" + selector_str
    elif isinstance(node, tree.ArraySelector):
        return "[%s]" % unparse(node.index)
    elif isinstance(node, tree.ClassReference):
        prefix_str = _get_prefix_str(node.prefix_operators)
        qualifier_str = _get_qualifier_str(node.qualifier)
        selector_str = _get_selector_str(node.selectors)
        type_str = "void" if isinstance(node, tree.VoidClassReference) else unparse(node.type)
        return "%s%s%s.class%s" % (prefix_str, qualifier_str, type_str, selector_str)

    elif isinstance(node, tree.ArrayCreator):
        selector_str = _get_selector_str(node.selectors)
        dim_str = ''.join([f'[{unparse(e)}]' if e is not None else '[]' for e in node.dimensions])
        init_str = unparse(node.initializer) if node.initializer is not None else ''
        if len(selector_str) == 0:
            return f'new {unparse(node.type)}{dim_str}{init_str}'
        else:
            return f'(new {unparse(node.type)}{dim_str}{init_str}){selector_str}'
    elif isinstance(node, tree.ClassCreator):
        if hasattr(node, 'prefix_operators'):
            prefix_str = _get_prefix_str(node.prefix_operators)
        else:
            prefix_str = ""
        args = ", ".join(unparse(arg) for arg in node.arguments)
        selector_str = _get_selector_str(node.selectors)
        body_str = _get_body_str(node.body, indent)
        return "%snew %s(%s)%s%s" % (prefix_str, unparse(node.type), args, selector_str, body_str)
    elif isinstance(node, tree.InnerClassCreator):
        qualifier_str = _get_qualifier_str(node.qualifier)
        args = ", ".join(unparse(arg) for arg in node.arguments)
        return "%snew %s(%s)" % (qualifier_str, unparse(node.type), args)
    
    elif isinstance(node, tree.EnumBody):
        constants_str = ",\n".join(indent_str + unparse(c, indent=indent) for c in node.constants)
        declarations_str = "\n".join(unparse(d, indent=indent) for d in node.declarations)
        return constants_str + "\n" + declarations_str
    elif isinstance(node, tree.EnumConstantDeclaration):
        if node.arguments is None or len(node.arguments) == 0:
            arg_str = ""
        else:
            arg_str = "(%s)" % ", ".join(unparse(a) for a in node.arguments)
        annotation_str = _get_annotation_str(node.annotations, indent_str)
        body_str = _get_body_str(node.body, indent)
        return annotation_str+node.name+arg_str+body_str
    elif isinstance(node, tree.AnnotationMethod):
        annotation_str = _get_annotation_str(node.annotations, indent_str)
        modifier_str = _get_modifier_str(node.modifiers, trailing_space=True)
        default_str = " default %s" % unparse(node.default) if node.default is not None else ""
        return "%s%s%s%s %s()%s;" % (annotation_str, indent_str, modifier_str, unparse(node.return_type), node.name, default_str)
    
    ## Weird fellows
    elif isinstance(node, tree.Statement):
        # only-semicolon lines?
        return ";"
    elif isinstance(node, list):
        # seems to be a static block? I'm unsure what this is. (found in SegmentedTimelineTests.java of Chart)
        statement_str = "\n".join(unparse(stmt, indent=indent+1) for stmt in node)
        return "%s {\n%s\n%s}" % (indent_str, statement_str, indent_str)
    else:
        raise NotImplementedError("Unparser for %s is not implemented at location %s" % (type(node), node._position))

