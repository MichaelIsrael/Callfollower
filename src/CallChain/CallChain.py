from CallGraphGenerator import CallGraphGenerator  # , NodeRole
import logging


class ChainLink:
    def __init__(self, chain, info):
        self._chain = chain
        self._info = info
        self._parents = []
        self._children = []
        self.log = logging.getLogger("CallFollower.CallChain.ChainLink.%s" %
                                     info.getName())

    def __hash__(self):
        return hash(self._info)

    def addParent(self, link):
        """ Link a parent. """
        self.log.debug("Adding a parent: '%s'.", link.getName())
        # Get the parent node and create one if not existing.
        parent = self._chain.getLink(link)
        if parent not in self._parents and link not in parent._children:
            self.log.debug("New parent appended.")
            self._parents.append(parent)
        return parent

    def addChild(self, link):
        """ Link a child. """
        self.log.debug("Adding a child: '%s'.", link.getName())
        # Get the child node and create one if not existing.
        child = self._chain.getLink(link)
        if child not in self._children and link not in child._parents:
            self.log.debug("New child appended.")
            self._children.append(child)
        return child

    def getParents(self):
        """ Return iterator of the link's parents. """
        return iter(self._parents)

    def getChildren(self):
        """ Return iterator of the link's children. """
        return iter(self._children)

    def getName(self):
        return self._info.getName()

    def __repr__(self):
        return "Object ChainLink {} of chain {} [{} parents, {} children]" \
            .format(self._info.getName(),
                    self._chain.getName(),
                    len(self._parents),
                    len(self._children))

    def __str__(self):
        return "ChainLink {}".format(self._info.getName())


class LinksList:
    def __init__(self, chain):
        self.log = logging.getLogger("CallFollower.CallChain.LinksList.%s" %
                                     chain.getName())
        self.log.debug("Creating a new LinksList.")
        self._links = {}
        self._chain = chain

    def __len__(self):
        return len(self._links)

    def __iter__(self):
        return iter(self._links.values())

    def __getitem__(self, key):
        return self._links[hash(key)]

    def create(self, link):
        self.log.debug("Create link: '%s'.", link.getName())
        try:
            return self[link]
        except KeyError:
            self.log.debug("Adding a new link for '%s'.", link.getName())
            newLink = ChainLink(self._chain, link)
            self._links[hash(link)] = newLink
            return newLink


class CallChain:
    def __init__(self, name, root):
        self.log = logging.getLogger("CallFollower.CallChain.CallChain.%s" %
                                     name)
        self.log.debug("Root: '%s'.", root.getName())
        self._name = name
        self._root = root
        self._list = LinksList(self)

    def getRoot(self):
        return self.getLink(self._root)

    def getName(self):
        return self._name

    def getLink(self, link):
        newLink = self._list.create(link)
        return newLink

    def generateGraph(self):
        with CallGraphGenerator(self._name) as graph:
            for link in self._list:
                self.log.debug("Defining: " + link._info.getName())
                graph.define(link._info)

            for link in self._list:
                for child in link.getChildren():
                    self.log.debug("Linking: " + link._info.getName() +
                                   " to " + child._info.getName())
                    graph.link(link._info, child._info)
                for parent in link.getParents():
                    self.log.debug("Linking: " + parent._info.getName() +
                                   " to " + link._info.getName())
                    graph.link(parent._info, link._info)

    def __repr__(self):
        return str(self)

    def __str__(self):
        return "Object CallChain {} [{} links]".format(self._name,
                                                       len(self._list))
