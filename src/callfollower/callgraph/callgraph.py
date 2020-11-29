from .abstractgraphgenerator import GraphGeneratorContextManager, \
                                    AbstractFormattable, GraphTemplateFormatter
from abc import ABC, abstractmethod
from string import Template
import logging


class HashTable(object):
    def __init__(self, *data, **kwargs):
        super().__init__(**kwargs)

        self._table = {}
        for item in data:
            self.insert(item)

    def insert(self, item):
        self._table[hash(item)] = item

    def __getitem__(self, item):
        return self._table[hash(item)]

    def __list__(self):
        return self._table.values()

    def __iter__(self):
        return iter(self._table.values())

    def __delitem__(self, item):
        del self._table[hash(item)]

    def __contains__(self, item):
        return hash(item) in self._table

    def __repr__(self):
        return "HashTable(" + repr(list(self._table.values())) + ")"


class GraphObject(ABC):
    @abstractmethod
    def _hashing_name(self):
        raise NotImplementedError()

    def __hash__(self):
        return hash(self._hashing_name())


class CallGraphNode(GraphObject, AbstractFormattable):
    def __init__(self, name, data, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._name = name
        self._data = dict(data)
        self._edges = []

    def _hashing_name(self):
        return "#".join(map(lambda x: str(x), self._data.values()))

    def add_edge(self, edge):
        self._edges.append(edge)

    @property
    def name(self):
        return self._name

    @property
    def data(self):
        return self._data

    def __repr__(self):
        return "CallGraphNode(" + self.name + " [" + str(hash(self)) + "])"


class CallGraphEdge(GraphObject, AbstractFormattable):
    def __init__(self, source, destination, data, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._source = source
        self._destination = destination
        self._data = dict(data)

    def _hashing_name(self):
        return self._source._hashing_name() + "-" + \
               self._destination._hashing_name()

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, data):
        self._data = data

    @property
    def source(self):
        return self._source

    @property
    def destination(self):
        return self._destination

    def __repr__(self):
        return "CallGraphEdge(" + repr(self.source) +\
               "->" + repr(self.destination) + ")"


class CallGraph(object):
    def __init__(self, name):
        self._log = logging.getLogger("CallFollower.CallChain.CallGraph.%s" %
                                      name)
        self._name = name
        self._nodes_list = HashTable()
        self._edges_list = HashTable()

    def add_node(self, node):
        self._log.info("Adding node: %s", node.name)
        self._nodes_list.insert(node)

    def add_edge(self, edge):
        self._log.info("Adding edge: %s -> %s",
                       edge.source.name,
                       edge.destination.name)

        if edge in self._edges_list:
            self._log.info("Edge already exists. Updating infos.")
            # self._edges_list[edge].data |= edge.data
            self._edges_list[edge].data.update(edge.data)
            return

        # Make sure they are in the nodes list first.
        if edge.source not in self._nodes_list:
            self.add_node(edge.source)
        if edge.destination not in self._nodes_list:
            self.add_node(edge.destination)

        # Update nodes.
        edge.source.add_edge(edge)
        edge.destination.add_edge(edge)

        # Add edge.
        self._edges_list.insert(edge)

    def draw(self, graph_type):
        self._log.info("Drawing graph.")
        with GraphGeneratorContextManager(graph_type, self._name) as graph:
            node_fmt = GraphTemplateFormatter(
                    Template("$filename-$line:\n$function"))
            edge_fmt = GraphTemplateFormatter(
                    Template("$lines"))
            self._log.info("Drawing nodes.")
            for node in self._nodes_list:
                self._log.debug("Node: " + node.name)
                graph.add_node(node, node_fmt)

            self._log.info("Drawing edges.")
            for edge in self._edges_list:
                self._log.debug("Edge: %s -> %s.",
                                edge.source.name,
                                edge.destination.name)
                graph.add_edge(edge, edge_fmt)
