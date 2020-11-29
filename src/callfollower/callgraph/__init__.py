__all__ = ["CallGraph",
           "CallGraphNode",
           "CallGraphEdge",
           "GraphType"
           ]
__author__ = "Michael Israel"


from .callgraph import CallGraph, CallGraphNode, CallGraphEdge
from .graphizgraphgenerator import PygraphvizGenerator
from enum import Enum


class GraphType(Enum):
    Pygraphviz = PygraphvizGenerator
    Default = Pygraphviz
