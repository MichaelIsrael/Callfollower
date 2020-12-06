from abc import ABC, abstractmethod
from .abstractgraphgenerator import GraphTemplateFormatter
from string import Template


class AbstractGraphStyler(ABC):
    @abstractmethod
    def get_group_from_node(self, node):
        raise NotImplementedError()

    @property
    @abstractmethod
    def node_formatter(self):
        raise NotImplementedError()

    @property
    @abstractmethod
    def edge_formatter(self):
        raise NotImplementedError()


class BasicStyler(AbstractGraphStyler):
    def get_group_from_node(self, node):
        return None

    @property
    def node_formatter(self):
        return GraphTemplateFormatter(Template("$filename-$line:\n$function"))

    @property
    def edge_formatter(self):
        return GraphTemplateFormatter(Template("$lines"))


class FileStyler(AbstractGraphStyler):
    def get_group_from_node(self, node):
        return node.data["filename"]

    @property
    def node_formatter(self):
        return GraphTemplateFormatter(Template("$function ($line)"))

    @property
    def edge_formatter(self):
        return GraphTemplateFormatter(Template("$lines"))


class ClassStyler(AbstractGraphStyler):
    def get_group_from_node(self, node):
        return node.data["classname"]
