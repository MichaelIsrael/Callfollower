from .abstractgraphgenerator import AbstractGraphGenerator
from pathlib import Path
import pygraphviz
import logging
import sys


class GraphvizGraphGenerator(AbstractGraphGenerator):
    _hash_positivier = 2 * (sys.maxsize + 1)

    def __init__(self, name, filename=None, filetype=None):
        self._log = logging.getLogger("CallFollower.CallGraphGenerator.%s" %
                                      name)

        self.name = name

        if filename:
            self.filename = Path(filename)
            if filetype:
                if self.filename.suffix != r"." + filetype:
                    self._log.warning("HHHHEEEYYY")
        else:
            try:
                self.filename = Path(name + r"." + filetype)
            except TypeError:
                self.filename = Path(name + r".png")

        self.count = 0

        self._log.debug("Creating CallGraphGenerator for file '%s'",
                        self.filename)

    def open(self):
        self._log.info("Creating file '%s'", self.filename)
        self.AG = pygraphviz.AGraph(name=self.name,
                                    strict=False,
                                    directed=True)
        self.AG.graph_attr.update(ranksep='0.3')
        self.AG.node_attr.update(shape="circle",
                                 fontsize=12,
                                 fontname="Courier",
                                 height=.1)
        self.AG.edge_attr.update(arrowsize=1)

    def add_group(self, name):
        raise NotImplementedError()

    def add_node(self, node, formatter=None):
        params = {}
        if formatter:
            params['label'] = formatter(node)
        else:
            params['label'] = node.name
        """
        params['style'] = "filled"

        if role == NodeRole.Root:
            params['fillcolor'] = "darkgreen"
        elif role == NodeRole.Parent:
            params['fillcolor'] = "blue"
        elif role == NodeRole.Child:
            params['fillcolor'] = "yellow"
        else:
            params['fillcolor'] = "mediumseagreen"
        """

        self._log.debug("Defining node '%s'. parameters: %s.",
                        node.name, str(params))

        self.AG.add_node("Node" + str(self._get_unique_id(node)), **params)

    def add_edge(self, edge, formatter=None):
        """
        self._log.debug("Adding link '%s' (%d) to '%s' (%d).",
                        n1.name, self._get_unique_id(n1),
                        n2.name, self._get_unique_id(n2))
        """
        text = None
        if formatter:
            try:
                text = formatter(edge)
            except TypeError:
                text = formatter
        self.AG.add_edge("Node" + str(self._get_unique_id(edge.source)),
                         "Node" + str(self._get_unique_id(edge.destination)),
                         label=text,
                         )

    def _get_unique_id(self, obj):
        return hash(obj) % self._hash_positivier

    def close(self):
        self._log.info("Closing file '%s'", self.filename)
        self.AG.layout(prog="dot")
        self.AG.draw(self.name+".png")
