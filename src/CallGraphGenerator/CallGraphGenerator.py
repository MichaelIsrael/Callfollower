from pathlib import Path
import pygraphviz
import logging
import os


class NodeRole:
    Root = 0
    Parent = 1
    Child = 2


class CallGraphGenerator:
    def __init__(self, name, filename=None, filetype=None):
        self.log = logging.getLogger("CallFollower.CallGraphGenerator.%s" %
                                     name)

        self.name = name

        if filename:
            self.filename = Path(filename)
            if filetype:
                if self.filename.suffix != r"." + filetype:
                    self.log.warning("HHHHEEEYYY")
        else:
            try:
                self.filename = Path(name + r"." + filetype)
            except TypeError:
                self.filename = Path(name + r".png")

        self.count = 0

        self.log.debug("Creating CallGraphGenerator for file '%s'",
                       self.filename)

    def __enter__(self):
        self.open()
        return self

    def open(self):
        self.log.info("Creating file '%s'", self.filename)
        self.AG = pygraphviz.AGraph(name=self.name,
                                    strict=False,
                                    directed=True)
        self.AG.graph_attr.update(ranksep='0.3')
        self.AG.node_attr.update(shape="circle",
                                 fontsize=12,
                                 fontname="Courier",
                                 height=.1)
        self.AG.edge_attr.update(arrowsize=1)

    def define(self, node):
        params = {}
        params['label'] = node.getFullName()
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

        self.log.debug("Defining node '%s'. parameters: %s.",
                       node.getName(), str(params))

        self.AG.add_node("Node" + str(node.getUniqueId()), **params)

    def link(self, n1, n2):
        self.log.debug("Adding link '%s' (%d) to '%s' (%d).",
                       n1.getName(), n1.getUniqueId(),
                       n2.getName(), n2.getUniqueId())
        self.AG.add_edge("Node" + str(n1.getUniqueId()),
                         "Node" + str(n2.getUniqueId()))

    def __exit__(self, *exc_info):
        self.close()
        if exc_info[0]:
            os.remove(self.filename)

    def close(self):
        self.log.info("Closing file '%s'", self.filename)
        self.AG.layout(prog="dot")
        self.AG.draw(self.name+".png")
