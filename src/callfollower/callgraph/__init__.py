__all__ = ["CallGraph",
           "CallGraphNode",
           "CallGraphEdge",
           "GraphType"
           ]
__author__ = "Michael Israel"


from .callgraph import CallGraph, CallGraphNode, CallGraphEdge
from .graphstylers import BasicStyler, FileStyler  # , ClassStyler
from .pygraphvizgenerator import PygraphvizGenerator
from enum import Enum


class GraphType(Enum):
    PYGRAPHVIZ = PygraphvizGenerator
    DEFAULT = PYGRAPHVIZ


class GraphStyle(Enum):
    BASIC = BasicStyler()
    FILE = FileStyler()
    # CLASS = ClassStyler  # No support for classes yet.
