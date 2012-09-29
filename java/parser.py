
import sys
import util

import tree
from tokenizer import (
    EndOfInput, Keyword, Modifier, BasicType, Identifier,
    Annotation, Literal, Operator, JavaToken
    )

ENABLE_TRACE_SUPPORT = True
DEBUG = False

# ------------------------------------------------------------------------------
# ---- Helper methods ----

def is_annotation(tokens, i=0):
    """ Returns true if the position is the start of an annotation application
    (as opposed to an annotation declaration)

    """

    return (isinstance(tokens.look(i), Annotation) and
            not tokens.look(i + 1).value == 'interface')

def is_annotation_declaration(tokens, i=0):
    """ Returns true if the position is the start of an annotation application
    (as opposed to an annotation declaration)

    """

    return (isinstance(tokens.look(i), Annotation) and
            tokens.look(i + 1).value == 'interface')

def parse_debug(method):
    global ENABLE_TRACE_SUPPORT

    if ENABLE_TRACE_SUPPORT:
        global _debug_level
        _debug_level = 0

        def _method(tokens):
            global DEBUG, _debug_level

            if DEBUG:
                depth = "{0:2}".format(_debug_level)
                token = unicode(tokens.look())
                start_value = tokens.look().value
                name = method.__name__
                sep = ("-" * _debug_level)
                e_message = ""

                print "{0} {1}> {2}({3})".format(depth, sep, name, token)

                _debug_level += 1

                try:
                    r = method(tokens)

                except JavaSyntaxError as e:
                    e_message = e.description
                    raise

                except Exception as e:
                    e_message = unicode(e)
                    raise

                finally:
                    token = unicode(tokens.last())
                    print "{0} <{1} {2}({3}, {4}) {5}".format(
                        depth, sep, name, start_value, token, e_message)
                    _debug_level -= 1
            else:
                _debug_level += 1
                try:
                    r = method(tokens)
                finally:
                    _debug_level -= 1

            return r

        return _method

    else:
        return method

def accept(tokens, *accepts):
    last = None

    if len(accepts) == 0:
        raise JavaParserError("Missing acceptable values")

    for accept in accepts:
        token = tokens.next()

        if isinstance(accept, basestring) and not token.value == accept:
            raise JavaSyntaxError("Expected '{0}'".format(accept))
        elif isinstance(accept, type) and not isinstance(token, accept):
            raise JavaSyntaxError("Expected {0}".format(accept.__name__))

        last = token

    return last.value

def would_accept(tokens, *accepts):
    if len(accepts) == 0:
        raise JavaParserError("Missing acceptable values")

    for i, accept in enumerate(accepts):
        token = tokens.look(i)

        if isinstance(accept, basestring) and not token.value == accept:
            return False
        elif isinstance(accept, type) and not isinstance(token, accept):
            return False

    return True

def try_accept(tokens, *accepts):
    if len(accepts) == 0:
        raise JavaParserError("Missing acceptable values")

    for i, accept in enumerate(accepts):
        token = tokens.look(i)

        if isinstance(accept, basestring) and not token.value == accept:
            return False
        elif isinstance(accept, type) and not isinstance(token, accept):
            return False

    for i in range(0, len(accepts)):
        tokens.next()

    return True

def build_binary_operation(parts, start_level=0):
    if len(parts) == 1:
        return parts[0]

    precedence = [ set(('||',)),
                   set(('&&',)),
                   set(('|',)),
                   set(('^',)),
                   set(('&',)),
                   set(('==', '!=')),
                   set(('<', '>', '>=', '<=', 'instanceof')),
                   set(('<<', '>>', '>>>')),
                   set(('+', '-')),
                   set(('*', '/', '%')) ]

    for level in range(start_level, len(precedence)):
        for i in xrange(len(parts) - 2, 0, -2):
            if parts[i] in precedence[level]:
                operator = parts[i]
                operandl = build_binary_operation(parts[:i], level)
                operandr = build_binary_operation(parts[i+1:], level + 1)

                return tree.BinaryOperation(operator=operator,
                                           operandl=operandl,
                                           operandr=operandr)

    raise JavaParserError("Failed to build binary operation")

# ------------------------------------------------------------------------------
# ---- Parsing exception ----

class JavaParserBaseException(Exception):
    def __init__(self, message=''):
        super(JavaParserBaseException, self).__init__(message)

class JavaSyntaxError(JavaParserBaseException):
    def __init__(self, description, at=None):
        super(JavaSyntaxError, self).__init__()

        self.description = description
        self.at = at

class JavaParserError(JavaParserBaseException):
    pass

# ------------------------------------------------------------------------------
# ---- Parsing methods ----

# ------------------------------------------------------------------------------
# -- Identifiers --

@parse_debug
def parse_identifier(tokens):
    return accept(tokens, Identifier)

@parse_debug
def parse_qualified_identifier(tokens):
    qualified_identifier = list()

    while True:
        identifier = parse_identifier(tokens)
        qualified_identifier.append(identifier)

        if not try_accept(tokens, '.'):
            break

    return '.'.join(qualified_identifier)

@parse_debug
def parse_qualified_identifier_list(tokens):
    qualified_identifiers = list()

    while True:
        qualified_identifier = parse_qualified_identifier(tokens)
        qualified_identifiers.append(qualified_identifier)

        if not try_accept(tokens, ','):
            break

    return qualified_identifiers

# ------------------------------------------------------------------------------
# -- Top level units --

@parse_debug
def parse_compilation_unit(tokens):
    package = None
    package_annotations = None
    import_declarations = list()
    type_declarations = list()

    tokens.push_marker()
    if is_annotation(tokens):
        package_annotations = parse_annotations(tokens)

    if try_accept(tokens, 'package'):
        tokens.pop_marker(False)
        package_name = parse_qualified_identifier(tokens)
        package = tree.PackageDeclaration(annotations=package_annotations,
                                          name=package_name)
        accept(tokens, ';')
    else:
        tokens.pop_marker(True)
        package_annotations = None

    while would_accept(tokens, 'import'):
        import_declaration = parse_import_declaration(tokens)
        import_declarations.append(import_declaration)

    while not isinstance(tokens.look(), EndOfInput):
        try:
            type_declaration = parse_type_declaration(tokens)
        except StopIteration:
            raise JavaSyntaxError("Unexpected end of input")

        if type_declaration:
            type_declarations.append(type_declaration)

    return tree.CompilationUnit(package=package,
                               imports=import_declarations,
                               types=type_declarations)

@parse_debug
def parse_import_declaration(tokens):
    qualified_identifier = list()
    static = False
    import_all = False

    accept(tokens, 'import')

    if try_accept(tokens, 'static'):
        static = True

    while True:
        identifier = parse_identifier(tokens)
        qualified_identifier.append(identifier)

        if try_accept(tokens, '.'):
            if try_accept(tokens, '*'):
                accept(tokens, ';')
                import_all = True
                break

        else:
            accept(tokens, ';')
            break

    return tree.Import(path='.'.join(qualified_identifier),
                       static=static,
                       wildcard=import_all)

