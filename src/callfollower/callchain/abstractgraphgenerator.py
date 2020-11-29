from abc import ABC, abstractmethod
import logging


class AbstractFormattable(ABC):
    """This is an interface for formattable objects. (can be used with
    GraphFormatter)"""
    @property
    @abstractmethod
    def data(self):
        """This property should return a dict-like object containing all
        available information related to this object."""
        raise NotImplementedError()


class GraphTemplateFormatter(object):
    def __init__(self, template):
        self._template = template

    def __call__(self, formattable):
        return self._template.safe_substitute(formattable.data)


class AbstractGraphGenerator(ABC):
    @abstractmethod
    def open(self):
        raise NotImplementedError()

    @abstractmethod
    def add_node(self, node, formatter=None):
        raise NotImplementedError()

    @abstractmethod
    def add_edge(self, edge, formatter=None):
        raise NotImplementedError()

    @abstractmethod
    def close(self):
        raise NotImplementedError()


class GraphGeneratorContextManager(object):
    def __init__(self, graph_type, *args, **kwargs):
        self.log = logging.getLogger("CallFollower.GraphGenCM")
        self._graph_type = graph_type
        self._args = args
        self._kwargs = kwargs

    def __enter__(self):
        self.graph_gen = self._graph_type(*self._args, **self._kwargs)
        self.graph_gen.open()
        return self.graph_gen

    def __exit__(self, *exc_info):
        self.graph_gen.close()
