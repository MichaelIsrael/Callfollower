from CallGraphGenerator import CallGraphGenerator  # , NodeRole


class CallChain:
    def __init__(self, info):
        try:
            self._name = info.name
        except AttributeError:
            self._name = info
            self._info = None
        else:
            self._info = info
        self.Parents = []
        self.Children = []

    def getName(self):
        return self._name

    def __eq__(self, other):
        return self._info == other._info

    def createParent(self, link):
        # TODO: Check if parent already exists
        newParent = CallChain(link)
        if newParent not in self.Parents:
            self.Parents.append(newParent)
        return newParent

    def createChild(self, link):
        # TODO: Check if child already exists
        newChild = CallChain(link)
        if newChild not in self.Children:
            self.Children.append(newChild)
        return newChild

    def _writeNode(self, graph):
        MeNode = graph.addNode(self.getName())

        ChildrenNodes = []
        for child in self.Children:
            childNode = child._writeNode(graph)
            ChildrenNodes.append(childNode)
            MeNode.linkChildren(childNode)

        ParentNodes = []
        for parent in self.Parents:
            parentNode = parent._writeNode(graph)
            ParentNodes.append(parentNode)
            MeNode.linkParents(parentNode)

        return MeNode

    def generateGraph(self):
        with CallGraphGenerator(self.getName()) as graph:
            self._writeNode(graph)

    def __repr__(self):  # TODO: Working-around! Remove!
        return str(self)

    def __str__(self):
        # TODO:
        return str(self.Parents)+"\n"+str(self.getName())+"\n"+str(self.Children)
