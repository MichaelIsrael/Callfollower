from .abstractgraphgenerator import AbstractGraphGenerator
from pathlib import Path
import pygraphviz
import logging
import sys


class PygraphvizGenerator(AbstractGraphGenerator):
    _hash_positivier = 2 * (sys.maxsize + 1)

    def __init__(self, name, filename=None, filetype=None, group_fcn=None):
        self._log = logging.getLogger("CallFollower.CallGraphGenerator.%s" %
                                      name)

        self._name = name
        self._group_fcn = group_fcn
        self._groups = {}

        if filename:
            self._filename = Path(filename)
            if filetype and \
               self._filename.suffix.lower() != r"." + filetype.lower():
                self._log.warning("FileType does not match the file extension\
                 (%s - %s).", filetype, filename)
        else:
            try:
                self._filename = Path(name + r"." + filetype)
            except TypeError:
                self._filename = Path(name + r".png")

        self._log.debug("Creating CallGraphGenerator for file '%s'",
                        self._filename)

    def open(self):
        self._log.info("Creating file '%s'", self._filename)
        self._agraph = pygraphviz.AGraph(name=self._name,
                                         strict=False,
                                         directed=True)
        self._agraph.graph_attr.update(ranksep='0.3')
        self._agraph.node_attr.update(shape="circle",
                                      fontsize=12,
                                      fontname="Courier",
                                      height=.1)
        self._agraph.edge_attr.update(arrowsize=1)

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

        self._log.debug("Creating node '%s'. parameters: %s.",
                        node.name, str(params))
        self._agraph.add_node("Node" + str(self._get_unique_id(node)),
                              **params)

        if self._group_fcn:
            group = self._group_fcn(node)
            if group:
                subgraph = self._agraph.get_subgraph(name="cluster_" + group)
                if not subgraph:
                    subgraph = self._agraph.add_subgraph(name="cluster_"+group,
                                                         label=group,
                                                         style="rounded",
                                                         )
                self._log.debug("Node added to group '%s'", group)
                subgraph.add_node("Node" + str(self._get_unique_id(node)))

    def add_edge(self, edge, formatter=None):
        self._log.debug("Creating edge: '%s' (%d) -> '%s' (%d).",
                        edge.source.name,
                        self._get_unique_id(edge.source),
                        edge.destination.name,
                        self._get_unique_id(edge.destination)
                        )
        text = None
        if formatter:
            try:
                text = formatter(edge)
            except TypeError:
                text = formatter
        self._agraph.add_edge(
            "Node" + str(self._get_unique_id(edge.source)),
            "Node" + str(self._get_unique_id(edge.destination)),
            label=text,
            )

    def _get_unique_id(self, obj):
        return hash(obj) % self._hash_positivier

    def close(self):
        self._log.info("Closing file '%s'", self._filename)
        self._agraph.layout(prog="dot")
        self._agraph.draw(self._name+".png")
