import os


class NodeRole:
    Root = 0
    Parent = 1
    Child = 2


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

    def define(self, node):
        """
        params = {}
        params['label'] = Label
        params['style'] = "filled"

        if role == NodeRole.Root:
            params['fillcolor'] = "darkgreen"
        elif role == NodeRole.Parent:
            params['fillcolor'] = "blue"
        elif role == NodeRole.Child:
            params['fillcolor'] = "yellow"
        else:
            params['fillcolor'] = "mediumseagreen"
        params = " ".join(['{}={}'.format(k, v) \
                           for k, v in params.items()])
        """
        params = "label={}".format(node.getFullName())
        self.file.write('{} [{}]\n'.format("Node" + str(node.getUniqueId()),
                                           params))

    def link(self, n1, n2):
        self.file.write('{} -> {}\n'.format("Node" + str(n1.getUniqueId()),
                                            "Node" + str(n2.getUniqueId())))

    def __exit__(self, *exc_info):
        self.close()
        if exc_info[0]:
            os.remove(self.filename)

    def close(self):
        self.file.write("}\n")
        self.file.close()
