from .abstractcodeparser import AbstractCodeParser, CodeDefinition
# from .abstractcodeparser import CodeParserException
from . import SUPPORTED_FILE_TYPES
from pycparser import c_ast, parse_file
from collections import namedtuple
# from ..callgraph import CallGraph, CallGraphNode, CallGraphEdge


Function = namedtuple("Function", ["declaration", "calls"])


class CodeVisitor(c_ast.NodeVisitor):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self._graph = CallGraph("Complete Code")
        self._code = {}
        self._scope = None

    def visit_FuncDef(self, node):
        self._code[node.decl.name] = Function(node, [])
        self._scope = node.decl.name
        for c in node:
            self.visit(c)

    def visit_FuncCall(self, node):
        self._code[self._scope].calls.append((node))
        """
        print(node)
        print(node.name)
        print(node.name.name)
        print(node.args)
        print(node.coord)
        """
        for c in node:
            self.visit(c)

    def get_code(self):
        return self._code


class CParser(AbstractCodeParser):
    def __init__(self, root_dir=r"."):
        # Calling constructor of AbstractCodeParser
        super(CParser, self).__init__(root_dir)
        # list of source files.
        self._source_files = []
        self._sources = {}

    def initialize(self):
        self.log.info("Finding source files.")
        for ext in SUPPORTED_FILE_TYPES["C"]:
            # Looking for the pattern recursively in the root directory.
            lst = self.getRootDir().rglob(r"*." + ext)
            # Gathering found files.
            for f in lst:
                self.log.debug("Found '%s'.", f)
                self._source_files.append(f)
        self.preprocess()

    def getCaller(self, function):
        # Quick and dirty (slow) implementation.
        callers = []
        for calling_function, f_data in self._code.items():
            for call in f_data.calls:
                if function in call.name.name:
                    callers.append(
                        (CodeDefinition(f_data.declaration.decl.name,
                                        f_data.declaration.coord.file,
                                        f_data.declaration.coord.line,
                                        ),
                         call.coord.line
                         ))
        return callers

    def getCalled(self, function):
        try:
            calls = self._code[function].calls
        except KeyError:
            return []
            raise  # TODO
        else:
            return [(definition, c.coord.line)
                    for c in calls
                    for definition in self.getDefinition(c.name.name)]

    def getDefinition(self, function):
        try:
            f = self._code[function].declaration
        except KeyError:
            return [CodeDefinition(function, "Not found", 0)]
        else:
            # TODO: Overloading! (C++)
            return [CodeDefinition(f.decl.name, f.coord.file, f.coord.line)]

    def clean(self):
        self._sources = {}

    def preprocess(self):
        self.log.info("Finding source files.")
        code_visitor = CodeVisitor()
        for srcfile in self._source_files:
            self.log.debug("Parsing '%s'.", srcfile)
            self._sources[srcfile] = \
                parse_file(srcfile,
                           use_cpp=True,
                           cpp_args=r'-Iutils/fake_libc_include')
            code_visitor.visit(self._sources[srcfile])
        self._code = code_visitor.get_code()
        """
        for entry in self._code.values():
            print(entry.declaration.decl.name,
                  [call.name.name for call in entry.calls])
        """
