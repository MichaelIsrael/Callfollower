#!/usr/bin/env python3
from CallChain import CallChain
from CodeQuery import CscopeCodeQuery
import argparse
import logging
import sys
try:
    # Not really necessary.
    import argcomplete
    # PYTHON_ARGCOMPLETE_OK
except ModuleNotFoundError:
    pass


#######################################
# Constants                           #
#######################################
VERSION = {"Major": 0,
           "Minor": 1,
           }
VERSION_TXT = '{Major}.{Minor}'.format(**VERSION)
ARGPARSE_VERSION_TXT = '%(prog)s {}'.format(VERSION_TXT)


#######################################
# CallFollower                        #
#######################################
class CallFollower:
    def __init__(self, root_dir=r"."):
        self.log = logging.getLogger("CallFollower.CallFollower")
        self.log.debug("Creating CscopeCodeQuery instance.")
        self._cquery = CscopeCodeQuery(root_dir)

    def _createCallerChain(self, link, counter):
        self.log.debug("_createCallerChain: %s. Counter = %d.", link, counter)

        if counter is not None:
            if counter != 0:
                counter -= 1
            else:
                return

        callers = self._cquery.getCaller(link.getName())

        for caller in callers:
            parent = link.addParent(caller)
            self._createCallerChain(parent, counter)

    def getCaller(self, function, limit=0):
        self.log.info("Getting callers of '%s' (limit = %d).", function, limit)

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

        for call in called:
            child = link.addChild(call)
            self._createCallingChain(child, counter)

    def getCalled(self, function, limit=0):
        self.log.info("Getting function called by '%s' (limit = %d).",
                      function, limit)

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