@parse_debug
def parse_type_declaration(tokens):
    if try_accept(tokens, ';'):
        return None
    else:
        return parse_class_or_interface_declaration(tokens)

@parse_debug
def parse_class_or_interface_declaration(tokens):
    modifiers, annotations = parse_modifiers(tokens)
    type_declaration = None

    token = tokens.look()
    if token.value == 'class':
        type_declaration = parse_normal_class_declaration(tokens)
    elif token.value == 'enum':
        type_declaration = parse_enum_declaration(tokens)
    elif token.value == 'interface':
        type_declaration = parse_normal_interface_declaration(tokens)
    elif is_annotation_declaration(tokens):
        type_declaration = parse_annotation_type_declaration(tokens)
    else:
        raise JavaSyntaxError("Expected type declaration")

    type_declaration.modifiers = modifiers
    type_declaration.annotations = annotations

    return type_declaration

@parse_debug
def parse_normal_class_declaration(tokens):
    name = None
    type_params = None
    extends = None
    implements = None
    body = None

    accept(tokens, 'class')

    name = parse_identifier(tokens)

    if would_accept(tokens, '<'):
        type_params = parse_type_parameters(tokens)

    if try_accept(tokens, 'extends'):
        extends = parse_type(tokens)

    if try_accept(tokens, 'implements'):
        implements = parse_type_list(tokens)

    body = parse_class_body(tokens)

    return tree.ClassDeclaration(name=name,
                                type_parameters=type_params,
                                extends=extends,
                                implements=implements,
                                body=body)

@parse_debug
def parse_enum_declaration(tokens):
    name = None
    implements = None
    body = None

    accept(tokens, 'enum')
    name = parse_identifier(tokens)

    if try_accept(tokens, 'implements'):
        implements = parse_type_list(tokens)

    body = parse_enum_body(tokens)

    return tree.EnumDeclaration(name=name,
                               implements=implements,
                               body=body)

@parse_debug
def parse_normal_interface_declaration(tokens):
    name = None
    type_parameters = None
    extends = None
    body = None

    accept(tokens, 'interface')
    name = parse_identifier(tokens)

    if would_accept(tokens, '<'):
        type_parameters = parse_type_parameters(tokens)

    if try_accept(tokens, 'extends'):
        extends = parse_type_list(tokens)

    body = parse_interface_body(tokens)

    return tree.InterfaceDeclaration(name=name,
                                    type_parameters=type_parameters,
                                    extends=extends,
                                    body=body)

@parse_debug
def parse_annotation_type_declaration(tokens):
    name = None
    body = None

    accept(tokens, '@', 'interface')

    name = parse_identifier(tokens)
    body = parse_annotation_type_body(tokens)

    return tree.AnnotationDeclaration(name=name,
                                     body=body)

# ------------------------------------------------------------------------------
# -- Types --

@parse_debug
def parse_type(tokens):
    java_type = None

    if isinstance(tokens.look(), BasicType):
        java_type = parse_basic_type(tokens)
    elif isinstance(tokens.look(), Identifier):
        java_type = parse_reference_type(tokens)
    else:
        raise JavaSyntaxError("Expected type")

    java_type.dimensions = parse_array_dimension(tokens)

    return java_type

@parse_debug
def parse_basic_type(tokens):
    return tree.BasicType(name=accept(tokens, BasicType))

@parse_debug
def parse_reference_type(tokens):
    reference_type = tree.ReferenceType()
    tail = reference_type

    while True:
        tail.name = parse_identifier(tokens)

        if would_accept(tokens, '<'):
            tail.arguments = parse_type_arguments(tokens)

        if try_accept(tokens, '.'):
            tail.sub_type = tree.ReferenceType()
            tail = tail.sub_type
        else:
            break

    return reference_type

@parse_debug
def parse_type_arguments(tokens):
    type_arguments = list()

    accept(tokens, '<')

    while True:
        type_argument = parse_type_argument(tokens)
        type_arguments.append(type_argument)

        if try_accept(tokens, '>'):
            break

        accept(tokens, ',')

    return type_arguments

@parse_debug
def parse_type_argument(tokens):
    pattern_type = None
    base_type = None

    if try_accept(tokens, '?'):
        wildcard = True

        if tokens.look().value in ('extends', 'super'):
            pattern_type = tokens.next().value
        else:
            return tree.TypeArgument(pattern_type='?')

    if would_accept(tokens, BasicType):
        base_type = parse_basic_type(tokens)
        accept(tokens, '[', ']')
        base_type.dimensions = [None]
    else:
        base_type = parse_reference_type(tokens)
        base_type.dimensions = []

    base_type.dimensions += parse_array_dimension(tokens)

    return tree.TypeArgument(type=base_type,
                            pattern_type=pattern_type)

@parse_debug
def parse_nonwildcard_type_arguments(tokens):
    accept(tokens, '<')
    type_arguments = parse_type_list(tokens)
    accept(tokens, '>')

    return [tree.TypeArgument(type=t) for t in type_arguments]

@parse_debug
def parse_type_list(tokens):
    types = list()

    while True:
        if would_accept(tokens, BasicType):
            base_type = parse_basic_type(tokens)
            accept(tokens, '[', ']')
            base_type.dimensions = [None]
        else:
            base_type = parse_reference_type(tokens)
            base_type.dimensions = []

        base_type.dimensions += parse_array_dimension(tokens)
        types.append(base_type)

        if not try_accept(tokens, ','):
            break

    return types

@parse_debug
def parse_type_arguments_or_diamond(tokens):
    if try_accept(tokens, '<', '>'):
        return list()
    else:
        return parse_type_arguments(tokens)

@parse_debug
def parse_nonwildcard_type_arguments_or_diamond(tokens):
    if try_accept(tokens, '<', '>'):
        return list()
    else:
        return parse_nonwildcard_type_arguments(tokens)

@parse_debug
def parse_type_parameters(tokens):
    type_parameters = list()

    accept(tokens, '<')

    while True:
        type_parameter = parse_type_parameter(tokens)
        type_parameters.append(type_parameter)

        if try_accept(tokens, '>'):
            break
        else:
            accept(tokens, ',')

    return type_parameters

@parse_debug
def parse_type_parameter(tokens):
    identifier = parse_identifier(tokens)
    extends = None

    if try_accept(tokens, 'extends'):
        extends = list()

        while True:
            reference_type = parse_reference_type(tokens)
            extends.append(reference_type)

            if not try_accept(tokens, '&'):
                break

    return tree.TypeParameter(name=identifier,
                             extends=extends)

@parse_debug
def parse_array_dimension(tokens):
    array_dimension = 0

    while try_accept(tokens, '[', ']'):
        array_dimension += 1

    return [None] * array_dimension

# ------------------------------------------------------------------------------
# -- Annotations and modifiers --

@parse_debug
def parse_modifiers(tokens):
    annotations = list()
    modifiers = set()

    while True:
        if would_accept(tokens, Modifier):
            modifiers.add(accept(tokens, Modifier))

        elif is_annotation(tokens):
            annotation = parse_annotation(tokens)
            annotations.append(annotation)

        else:
            break

    return (modifiers, annotations)

