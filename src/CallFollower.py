#!/usr/bin/env python3
from CallChain import CallChain
from CodeQuery import CodeQuery
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
        self._cquery = CodeQuery(root_dir)
        self.log = logging.getLogger("CallFollower")
        out_hdlr = logging.StreamHandler(sys.stdout)
        out_hdlr.setFormatter(logging.Formatter('%(asctime)s %(message)s'))
        # out_hdlr.setLevel(logging.INFO)
        self.log.addHandler(out_hdlr)
        self.log.setLevel(logging.DEBUG)

    def _createCallerChain(self, chain, function, counter):
        self.log.debug("_createCallerChain: %s %s", chain, function)
        if counter is not None:
            if counter != 0:
                counter -= 1
            else:
                return

        callers = self._cquery.getCaller(function)

        for caller in callers:
            parent = chain.createParent(caller)
            self._createCallerChain(parent, caller.getName(), counter)

    def getCaller(self, function, limit=0):
        if limit == 0:
            counter = None
        else:
            counter = limit

        chain = CallChain(function)
        self._createCallerChain(chain, function, counter)
        return chain

    def _createCallingChain(self, chain, function, counter):
        self.log.debug("_createCallingChain: %s %s", chain, function)
        if counter is not None:
            if counter != 0:
                counter -= 1
            else:
                return
            # raise NotImplementedError

        called = self._cquery.getCalled(function)

        for call in called:
            child = chain.createChild(call)
            self._createCallingChain(child, call.getName(), counter)

    def getCalled(self, function, limit=0):
        if limit == 0:
            counter = None
        else:
            counter = limit

        chain = CallChain(function)
        self._createCallingChain(chain, function, counter)
        return chain

    def getFullTree(self, function, limit=0):
        if limit == 0:
            counter = None
        else:
            counter = limit

        chain = CallChain(function)
        self._createCallerChain(chain, function, counter)
        self._createCallingChain(chain, function, counter)
        return chain


#######################################
# Standalone runner.                  #
#######################################
class CallFollowerRunner:
    def __init__(self):
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
        print(args)

        # Create instance of CallFollower only if needed.
        if args.subcmd != self.help:
            # TODO: Verbose
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
