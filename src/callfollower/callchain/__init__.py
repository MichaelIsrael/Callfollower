__all__ = ["CallGraph",
           "CallGraphNode",
           "CallGraphEdge",
           "GraphType"
           ]
__author__ = "Michael Israel"


from .callgraph import CallGraph, CallGraphNode, CallGraphEdge
from .callgraphgenerator import GraphvizGraphGenerator
from enum import Enum


class GraphType(Enum):
    Graphviz = GraphvizGraphGenerator
    Default = Graphviz