@parse_debug
def parse_annotations(tokens):
    annotations = list()

    while True:
        annotation = parse_annotation(tokens)
        annotations.append(annotation)

        if not is_annotation(tokens):
            break

    return annotations

@parse_debug
def parse_annotation(tokens):
    qualified_identifier = None
    annotation_element = None

    accept(tokens, '@')
    qualified_identifier = parse_qualified_identifier(tokens)

    if try_accept(tokens, '('):
        if not would_accept(tokens, ')'):
            annotation_element = parse_annotation_element(tokens)
        accept(tokens, ')')

    return tree.Annotation(annotation=qualified_identifier,
                          element=annotation_element)

@parse_debug
def parse_annotation_element(tokens):
    if would_accept(tokens, Identifier, '='):
        return parse_element_value_pairs(tokens)
    else:
        return parse_element_value(tokens)

@parse_debug
def parse_element_value_pairs(tokens):
    pairs = list()

    while True:
        pair = parse_element_value_pair(tokens)
        pairs.append(pair)

        if not try_accept(tokens, ','):
            break

    return pairs

@parse_debug
def parse_element_value_pair(tokens):
    identifier = parse_identifier(tokens)
    accept(tokens, '=')
    value = parse_element_value(tokens)

    return tree.ElementValuePair(name=identifier,
                                value=value)

@parse_debug
def parse_element_value(tokens):
    if is_annotation(tokens):
        return parse_annotation(tokens)

    elif would_accept(tokens, '{'):
        return parse_element_value_array_initializer(tokens)

    else:
        return parse_expressionl(tokens)

@parse_debug
def parse_element_value_array_initializer(tokens):
    accept(tokens, '{')

    if try_accept(tokens, '}'):
        return list()

    element_values = parse_element_values(tokens)
    try_accept(tokens, ',')
    accept(tokens, '}')

    return tree.ElementArrayValue(values=element_values)

@parse_debug
def parse_element_values(tokens):
    element_values = list()

    while True:
        element_value = parse_element_value(tokens)
        element_values.append(element_value)

        if would_accept(tokens, '}') or would_accept(tokens, ',', '}'):
            break

        accept(tokens, ',')

    return element_value

# ------------------------------------------------------------------------------
# -- Class body --

@parse_debug
def parse_class_body(tokens):
    declarations = list()

    accept(tokens, '{')

    while not would_accept(tokens, '}'):
        declaration = parse_class_body_declaration(tokens)
        if declaration:
            declarations.append(declaration)

    accept(tokens, '}')

    return declarations

@parse_debug
def parse_class_body_declaration(tokens):
    token = tokens.look()

    if try_accept(tokens, ';'):
        return None

    elif would_accept(tokens, 'static', '{'):
        accept(tokens, 'static')
        return parse_block(tokens)

    elif would_accept(tokens, '{'):
        return parse_block(tokens)

    else:
        return parse_member_declaration(tokens)

@parse_debug
def parse_member_declaration(tokens):
    modifiers, annotations = parse_modifiers(tokens)
    member = None

    token = tokens.look()
    if try_accept(tokens, 'void'):
        method_name = parse_identifier(tokens)
        member = parse_void_method_declarator_rest(tokens)
        member.name = method_name

    elif token.value == '<':
        member = parse_generic_method_or_constructor_declaration(tokens)

    elif token.value == 'class':
        member = parse_normal_class_declaration(tokens)

    elif token.value == 'enum':
        member = parse_enum_declaration(tokens)

    elif token.value == 'interface':
        member = parse_normal_interface_declaration(tokens)

    elif is_annotation_declaration(tokens):
        member = parse_annotation_type_declaration(tokens)

    elif would_accept(tokens, Identifier, '('):
        constructor_name = parse_identifier(tokens)
        member = parse_constructor_declarator_rest(tokens)
        member.name = constructor_name

    else:
        member = parse_method_or_field_declaraction(tokens)

    member.modifiers = modifiers
    member.annotations = annotations

    return member

@parse_debug
def parse_method_or_field_declaraction(tokens):
    member_type = parse_type(tokens)
    member_name = parse_identifier(tokens)

    member = parse_method_or_field_rest(tokens)

    if isinstance(member, tree.MethodDeclaration):
        member_type.dimensions += member.return_type.dimensions

        member.name = member_name
        member.return_type = member_type
    else:
        member.type = member_type
        member.declarators[0].name = member_name

    return member

@parse_debug
def parse_method_or_field_rest(tokens):
    if would_accept(tokens, '('):
        return parse_method_declarator_rest(tokens)
    else:
        rest = parse_field_declarators_rest(tokens)
        accept(tokens, ';')
        return rest

@parse_debug
def parse_field_declarators_rest(tokens):
    array_dimension, initializer = parse_variable_declarator_rest(tokens)
    declarators = [tree.VariableDeclarator(dimensions=array_dimension,
                                           initializer=initializer)]

    while try_accept(tokens, ','):
        declarator = parse_variable_declarator(tokens)
        declarators.append(declarator)

    return tree.FieldDeclaration(declarators=declarators)

@parse_debug
def parse_method_declarator_rest(tokens):
    formal_parameters = parse_formal_parameters(tokens)
    additional_dimensions = parse_array_dimension(tokens)
    throws = None
    body = None

    if try_accept(tokens, 'throws'):
        throws = parse_qualified_identifier_list(tokens)

    if would_accept(tokens, '{'):
        body = parse_block(tokens)
    else:
        accept(tokens, ';')

    return tree.MethodDeclaration(parameters=formal_parameters,
                                 throws=throws,
                                 body=body,
                                 return_type=tree.Type(dimensions=additional_dimensions))

@parse_debug
def parse_void_method_declarator_rest(tokens):
    formal_parameters = parse_formal_parameters(tokens)
    throws = None
    body = None

    if try_accept(tokens, 'throws'):
        throws = parse_qualified_identifier_list(tokens)

    if would_accept(tokens, '{'):
        body = parse_block(tokens)
    else:
        accept(tokens, ';')

    return tree.MethodDeclaration(parameters=formal_parameters,
                                 throws=throws,
                                 body=body)

@parse_debug
def parse_constructor_declarator_rest(tokens):
    formal_parameters = parse_formal_parameters(tokens)
    throws = None
    body = None

    if try_accept(tokens, 'throws'):
        throws = parse_qualified_identifier_list(tokens)

    body = parse_block(tokens)

    return tree.ConstructorDeclaration(parameters=formal_parameters,
                                      throws=throws,
                                      body=body)

@parse_debug
def parse_generic_method_or_constructor_declaration(tokens):
    type_parameters = parse_type_parameters(tokens)
    method = None

    if would_accept(tokens, Identifier, '('):
        constructor_name = parse_identifier(tokens)
        method = parse_constructor_declarator_rest(tokens)
        method.name = constructor_name

    elif try_accept(tokens, 'void'):
        method_name = parse_identifier(tokens)
        method = parse_void_method_declarator_rest(tokens)
        method.name = method_name

    else:
        method_return_type = parse_type(tokens)
        method_name = parse_identifier(tokens)

        method = parse_method_declarator_rest(tokens)

        method_return_type.dimensions += method.return_type.dimensions
        method.return_type = method_return_type
        method.name = method_name

    method.type_parameters = type_parameters
    return method

