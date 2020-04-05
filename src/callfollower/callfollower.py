#!/usr/bin/env python3
from .callchain import CallChain
from .codeparser import ParserType
import logging


#######################################
# CallFollower                        #
#######################################
class CallFollower:
    def __init__(self, root_dir=r".", parser=ParserType.Default):
        self.log = logging.getLogger("CallFollower.CallFollower")
        self.log.debug("Creating a CodeQuery instance of type '" +
                       str(parser) + "'.")
        self._cquery = parser(root_dir)

    def _createCallerChain(self, link, counter):
        self.log.debug("_createCallerChain: %s. Counter = %d.", link, counter)

        if counter is not None:
            if counter != 0:
                counter -= 1
            else:
                return

        callers = self._cquery.getCaller(link.getName())

        for caller, line in callers:
            parent = link.addParent(caller, line)
            self._createCallerChain(parent, counter)

    def getCaller(self, function, limit=0):
        self.log.info("Getting callers of '%s' (limit = %d).", function, limit)

        self._cquery.initialize()

        if limit == 0:
            counter = None
        else:
            counter = limit

        rootFunction = self._cquery.getDefinition(function)[0]
        chain = CallChain(function, rootFunction)
        rootLink = chain.getRoot()
        self._createCallerChain(rootLink, counter)
        return chain

    def _createCallingChain(self, link, counter):
        self.log.debug("_createCallingChain: %s. Counter = %d.", link, counter)

        if counter is not None:
            if counter != 0:
                counter -= 1
            else:
                return

        called = self._cquery.getCalled(link.getName())

        for call, line in called:
            child = link.addChild(call, line)
            self._createCallingChain(child, counter)

    def getCalled(self, function, limit=0):
        self.log.info("Getting function called by '%s' (limit = %d).",
                      function, limit)

        self._cquery.initialize()

        if limit == 0:
            counter = None
        else:
            counter = limit

        rootFunction = self._cquery.getDefinition(function)[0]
        chain = CallChain(function, rootFunction)
        rootLink = chain.getRoot()
        self._createCallingChain(rootLink, counter)
        return chain

    def getFullTree(self, function, limit=0):
        self.log.info("Getting full call tree of '%s' (limit = %d).",
                      function, limit)

        self._cquery.initialize()

        if limit == 0:
            counter = None
        else:
            counter = limit

        rootFunction = self._cquery.getDefinition(function)[0]
        chain = CallChain(function, rootFunction)
        rootLink = chain.getRoot()
        self._createCallerChain(rootLink, counter)
        self._createCallingChain(rootLink, counter)
        return chain

    def preprocess(self):
        self.log.info("Invoking preprocessor.")
        self._cquery.preprocess()
