from CallGraphGenerator import CallGraphGenerator  # , NodeRole


class ChainLink:
    def __init__(self, chain, info):
        self._chain = chain
        self._info = info
        self._parents = []
        self._children = []

    def __hash__(self):
        return hash(self._info)

    def addParent(self, link):
        parent = self._chain.getLink(link)
        if parent not in self._parents:
            self._parents.append(parent)
        return parent

    def addChild(self, link):
        child = self._chain.getLink(link)
        if child not in self._children:
            self._children.append(child)
        return child

    def getParents(self):
        return iter(self._parents)

    def getChildren(self):
        return iter(self._children)


class LinksList:
    def __init__(self, chain):
        self._links = {}
        self._chain = chain

    def __len__(self):
        return len(self._links)

    def __iter__(self):
        return iter(self._links.values())

    def __getitem__(self, key):
        return self._links[hash(key)]

    def create(self, link):
        try:
            return self[link]
        except KeyError:
            newLink = ChainLink(self._chain, link)
            self._links[hash(link)] = newLink
            return newLink


class CallChain:
    def __init__(self, name, root):
        self._name = name
        self._root = root
        self._list = LinksList(self)

    def getRoot(self):
        return self.getLink(self._root)

    def getLink(self, link):
        newLink = self._list.create(link)
        return newLink

    def generateGraph(self):
        with CallGraphGenerator(self._name) as graph:
            for link in self._list:
                # print("Defining :"+link._info.getName())
                graph.define(link._info)

            for link in self._list:
                for child in link.getChildren():
                    # print("Linking :" + link._info.getName() + " to " + child._info.getName())
                    graph.link(link._info, child._info)
                for parent in link.getParents():
                    # print("Linking :" + parent._info.getName() + " to " + link._info.getName())
                    graph.link(parent._info, link._info)

    def __repr__(self):
        return str(self)

    def __str__(self):
        return "Object CallChain {} [{} links]".format(self._name,
                                                       len(self._list))