# ------------------------------------------------------------------------------
# -- Interface body --

@parse_debug
def parse_interface_body(tokens):
    declarations = list()

    accept(tokens, '{')
    while not would_accept(tokens, '}'):
        declaration = parse_interface_body_declaration(tokens)

        if declaration:
            declarations.append(declaration)
    accept(tokens, '}')

    return declarations

@parse_debug
def parse_interface_body_declaration(tokens):
    if try_accept(tokens, ';'):
        return None

    modifiers, annotations = parse_modifiers(tokens)

    declaration = parse_interface_member_declaration(tokens)
    declaration.modifiers = modifiers
    declaration.annotations = annotations

    return declaration

@parse_debug
def parse_interface_member_declaration(tokens):
    declaration = None

    if would_accept(tokens, 'class'):
        declaration = parse_normal_class_declaration(tokens)
    elif would_accept(tokens, 'interface'):
        declaration = parse_normal_interface_declaration(tokens)
    elif would_accept(tokens, 'enum'):
        declaration = parse_enum_declaration(tokens)
    elif is_annotation_declaration(tokens):
        declaration = parse_annotation_type_declaration(tokens)
    elif would_accept(tokens, '<'):
        declaration = parse_interface_generic_method_declarator(tokens)
    elif try_accept(tokens, 'void'):
        method_name = parse_identifier(tokens)
        declaration = parse_void_interface_method_declarator_rest(tokens)
        declaration.name = method_name
    else:
        declaration = parse_interface_method_or_field_declaration(tokens)

    return declaration

@parse_debug
def parse_interface_method_or_field_declaration(tokens):
    java_type = parse_type(tokens)
    name = parse_identifier(tokens)
    member = parse_interface_method_or_field_rest(tokens)
    member.name = name

    if isinstance(member, tree.MethodDeclaration):
        java_type.dimensions += member.return_type.dimensions
        member.return_type = java_type
    else:
        member.type = java_type

    return member

@parse_debug
def parse_interface_method_or_field_rest(tokens):
    rest = None

    if would_accept(tokens, '('):
        rest = parse_interface_method_declarator_rest(tokens)
    else:
        rest = parse_constant_declarators_rest(tokens)
        accept(tokens, ';')

    return rest

@parse_debug
def parse_constant_declarators_rest(tokens):
    array_dimension, initializer = parse_constant_declarator_rest(tokens)
    declarators = [tree.VariableDeclarator(dimensions=array_dimension,
                                           initializer=initializer)]

    while try_accept(tokens, ','):
        declarator = parse_constant_declarator(tokens)
        declarators.append(declarator)

    return tree.ConstantDeclaration(declarators=declarators)

@parse_debug
def parse_constant_declarator_rest(tokens):
    array_dimension = parse_array_dimension(tokens)
    accept(tokens, '=')
    initializer = parse_variable_initializer(tokens)

    return (array_dimension, initializer)

@parse_debug
def parse_constant_declarator(tokens):
    name = parse_identifier(tokens)
    additional_dimension, initializer = parse_constant_declarator_rest(tokens)

    return tree.VariableDeclarator(name=name,
                                   dimensions=additional_dimension,
                                   initializer=initializer)

@parse_debug
def parse_interface_method_declarator_rest(tokens):
    parameters = parse_formal_parameters(tokens)
    array_dimension = parse_array_dimension(tokens)
    throws = None

    if try_accept(tokens, 'throws'):
        throws = parse_qualified_identifier_list(tokens)

    accept(tokens, ';')

    return tree.MethodDeclaration(parameters=parameters,
                                  throws=throws,
                                  return_type=tree.Type(dimensions=array_dimension))

@parse_debug
def parse_void_interface_method_declarator_rest(tokens):
    parameters = parse_formal_parameters(tokens)
    throws = None

    if try_accept(tokens, 'throws'):
        throws = parse_qualified_identifier_list(tokens)

    accept(tokens, ';')

    return tree.MethodDeclaration(parameters=parameters,
                                  throws=throws)

@parse_debug
def parse_interface_generic_method_declarator(tokens):
    type_parameters = parse_type_parameters(tokens)
    return_type = None
    method_name = None
    rest = None

    if not try_accept(tokens, 'void'):
        return_type = parse_type(tokens)

    method_name = parse_identifier(tokens)
    method = parse_interface_method_declarator_rest(tokens)
    method.name = method_name
    method.return_type = return_type
    method.type_parameters = type_parameters

    return method

# ------------------------------------------------------------------------------
# -- Parameters and variables --

@parse_debug
def parse_formal_parameters(tokens):
    formal_parameters = list()

    accept(tokens, '(')

    if try_accept(tokens, ')'):
        return formal_parameters

    while True:
        modifiers, annotations = parse_variable_modifiers(tokens)
        parameter_type = parse_type(tokens)
        varargs = False

        if try_accept(tokens, '...'):
            varargs = True

        parameter_name = parse_identifier(tokens)
        parameter_type.dimensions += parse_array_dimension(tokens)

        parameter = tree.FormalParameter(modifiers=modifiers,
                                        annotations=annotations,
                                        type=parameter_type,
                                        name=parameter_name,
                                        varargs=varargs)

        formal_parameters.append(parameter)

        if varargs:
            # varargs parameter must be the last
            break

        if not try_accept(tokens, ','):
            break

    accept(tokens, ')')

    return formal_parameters

@parse_debug
def parse_variable_modifiers(tokens):
    modifiers = set()
    annotations = list()

    while True:
        if try_accept(tokens, 'final'):
            modifiers.add('final')
        elif is_annotation(tokens):
            annotation = parse_annotation(tokens)
            annotations.append(annotation)
        else:
            break

    return modifiers, annotations

@parse_debug
def parse_variable_declators(tokens):
    declarators = list()

    while True:
        declarator = parse_variable_declator(tokens)
        declarators.append(declarator)

        if not try_accept(tokens, ','):
            break

    return declarators

@parse_debug
def parse_variable_declarators(tokens):
    declarators = list()

    while True:
        declarator = parse_variable_declarator(tokens)
        declarators.append(declarator)

        if not try_accept(tokens, ','):
            break

    return declarators

@parse_debug
def parse_variable_declarator(tokens):
    identifier = parse_identifier(tokens)
    array_dimension, initializer = parse_variable_declarator_rest(tokens)

    return tree.VariableDeclarator(name=identifier,
                                  dimensions=array_dimension,
                                  initializer=initializer)

@parse_debug
def parse_variable_declarator_rest(tokens):
    array_dimension = parse_array_dimension(tokens)
    initializer = None

    if try_accept(tokens, '='):
        initializer = parse_variable_initializer(tokens)

    return (array_dimension, initializer)

@parse_debug
def parse_variable_initializer(tokens):
    if would_accept(tokens, '{'):
        return parse_array_initializer(tokens)
    else:
        return parse_expression(tokens)

