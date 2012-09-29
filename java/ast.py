
class MetaNode(type):
    def __new__(mcs, name, bases, dict):
        dict['attrs'] = list(dict['attrs'])

        for base in bases:
            if hasattr(base, 'attrs'):
                dict['attrs'].extend(base.attrs)

        return type.__new__(mcs, name, bases, dict)

class Node(object):
    __metaclass__ = MetaNode

    attrs = ()

    def __init__(self, **kwargs):
        values = kwargs.copy()

        for attr_name in self.attrs:
            value = values.pop(attr_name, None)
            setattr(self, attr_name, value)

        if values:
            raise ValueError('Extraneous arguments')

    def __equals__(self, other):
        if type(other) is type(self):
            return False

        for attr in self.attrs:
            if getattr(other, attr) != getattr(self, attr):
                return False

        return True

    def __repr__(self):
        return type(self).__name__

    def __iter__(self):
        return TreeIterator(self)

    def filter(self, pattern):
        for node in self:
            if ((isinstance(pattern, type) and isinstance(node, node_type)) or
                (node == pattern)):
                yield node

    @property
    def children(self):
        return [getattr(self, attr_name) for attr_name in self.attrs]

class TreeIterator(object):
    def __init__(self, node):
        self.root = node
        self.iter = self.__gen_node()

    def __iter__(self):
        return self

    def __gen_node(self):
        yield (), self.root

        for attr, child in zip(self.root.attrs, self.root.children):
            if isinstance(child, Node):
                for path, node in TreeIterator(child):
                    yield ((self.root, attr),) + path, node

            elif isinstance(child, (tuple, list)):
                for i, childchild in enumerate(child):
                    if isinstance(childchild, Node):
                        for path, node in childchild:
                            yield ((self.root, "{0}[{1}]".format(attr, i)),) + path, node

    def next(self):
        return self.iter.next()
