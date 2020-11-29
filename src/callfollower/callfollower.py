#!/usr/bin/env python3
from .callgraph import CallGraph, CallGraphNode, CallGraphEdge
from .codeparser import ParserType
import logging


#######################################
# CallFollower                        #
#######################################
class CallFollower:
    def __init__(self, root_dir=r".", parser=ParserType.Default):
        self.log = logging.getLogger("CallFollower.CallFollower")
        self.log.debug("Creating a CodeQuery instance of type '" +
                       str(parser) + "'.")
        self._cquery = parser(root_dir)

    def _createCallerChain(self, graph, node, counter):
        self.log.debug("_createCallerChain: %s. Counter = %d.", node, counter)

        if counter is not None:
            if counter == 0:
                return
            counter -= 1

        callers = self._cquery.getCaller(node.data["function"])

        for caller, line in callers:
            parent = CallGraphNode(caller.function, caller)
            graph.add_edge(CallGraphEdge(parent, node, {"lines": [line]}))
            self._createCallerChain(graph, parent, counter)

    def getCaller(self, function, limit=0):
        self.log.info("Getting callers of '%s' (limit = %d).", function, limit)

        self._cquery.initialize()

        if limit == 0:
            counter = None
        else:
            counter = limit

        graph = CallGraph(function)
        for func_def in self._cquery.getDefinition(function):
            node = CallGraphNode(func_def.function, func_def)
            graph.add_node(node)
            self._createCallerChain(graph, node, counter)
        return graph

    def _createCallingChain(self, graph, node, counter):
        self.log.debug("_createCallingChain: %s. Counter = %d.", node, counter)

        if counter is not None:
            if counter == 0:
                return
            counter -= 1

        called = self._cquery.getCalled(node.data["function"])

        for call, line in called:
            child = CallGraphNode(call.function, call)
            graph.add_edge(CallGraphEdge(node, child, {"lines": [line]}))
            self._createCallingChain(graph, child, counter)

    def getCalled(self, function, limit=0):
        self.log.info("Getting function called by '%s' (limit = %d).",
                      function, limit)

        self._cquery.initialize()

        if limit == 0:
            counter = None
        else:
            counter = limit

        graph = CallGraph(function)
        for func_def in self._cquery.getDefinition(function):
            node = CallGraphNode(func_def.function, func_def)
            graph.add_node(node)
            self._createCallingChain(graph, node, counter)
        return graph

    def getFullTree(self, function, limit=0):
        self.log.info("Getting full call tree of '%s' (limit = %d).",
                      function, limit)

        self._cquery.initialize()

        if limit == 0:
            counter = None
        else:
            counter = limit

        graph = CallGraph(function)
        for func_def in self._cquery.getDefinition(function):
            node = CallGraphNode(func_def.function, func_def)
            graph.add_node(node)
            self._createCallerChain(graph, node, counter)
            self._createCallingChain(graph, node, counter)
        return graph

    def preprocess(self):
        self.log.info("Invoking preprocessor.")
        self._cquery.preprocess()