@parse_debug
def parse_array_initializer(tokens):
    array_initializer = tree.ArrayInitializer(initializers=list())

    accept(tokens, '{')

    if try_accept(tokens, ','):
        accept(tokens, '}')
        return array_initializer

    if try_accept(tokens, '}'):
        return array_initializer

    while True:
        initializer = parse_variable_initializer(tokens)
        array_initializer.initializers.append(initializer)

        if not would_accept(tokens, '}'):
            accept(tokens, ',')

        if try_accept(tokens, '}'):
            return array_initializer

# ------------------------------------------------------------------------------
# -- Blocks and statements --

@parse_debug
def parse_block(tokens):
    statements = list()

    accept(tokens, '{')

    while not would_accept(tokens, '}'):
        statement = parse_block_statement(tokens)
        statements.append(statement)
    accept(tokens, '}')

    return statements

@parse_debug
def parse_block_statement(tokens):
    if would_accept(tokens, Identifier, ':'):
        # Labeled statement
        return parse_statement(tokens)

    if would_accept(tokens, 'synchronized'):
        return parse_statement(tokens)

    token = None
    found_annotations = False
    i = 0

    # Look past annoatations and modifiers. If we find a modifier that is not
    # 'final' then the statement must be a class or interface declaration
    while True:
        token = tokens.look(i)

        if isinstance(token, Modifier):
            if not token.value == 'final':
                return parse_class_or_interface_declaration(tokens)

        elif is_annotation(tokens, i):
            found_annotations = True

            i += 2
            while tokens.look(i).value == '.':
                i += 2

            if tokens.look(i).value == '(':
                parens = 1
                i += 1

                while parens > 0:
                    token = tokens.look(i)
                    if token.value == '(':
                        parens += 1
                    elif token.value == ')':
                        parens -= 1
                    i += 1
                continue

        else:
            break

        i += 1

    if token.value in ('class', 'enum', 'interface', '@'):
        return parse_class_or_interface_declaration(tokens)

    if found_annotations or isinstance(token, BasicType):
        return parse_local_variable_declaration_statement(tokens)

    # At this point, if the block statement is a variable definition the next
    # token MUST be an identifier, so if it isn't we can conclude the block
    # statement is a normal statement
    if not isinstance(token, Identifier):
        return parse_statement(tokens)

    # We can't easily determine the statement type. Try parsing as a variable
    # declaration first and fall back to a statement
    try:
        with tokens:
            return parse_local_variable_declaration_statement(tokens)
    except JavaSyntaxError:
        return parse_statement(tokens)

@parse_debug
def parse_local_variable_declaration_statement(tokens):
    modifiers, annotations = parse_variable_modifiers(tokens)
    java_type = parse_type(tokens)
    declarators = parse_variable_declarators(tokens)
    accept(tokens, ';')

    var = tree.LocalVariableDeclaration(modifiers=modifiers,
                                       annotations=annotations,
                                       type=java_type,
                                       declarators=declarators)
    return var

@parse_debug
def parse_statement(tokens):
    token = tokens.look()

    if would_accept(tokens, '{'):
        block = parse_block(tokens)
        return tree.BlockStatement(statements=block)

    elif try_accept(tokens, ';'):
        return tree.Statement()

    elif would_accept(tokens, Identifier, ':'):
        identifer = parse_identifier(tokens)
        accept(tokens, ':')

        statement = parse_statement(tokens)
        statement.label = identifer

        return statement

    elif try_accept(tokens, 'if'):
        condition = parse_par_expression(tokens)
        then = parse_statement(tokens)
        else_statement = None

        if try_accept(tokens, 'else'):
            else_statement = parse_statement(tokens)

        return tree.IfStatement(condition=condition,
                               then_statement=then,
                               else_statement=else_statement)

    elif try_accept(tokens, 'assert'):
        condition = parse_expression(tokens)
        value = None

        if try_accept(tokens, ':'):
            value = parse_expression(tokens)

        accept(tokens, ';')

        return tree.AssertStatement(condition=condition,
                                   value=value)

    elif try_accept(tokens, 'switch'):
        switch_expression = parse_par_expression(tokens)
        accept(tokens, '{')
        switch_block = parse_switch_block_statement_groups(tokens)
        accept(tokens, '}')

        return tree.SwitchStatement(expression=switch_expression,
                                   cases=switch_block)

    elif try_accept(tokens, 'while'):
        condition = parse_par_expression(tokens)
        action = parse_statement(tokens)

        return tree.WhileStatement(condition=condition,
                                  body=action)

    elif try_accept(tokens, 'do'):
        action = parse_statement(tokens)
        accept(tokens, 'while')
        condition = parse_par_expression(tokens)
        accept(tokens, ';')

        return tree.DoStatement(condition=condition,
                               body=action)

    elif try_accept(tokens, 'for'):
        accept(tokens, '(')
        for_control = parse_for_control(tokens)
        accept(tokens, ')')
        for_statement = parse_statement(tokens)

        return tree.ForStatement(control=for_control,
                                body=for_statement)

    elif try_accept(tokens, 'break'):
        label = None

        if would_accept(tokens, Identifier):
            label = parse_identifier(tokens)

        accept(tokens, ';')

        return tree.BreakStatement(goto=label)

    elif try_accept(tokens, 'continue'):
        label = None

        if would_accept(tokens, Identifier):
            label = parse_identifier(tokens)

        accept(tokens, ';')

        return tree.ContinueStatement(goto=label)

    elif try_accept(tokens, 'return'):
        value = None

        if not would_accept(tokens, ';'):
            value = parse_expression(tokens)

        accept(tokens, ';')

        return tree.ReturnStatement(expression=value)

    elif try_accept(tokens, 'throw'):
        value = parse_expression(tokens)
        accept(tokens, ';')

        return tree.ThrowStatement(expression=value)

    elif try_accept(tokens, 'synchronized'):
        lock = parse_par_expression(tokens)
        block = parse_block(tokens)

        return tree.SynchronizedStatement(lock=lock,
                                         block=block)

    elif try_accept(tokens, 'try'):
        resource_specification = None
        block = None
        catches = None
        finally_block = None

        if would_accept(tokens, '{'):
            block = parse_block(tokens)

            if would_accept(tokens, 'catch'):
                catches = parse_catches(tokens)

            if try_accept(tokens, 'finally'):
                finally_block = parse_block(tokens)

            if catches == None and finally_block == None:
                raise JavaSyntaxError("Expected catch/finally block")

        else:
            resource_specification = parse_resource_specification(tokens)
            block = parse_block(tokens)

            if would_accept(tokens, 'catch'):
                catches = parse_catches(tokens)

            if try_accept(tokens, 'finally'):
                finally_block = parse_block(tokens)

        return tree.TryStatement(resources=resource_specification,
                                block=block,
                                catches=catches,
                                finally_block=finally_block)

    else:
        expression = parse_expression(tokens)
        accept(tokens, ';')

        return tree.StatementExpression(expression=expression)

# ------------------------------------------------------------------------------
# -- Try / catch --

@parse_debug
def parse_catches(tokens):
    catches = list()

    while True:
        catch = parse_catch_clause(tokens)
        catches.append(catch)

        if not would_accept(tokens, 'catch'):
            break

    return catches