#######################################
# Standalone runner.                  #
#######################################
class CallFollowerRunner:
    def __init__(self):
        # Create logger.
        self.rootlog = logging.getLogger("CallFollower")
        StdOutHandler = logging.StreamHandler(sys.stdout)
        StdOutHandler.setFormatter(logging.Formatter('%(name)s: %(message)s'))
        self.rootlog.addHandler(StdOutHandler)
        self.log = logging.getLogger("CallFollower.CallFollowerRunner")

        #######################################################################
        # Start of argparse configuration.                                    #
        #######################################################################
        # Create parser.
        self.parser = argparse.ArgumentParser(
            prog="CallFollower",
            formatter_class=argparse.RawDescriptionHelpFormatter)

        # --version
        self.parser.add_argument('--version',
                                 action='version',
                                 version=ARGPARSE_VERSION_TXT)

        # -v, --verbose
        self.parser.add_argument("-v",
                                 "--verbose",
                                 help="Activate debug mode (show full \
                                       exceptions).",
                                 default=0,
                                 action="count")

        # -d, --dir
        self.parser.add_argument("-d",
                                 "--dir",
                                 help="Root directory for parsing.",
                                 metavar="dir",
                                 default=".",
                                 action="store")

        #######################################################################
        # Adding subparsers.                                                  #
        #######################################################################
        subparsers = self.parser.add_subparsers(metavar="Command",
                                                required=True)

        #######################################################################
        # help                                                                #
        #######################################################################
        CmdHelp = subparsers.add_parser(
                "help",
                help="Show help for a certain command.")

        # Attach command function.
        CmdHelp.set_defaults(subcmd=self.help)

        # Optional positional argument(s) Command.
        CmdHelp.add_argument("Command",
                             nargs="*",
                             default=[],
                             action="store")

        #######################################################################
        # Preprocess                                                          #
        #######################################################################
        CmdPreprocess = subparsers.add_parser(
                "preprocess",
                help="preprocess files for faster execution.")

        # Attach command function.
        CmdPreprocess.set_defaults(subcmd=self.preprocess)

        #######################################################################
        # follow                                                              #
        #######################################################################
        CmdFollow = subparsers.add_parser("follow",
                                          help="create a calling chain.")

        # -l, --limit
        CmdFollow.add_argument("-l",
                               "--limit",
                               help="maximum number of call layers (for each \
                                     direction when all is used.",
                               action="store",
                               type=int,
                               metavar="N",
                               default=0)

        # Create subparsers for follow.
        subfollow = CmdFollow.add_subparsers(metavar="Direction",
                                             required=True)

        #######################################################################
        # follow up                                                           #
        #######################################################################
        CmdUp = subfollow.add_parser(
                "up",
                help="create the chain of calling functions.")

        # Attach command function.
        CmdUp.set_defaults(subcmd=self.followUp)

        # positional argument function.
        CmdUp.add_argument("func",
                           metavar="FUNCTION",
                           action="store")

        # -l, --limit
        CmdUp.add_argument("-l",
                           "--limit",
                           help="maximum number of calling layers.",
                           action="store",
                           type=int,
                           metavar="N",
                           default=0)

        #######################################################################
        # follow down                                                         #
        #######################################################################
        CmdDown = subfollow.add_parser(
                "down",
                help="create the chain of called functions.")

        # Attach command function.
        CmdDown.set_defaults(subcmd=self.followDown)

        # positional argument function.
        CmdDown.add_argument("func",
                             metavar="FUNCTION",
                             action="store")

        # -l, --limit
        CmdDown.add_argument("-l",
                             "--limit",
                             help="maximum number of called layers.",
                             action="store",
                             type=int,
                             metavar="N",
                             default=0)

        #######################################################################
        # follow all                                                          #
        #######################################################################
        CmdAll = subfollow.add_parser(
                "all",
                help="create the chain of both calling and called functions.")

        # Attach command function.
        CmdAll.set_defaults(subcmd=self.followAll)

        # positional argument function.
        CmdAll.add_argument("func",
                            metavar="FUNCTION",
                            action="store")

        # -l, --limit
        CmdAll.add_argument("-l",
                            "--limit",
                            help="maximum number of call layers in each \
                                  direction.",
                            action="store",
                            type=int,
                            metavar="N",
                            default=0)
        #######################################################################
        # End of argpare configuration                                        #
        #######################################################################

        # Bash autocomplete
        try:
            argcomplete.autocomplete(self.parser)
        except NameError:
            pass

    def run(self):
        # Parse arguments
        args = self.parser.parse_args()

        # Parse verbosity
        if args.verbose >= 2:
            self.rootlog.setLevel(logging.DEBUG)
            self.log.debug("Verbosity = %d. Setting log level to DEBUG",
                           args.verbose)
        elif args.verbose == 1:
            self.rootlog.setLevel(logging.INFO)
            self.log.debug("Verbosity = %d. Setting log level to INFO",
                           args.verbose)

        self.log.debug("Started with args %s.", str(args))

        # Create instance of CallFollower only if needed.
        if args.subcmd != self.help:
            self.follower = CallFollower(args.dir)

        # Running subcommand.
        args.subcmd(args)

    def help(self, args):
        """Run the 'help' subcommand."""
        # Add "-h" to the commands and re-run the parser.
        args.Command.append("-h")
        self.parser.parse_args(args.Command)

    def preprocess(self, args):
        """Run the 'preprocess' subcommand."""
        raise NotImplementedError

    def followUp(self, args):
        """Run the 'follow up' subcommand."""
        chain = self.follower.getCaller(args.func, args.limit)
        chain.generateGraph()

    def followDown(self, args):
        """Run the 'follow down' subcommand."""
        chain = self.follower.getCalled(args.func, args.limit)
        chain.generateGraph()

    def followAll(self, args):
        """Run the 'follow all' subcommand."""
        chain = self.follower.getFullTree(args.func, args.limit)
        chain.generateGraph()


if __name__ == "__main__":
    # Create a standalone runnner instanace and run it.
    runner = CallFollowerRunner()
    runner.run()
