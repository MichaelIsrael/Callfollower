import os


class NodeRole:
    Root = 0
    Parent = 1
    Child = 2


class CallGraphNode:
    def __init__(self, Id, Label, File, role=None):
        # Store arguments.
        self.Id = Id
        self.Label = Label
        self.File = File
        self.params = {}
        self.params['label'] = Label
        """
        self.params['style'] = "filled"

        if role == NodeRole.Root:
            self.params['fillcolor'] = "darkgreen"
        elif role == NodeRole.Parent:
            self.params['fillcolor'] = "blue"
        elif role == NodeRole.Child:
            self.params['fillcolor'] = "yellow"
        else:
            self.params['fillcolor'] = "mediumseagreen"
        """

        # Write node definition.
        self._define()

    def getName(self):
        """Function to return the link's internal name."""
        return "Node" + str(self.Id)

    def _define(self):
        """Function to write the link's defintion to the file."""
        params = " ".join(['{}={}'.format(k, v) \
                           for k, v in self.params.items()])
        self.File.write('{} [{}]\n'.format(self.getName(), params))

    def linkChildren(self, Node):
        """Function to link to a different node."""
        # TODO: What if the file was already closed?
        self.File.write('{} -> {}\n'.format(self.getName(), Node.getName()))

    def linkParents(self, Node):
        """Function to link to a different node."""
        # TODO: What if the file was already closed?
        #self.File.write('{} <- {}\n'.format(self.getName(), Node.getName()))
        self.File.write('{} -> {}\n'.format(Node.getName(), self.getName()))


class CallGraphGenerator:
    def __init__(self, name):
        self.name = name
        self.filename = name + r".gv"
        self.count = 0

    def __enter__(self):
        self.open()
        return self

    def open(self):
        self.file = open(self.filename, 'w')
        self.file.write("""digraph %s {
node [shape=circle, fontsize=12, fontname="Courier", height=.1];
ranksep=.3;
edge [arrowsize=.5]
""" % self.name)

    def addNode(self, label):
        self.count += 1
        newNode = CallGraphNode(self.count, label, self.file)
        return newNode

    def __exit__(self, *exc_info):
        self.close()
        if exc_info[0]:
            os.remove(self.filename)

    def close(self):
        self.file.write("}\n")
        self.file.close()