@parse_debug
def parse_catch_clause(tokens):
    accept(tokens, 'catch', '(')

    modifiers, annotations = parse_variable_modifiers(tokens)
    catch_types = list()

    catch_parameter = tree.CatchClauseParameter(types=list())

    while True:
        catch_type = parse_qualified_identifier(tokens)
        catch_parameter.types.append(catch_type)

        if not try_accept(tokens, '|'):
            break
    catch_parameter.name = parse_identifier(tokens)

    accept(tokens, ')')
    block = parse_block(tokens)

    return tree.CatchClause(parameter=catch_parameter,
                           block=block)

@parse_debug
def parse_resource_specification(tokens):
    resources = list()

    accept(tokens, '(')

    while True:
        resource = parse_resource(tokens)
        resources.append(resource)

        if not would_accept(tokens, ')'):
            accept(tokens, ';')

        if try_accept(tokens, ')'):
            break

    return resources

@parse_debug
def parse_resource(tokens):
    modifiers, annotations = parse_variable_modifiers(tokens)
    reference_type = parse_reference_type(tokens)
    reference_type.dimensions = parse_array_dimension(tokens)
    name = parse_identifier(tokens)
    reference_type.dimensions += parse_array_dimension(tokens)
    accept(tokens, '=')
    value = parse_expression(tokens)

    return tree.TryResource(modifiers=modifiers,
                           annotations=annotations,
                           type=reference_type,
                           name=name,
                           value=value)

# ------------------------------------------------------------------------------
# -- Switch and for statements ---

@parse_debug
def parse_switch_block_statement_groups(tokens):
    statement_groups = list()

    while tokens.look().value in ('case', 'default'):
        statement_group = parse_switch_block_statement_group(tokens)
        statement_groups.append(statement_group)

    return statement_groups

@parse_debug
def parse_switch_block_statement_group(tokens):
    labels = list()
    statements = list()

    while True:
        case_type = tokens.next().value
        case_value = None

        if case_type == 'case':
            if would_accept(tokens, Identifier, ':'):
                case_value = parse_identifier(tokens)
            else:
                case_value = parse_expression(tokens)

            labels.append(case_value)
        elif not case_type == 'default':
            raise JavaSyntaxError("Expected switch case")

        accept(tokens, ':')

        if tokens.look().value not in ('case', 'default'):
            break

    while tokens.look().value not in ('case', 'default', '}'):
        statement = parse_block_statement(tokens)
        statements.append(statement)

    return tree.SwitchStatementCase(case=labels,
                                   statements=statements)

@parse_debug
def parse_for_control(tokens):
    # Try for_var_control and fall back to normal three part for control

    try:
        with tokens:
            return parse_for_var_control(tokens)
    except JavaSyntaxError:
        pass

    init = None
    if not would_accept(tokens, ';'):
        init = parse_for_init_or_update(tokens)

    accept(tokens, ';')

    condition = None
    if not would_accept(tokens, ';'):
        condition = parse_expression(tokens)

    accept(tokens, ';')

    update = None
    if not would_accept(tokens, ')'):
        update = parse_for_init_or_update(tokens)

    return tree.ForControl(init=init,
                          condition=condition,
                          update=update)

@parse_debug
def parse_for_var_control(tokens):
    modifiers, annotations = parse_modifiers(tokens)
    var_type = parse_type(tokens)
    var_name = parse_identifier(tokens)
    var_type.dimensions += parse_array_dimension(tokens)

    var = tree.VariableDeclaration(modifiers=modifiers,
                                  annotations=annotations,
                                  type=var_type)

    rest = parse_for_var_control_rest(tokens)

    if isinstance(rest, tree.Expression):
        var.declarators = [tree.VariableDeclarator(name=var_name)]
        return tree.EnhancedForControl(var=var,
                                      iterable=rest)
    else:
        declarators, condition, update = rest
        declarators[0].name = var_name
        var.declarators = declarators
        return tree.ForControl(init=var,
                              condition=condition,
                              update=update)

@parse_debug
def parse_for_var_control_rest(tokens):
    if try_accept(tokens, ':'):
        expression = parse_expression(tokens)
        return expression

    declarators = None
    if not would_accept(tokens, ';'):
        declarators = parse_for_variable_declarator_rest(tokens)
    accept(tokens, ';')

    condition = None
    if not would_accept(tokens, ';'):
        condition = parse_expression(tokens)
    accept(tokens, ';')

    update = None
    if not would_accept(tokens, ')'):
        update = parse_for_init_or_update(tokens)

    return (declarators, condition, update)

@parse_debug
def parse_for_variable_declarator_rest(tokens):
    initializer = None

    if try_accept(tokens, '='):
        initializer = parse_variable_initializer(tokens)

    declarators = [tree.VariableDeclarator(initializer=initializer)]

    while try_accept(tokens, ','):
        declarator = parse_variable_declarator(tokens)
        declarators.append(declarator)

    return declarators

@parse_debug
def parse_for_init_or_update(tokens):
    expressions = list()

    while True:
        expression = parse_expression(tokens)
        expressions.append(expression)

        if not try_accept(tokens, ','):
            break

    return expressions

# ------------------------------------------------------------------------------
# -- Expressions --

@parse_debug
def parse_expression(tokens):
    expressionl = parse_expressionl(tokens)
    assignment_type = None
    assignment_expression = None

    if tokens.look().value in Operator.ASSIGNMENT:
        assignment_type = tokens.next().value
        assignment_expression = parse_expression(tokens)
        return tree.Assignment(expressionl=expressionl,
                              type=assignment_type,
                              value=assignment_expression)
    else:
        return expressionl

@parse_debug
def parse_expressionl(tokens):
    expression_2 = parse_expression_2(tokens)
    is_ternary = False
    true_expression = None
    false_expression = None

    if try_accept(tokens, '?'):
        is_ternary = True
        true_expression = parse_expression(tokens)
        accept(tokens, ':')
        false_expression = parse_expressionl(tokens)

        return tree.TernaryExpression(condition=expression_2,
                                     if_true=true_expression,
                                     if_false=false_expression)

    return expression_2

@parse_debug
def parse_expression_2(tokens):
    expression_3 = parse_expression_3(tokens)
    expression_2_rest = None

    token = tokens.look()
    if token.value in Operator.INFIX or token.value == 'instanceof':
        parts = parse_expression_2_rest(tokens)
        parts.insert(0, expression_3)
        return build_binary_operation(parts)

    return expression_3

@parse_debug
def parse_expression_2_rest(tokens):
    parts = list()

    token = tokens.look()
    while token.value in Operator.INFIX or token.value == 'instanceof':
        if try_accept(tokens, 'instanceof'):
            comparison_type = parse_type(tokens)
            parts.extend(('instanceof', comparison_type))
        else:
            operator = parse_infix_operator(tokens)
            expression = parse_expression_3(tokens)
            parts.extend((operator, expression))

        token = tokens.look()

    return parts

# ------------------------------------------------------------------------------
# -- Expression operators --

