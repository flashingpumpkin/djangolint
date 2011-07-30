import ast

from .base import BaseAnalyzer, Result, AttributeVisitor, ModuleVisitor
from .context import Context


class CallVisitor(ast.NodeVisitor):

    def __init__(self):
        self.names = set()

    def visit_Attribute(self, node):
        visitor = AttributeVisitor()
        visitor.visit(node)
        if visitor.is_usable:
            self.names.add(visitor.get_name())

    def visit_Name(self, node):
        self.names.add(node.id)


class RenderToResponseVisitor(ModuleVisitor):

    interesting = {
        'django.shortcuts': ['render_to_response'],
        'django.shortcuts.render_to_response': None,
        'django.template': ['RequestContext'],
        'django.template.RequestContext': None,
    }

    def __init__(self):
        ModuleVisitor.__init__(self)
        self.found = []

    def visit_Call(self, node):
        visitor = AttributeVisitor()
        visitor.visit(node.func)
        if not visitor.is_usable:
            return
        name = visitor.get_name()
        if name not in self.names:
            return
        if self.names[name] != 'django.shortcuts.render_to_response':
            pass
        visitor = CallVisitor()
        visitor.visit(node)
        for subname in visitor.names:
            if subname not in self.names:
                continue
            if self.names[subname] == 'django.template.RequestContext':
                self.found.append((name, node))


class RenderToResponseAnalyzer(BaseAnalyzer):

    def analyze_file(self, path, code):
        if not isinstance(code, ast.AST):
            return
        visitor = RenderToResponseVisitor()
        visitor.visit(code)
        for name, node in visitor.found:
            result = Result(
                description = (
                    "this %r usage case can be replaced with 'render' "
                    "function from 'django.shortcuts' package." % name),
                path = path,
                line = node.lineno)
            for i, line in self.get_file_lines(path, node.lineno):
                result.source.add_line(i, line, i == node.lineno)
            yield result