@parse_debug
def parse_expression_3(tokens):
    prefix_operators = list()

    while tokens.look().value in Operator.PREFIX:
        prefix_operators.append(tokens.next().value)

    if would_accept(tokens, '('):
        try:
            with tokens:
                accept(tokens, '(')
                cast_target = parse_type(tokens)
                accept(tokens, ')')
                expression = parse_expression_3(tokens)

                return tree.Cast(type=cast_target,
                                expression=expression)
        except JavaSyntaxError:
            pass

    primary = parse_primary(tokens)
    primary.prefix_operators = prefix_operators
    primary.selectors = list()
    primary.postfix_operators = list()

    token = tokens.look()
    while token.value in '[.':
        selector = parse_selector(tokens)
        primary.selectors.append(selector)

        token = tokens.look()

    while token.value in Operator.POSTFIX:
        primary.postfix_operators.append(tokens.next().value)
        token = tokens.look()

    return primary

@parse_debug
def parse_infix_operator(tokens):
    operator = accept(tokens, Operator)

    if not operator in Operator.INFIX:
        raise JavaSyntaxError("Expected infix operator")

    if operator == '>' and try_accept(tokens, '>'):
        operator = '>>'

        if try_accept(tokens, '>'):
            operator = '>>>'

    return operator

# ------------------------------------------------------------------------------
# -- Primary expressions --

@parse_debug
def parse_primary(tokens):
    token = tokens.look()

    if isinstance(token, Literal):
        return parse_literal(tokens)

    elif token.value == '(':
        return parse_par_expression(tokens)

    elif try_accept(tokens, 'this'):
        arguments = None

        if would_accept(tokens, '('):
            arguments = parse_arguments(tokens)
            return tree.ExplicitConstructorInvocation(arguments=arguments)

        return tree.This()

    elif try_accept(tokens, 'super'):
        super_suffix = parse_super_suffix(tokens)
        return super_suffix

    elif try_accept(tokens, 'new'):
        return parse_creator(tokens)

    elif token.value == '<':
        type_arguments = parse_nonwildcard_type_arguments(tokens)

        if try_accept(tokens, 'this'):
            arguments = parse_arguments(tokens)
            return tree.ExplicitConstructorInvocation(type_arguments=type_arguments,
                                                     arguments=arguments)
        else:
            invocation = parse_explicit_generic_invocation_suffix(tokens)
            invocation.type_arguments = type_arguments

            return invocation

    elif isinstance(token, Identifier):
        qualified_identifier = [parse_identifier(tokens)]

        while would_accept(tokens, '.', Identifier):
            accept(tokens, '.')
            identifier = parse_identifier(tokens)
            qualified_identifier.append(identifier)

        identifier_suffix = parse_identifier_suffix(tokens)

        if isinstance(identifier_suffix, (tree.MemberReference, tree.MethodInvocation)):
            # Take the last identifer as the member and leave the rest for the qualifier
            identifier_suffix.member = qualified_identifier.pop()

        identifier_suffix.qualifier = '.'.join(qualified_identifier)

        return identifier_suffix

    elif isinstance(token, BasicType):
        base_type = parse_basic_type(tokens)
        base_type.dimensions = parse_array_dimension(tokens)
        accept(tokens, '.', 'class')

        return tree.ClassReference(type=base_type)

    elif try_accept(tokens, 'void'):
        accept(tokens, '.', 'class')
        return tree.VoidClassReference()

    raise JavaSyntaxError("Expected expression")

@parse_debug
def parse_literal(tokens):
    literal = accept(tokens, Literal)
    return tree.Literal(value=literal)

@parse_debug
def parse_par_expression(tokens):
    accept(tokens, '(')
    expression = parse_expression(tokens)
    accept(tokens, ')')

    return expression

@parse_debug
def parse_arguments(tokens):
    expressions = list()

    accept(tokens, '(')

    if try_accept(tokens, ')'):
        return expressions

    while True:
        expression = parse_expression(tokens)
        expressions.append(expression)

        if not try_accept(tokens, ','):
            break

    accept(tokens, ')')

    return expressions

@parse_debug
def parse_super_suffix(tokens):
    identifier = None
    type_arguments = None
    arguments = None

    if try_accept(tokens, '.'):
        if would_accept(tokens, '<'):
            type_arguments = parse_nonwildcard_type_arguments(tokens)

        identifier = parse_identifier(tokens)

        if would_accept(tokens, '('):
            arguments = parse_arguments(tokens)
    else:
        arguments = parse_arguments(tokens)

    if identifier and arguments:
        return tree.SuperMethodInvocation(member=identifier,
                                         arguments=arguments,
                                         type_arguments=type_arguments)
    elif arguments:
        return tree.SuperConstructorInvocation(arguments=arguments)
    else:
        return tree.SuperMemberReference(member=identifier)

@parse_debug
def parse_explicit_generic_invocation_suffix(tokens):
    java_super = False
    identifier = None
    arguments = None

    if try_accept(tokens, 'super'):
        return parse_super_suffix(tokens)
    else:
        identifier = parse_identifier(tokens)
        arguments = parse_arguments(tokens)
        return tree.MethodInvocation(member=identifier,
                                    arguments=arguments)

# ------------------------------------------------------------------------------
# -- Creators --

@parse_debug
def parse_creator(tokens):
    constructor_type_arguments = None

    if would_accept(tokens, BasicType):
        created_name = parse_basic_type(tokens)
        rest = parse_array_creator_rest(tokens)
        rest.type = created_name
        return rest

    if would_accept(tokens, '<'):
        constructor_type_arguments = parse_nonwildcard_type_arguments(tokens)

    created_name = parse_created_name(tokens)

    if would_accept(tokens, '['):
        if constructor_type_arguments:
            raise JavaSyntaxError("Array creator not allowed with generic constructor type arguments")

        rest = parse_array_creator_rest(tokens)
        rest.type = created_name
        return rest
    else:
        arguments, body = parse_class_creator_rest(tokens)
        return tree.ClassCreator(constructor_type_arguments=constructor_type_arguments,
                                type=created_name,
                                arguments=arguments,
                                body=body)

@parse_debug
def parse_created_name(tokens):
    created_name = tree.ReferenceType()
    tail = created_name

    while True:
        tail.name = parse_identifier(tokens)

        if would_accept(tokens, '<'):
            tail.arguments = parse_type_arguments_or_diamond(tokens)

        if try_accept(tokens, '.'):
            tail.sub_type = tree.ReferenceType()
            tail = tail.sub_type
        else:
            break

    return created_name

@parse_debug
def parse_class_creator_rest(tokens):
    arguments = parse_arguments(tokens)
    class_body = None

    if would_accept(tokens, '{'):
        class_body = parse_class_body(tokens)

    return (arguments, class_body)

@parse_debug
def parse_array_creator_rest(tokens):
    if would_accept(tokens, '[', ']'):
        array_dimension = parse_array_dimension(tokens)
        array_initializer = parse_array_initializer(tokens)

        return tree.ArrayCreator(dimensions=array_dimension,
                                initializer=array_initializer)

    else:
        array_dimensions = list()

        while would_accept(tokens, '[') and not would_accept(tokens, '[', ']'):
            accept(tokens, '[')
            expression = parse_expression(tokens)
            array_dimensions.append(expression)
            accept(tokens, ']')

        array_dimensions += parse_array_dimension(tokens)
        return tree.ArrayCreator(dimensions=array_dimensions)

@parse_debug
def parse_identifier_suffix(tokens):
    if try_accept(tokens, '[', ']'):
        array_dimension = [None] + parse_array_dimension(tokens)
        accept(tokens, '.', 'class')
        return tree.ClassReference(type=tree.Type(dimensions=array_dimension))

    elif would_accept(tokens, '('):
        arguments = parse_arguments(tokens)
        return tree.MethodInvocation(arguments=arguments)

    elif try_accept(tokens, '.', 'class'):
        return tree.ClassReference()

    elif try_accept(tokens, '.', 'this'):
        return tree.This()

    elif would_accept(tokens, '.', '<'):
        tokens.next()
        return parse_explicit_generic_invocation(tokens)

    elif try_accept(tokens, '.', 'new'):
        type_arguments = None

        if would_accept(tokens, '<'):
            type_arguments = parse_nonwildcard_type_arguments(tokens)

        inner_creator = parse_inner_creator(tokens)
        inner_creator.constructor_type_arguments = type_arguments

        return inner_creator

    elif would_accept(tokens, '.', 'super', '('):
        accept(tokens, '.', 'super')
        arguments = parse_arguments(tokens)
        return tree.SuperConstructorInvocation(arguments=arguments)

    else:
        return tree.MemberReference()

@parse_debug
def parse_explicit_generic_invocation(tokens):
    type_arguments = parse_nonwildcard_type_arguments(tokens)

    invocation = parse_explicit_generic_invocation_suffix(tokens)
    invocation.type_arguments = type_arguments

    return invocation

@parse_debug
def parse_inner_creator(tokens):
    identifier = parse_identifier(tokens)
    type_arguments = None

    if would_accept(tokens, '<'):
        type_arguments = parse_nonwildcard_type_arguments_or_diamond(tokens)

    java_type = tree.ReferenceType(name=identifier,
                                  arguments=type_arguments)

    arguments, class_body = parse_class_creator_rest(tokens)

    return tree.InnerClassCreator(type=java_type,
                                 arguments=arguments,
                                 body=body)

@parse_debug
def parse_selector(tokens):
    if try_accept(tokens, '['):
        expression = parse_expression(tokens)
        accept(tokens, ']')
        return tree.ArraySelector(index=expression)

    elif try_accept(tokens, '.'):

        token = tokens.look()
        if isinstance(token, Identifier):
            identifier = tokens.next().value
            arguments = None

            if would_accept(tokens, '('):
                arguments = parse_arguments(tokens)

            return tree.MethodInvocation(member=identifier,
                                        arguments=arguments)

        elif would_accept(tokens, '<'):
            return parse_explicit_generic_invocation(tokens)
        elif try_accept(tokens, 'this'):
            return tree.This()
        elif try_accept(tokens, 'super'):
            return parse_super_suffix(tokens)
        elif try_accept(tokens, 'new'):
            type_arguments = None

            if would_accept(tokens, '<'):
                type_arguments = parse_nonwildcard_type_arguments(tokens)

            inner_creator = parse_inner_creator(tokens)
            inner_creator.constructor_type_arguments = type_arguments

            return inner_creator

    raise JavaSyntaxError("Expected selector")

# ------------------------------------------------------------------------------
# -- Enum and annotation body --

@parse_debug
def parse_enum_body(tokens):
    constants = list()
    body_declarations = list()

    accept(tokens, '{')

    if not try_accept(tokens, ','):
        while not (would_accept(tokens, ';') or would_accept(tokens, '}')):
            constant = parse_enum_constant(tokens)
            constants.append(constant)

            if not try_accept(tokens, ','):
                break

    if try_accept(tokens, ';'):
        while not would_accept(tokens, '}'):
            declaration = parse_class_body_declaration(tokens)

            if declaration:
                body_declarations.append(declaration)

    accept(tokens, '}')

    return tree.EnumBody(constants=constants,
                         declarations=body_declarations)

@parse_debug
def parse_enum_constant(tokens):
    annotations = None
    constant_name = None
    arguments = None
    body = None

    if would_accept(tokens, Annotation):
        annotations = parse_annotations(tokens)

    constant_name = parse_identifier(tokens)

    if would_accept(tokens, '('):
        arguments = parse_arguments(tokens)

    if would_accept(tokens, '{'):
        body = parse_class_body(tokens)

    return tree.EnumConstantDeclaration(annotations=annotations,
                                       name=constant_name,
                                       arguments=arguments,
                                       body=body)

@parse_debug
def parse_annotation_type_body(tokens):
    declarations = None

    accept(tokens, '{')
    declarations = parse_annotation_type_element_declarations(tokens)
    accept(tokens, '}')

    return declarations

@parse_debug
def parse_annotation_type_element_declarations(tokens):
    declarations = list()

    while not would_accept(tokens, '}'):
        declaration = parse_annotation_type_element_declaration(tokens)
        declarations.append(declaration)

    return declarations

@parse_debug
def parse_annotation_type_element_declaration(tokens):
    modifiers, annotations = parse_modifiers(tokens)
    declaration = None

    if would_accept(tokens, 'class'):
        declaration = parse_normal_class_declaration(tokens)
    elif would_accept(tokens, 'interface'):
        declaration = parse_normal_interface_declaration(tokens)
    elif would_accept(tokens, 'enum'):
        declaration = parse_enum_declaration(tokens)
    elif is_annotation_declaration(tokens):
        declaration = parse_annotation_type_declaration(tokens)
    else:
        attribute_type = parse_type(tokens)
        attribute_name = parse_identifier(tokens)
        declaration = parse_annotation_method_or_constant_rest(tokens)
        accept(tokens, ';')

        if isinstance(declaration, tree.AnnotationMethod):
            declaration.name = attribute_name
            declaration.return_type = attribute_type
        else:
            declaration.declarators[0].name = attribute_name
            declaration.type = attribute_type

    declaration.modifiers = modifiers
    declaration.annotations = annotations

    return declaration

@parse_debug
def parse_annotation_method_or_constant_rest(tokens):
    if try_accept(tokens, '('):
        accept(tokens, ')')

        array_dimension = parse_array_dimension(tokens)
        default = None

        if try_accept(tokens, 'default'):
            default = parse_element_value(tokens)

        return tree.AnnotationMethod(dimensions=array_dimension,
                                    default=default)
    else:
        return parse_constant_declarators_rest(tokens)

# ------------------------------------------------------------------------------
# ---- Parsing entry point ----

def parse(tokens):
    tokens = util.LookAheadListIterator(tokens)
    tokens.set_default(EndOfInput(None))

    try:
        return parse_compilation_unit(tokens)

    except JavaSyntaxError as e:
        # Attach current token position if not already specified
        if not e.at:
            e.at = tokens.look()
        raise e

# ------------------------------------------------------------------------------
# ---- Debug control ----

def enable_debug():
    global DEBUG
    DEBUG = True

def disable_debug():
    global DEBUG
    DEBUG = False
