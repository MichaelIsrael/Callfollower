from .abstractcodeparser import AbstractCodeParser, CodeDefinition
from .abstractcodeparser import CodeParserException
from . import SUPPORTED_FILE_TYPES
from pathlib import Path
import subprocess
import logging
import re


CSCOPE_ENTRY_REGEX = r"(?P<File>.+\.({}))\s+" + \
                     r"(?P<Function>(\S+))\s+" + \
                     r"(?P<Line>\d+)\s+" + \
                     r"(?P<Code>.*)"


def BuildRegex():
    return CSCOPE_ENTRY_REGEX.format("|".join(SUPPORTED_FILE_TYPES["C"]))


class CscopeResultFormatError(CodeParserException):
    def __init__(self, text, regex):
        self.text = text
        self.regex = regex

    def __str__(self):
        return "Failed to parse '%s' by '%s'." % (self.text, self.regex)


class BadCscopeFile(CodeParserException):
    def __init__(self, CscopeOut):
        self.file = Path(CscopeOut)

    def __str__(self):
        return "'%s' is not valid." % self.file.resolve()


class CscopeError(CodeParserException):
    def __init__(self, cmd, ret):
        self.cmd = cmd
        self.ret = ret

    def __str__(self):
        return "Command '%s' returned %d." % (self.cmd, self.ret)


class CscopeNotInstalledError(CodeParserException):
    def __str__(self):
        return "cscope is not installed."


class CscopeResult:
    def __init__(self, entry):
        self.log = logging.getLogger("CallFollower.CscopeResult")
        self.log.debug("Parsing entry '%s'.", entry)
        regex = BuildRegex()
        match = re.match(regex, entry)
        if match:
            self.log.debug("Parsing returned '%s'.", str(match.groupdict()))
            self.info = match.groupdict()
        else:
            raise CscopeResultFormatError(entry, regex)

    def getFunction(self):
        return self.info["Function"]

    def getFile(self):
        return self.info["File"]

    def getLine(self):
        return int(self.info["Line"])

    def getCode(self):
        return self.info["Code"]


class CscopeCodeDefinition(CodeDefinition):
    def __init__(self, entry):
        result = CscopeResult(entry)
        super(CscopeCodeDefinition, self).__init__(result.getFunction(),
                                                   result.getFile(),
                                                   result.getLine())


class Cscope(AbstractCodeParser):
    def __init__(self, root_dir=r"."):
        # Calling constructor of AbstractCodeParser
        super(Cscope, self).__init__(root_dir)
        # A list to store cscope arguments.
        self._args = []

    def initialize(self):
        try:
            # Look for cscope.out in the root directory.
            CscopeOut = tuple(self.getRootDir().glob("cscope.out"))[0]
        except IndexError:
            self.log.debug("cscope.out not found.")
            # None is found. Preprocess sources.
            self.preprocess()
        else:
            # Make sure cscope.out is a regular file (or a link to one).
            if not CscopeOut.is_file():
                self.log.critical("cscope.out found but is not a file.")
                raise BadCscopeFile(CscopeOut)

    def _createFileList(self):
        self.log.info("Creating a new cscope.files")
        # Create a new cscope.files.
        with open(self.getRootDir().joinpath("cscope.files"), "w+") as files:
            # Add all known files.
            for ext in SUPPORTED_FILE_TYPES["C"]:
                self._addToList(files, r"*." + ext)

    def _addToList(self, File, pattern):
        self.log.info("Adding '%s' to the list of files.", pattern)
        # Looking for the pattern recursively in the root directory.
        lst = self.getRootDir().rglob(pattern)
        # Add every found file to cscope.files.
        for f in lst:
            self.log.debug("Found '%s'.", f)
            File.write(str(f.resolve())+"\n")

    def _query(self, num, string):
        query = "-qL{num}{string}".format(num=num, string=string)
        cscopeCmd = ["cscope", *self._args, query]
        self.log.debug("Running query: '%s'.", cscopeCmd)
        try:
            proc = subprocess.run(cscopeCmd,
                                  cwd=self.getRootDir(),
                                  check=True,
                                  capture_output=True,
                                  text=True)
        except subprocess.CalledProcessError as e:
            raise CscopeError(e.cmd, e.returncode) from None

        self.log.debug("Query returned: '%s'.", proc.returncode)

        return proc.stdout.splitlines()

    def getCaller(self, function):
        output = self._query(3, function)
        callers = [(definition, CscopeResult(line).getLine())
                   for line in output
                   for definition in
                   self.getDefinition(CscopeResult(line).getFunction())]
        self.log.info("Found %d caller(s) of %s: %s.",
                      len(callers),
                      function,
                      str([(c[0].getName(), c[1]) for c in callers]))
        return callers

    def getCalled(self, function):
        output = self._query(2, function)
        called = [(definition, CscopeResult(line).getLine())
                  for line in output
                  for definition in
                  self.getDefinition(CscopeResult(line).getFunction())]
        self.log.info("Found %d function(s) called by %s: %s.",
                      len(called),
                      function,
                      str([(c[0].getName(), c[1]) for c in called]))
        return called

    def getDefinition(self, function):
        output = self._query(1, function)
        definitions = [CscopeCodeDefinition(line) for line in output]
        self.log.info("Found %d definition(s) for %s: %s.",
                      len(definitions),
                      function,
                      str([d.getLocation() for d in definitions]))
        return definitions

    def clean(self):
        self.log.info("Deleting cscope files.")
        files = [r"cscope.out", r"cscope.files",
                 r"cscope.in.out", r"cscope.po.out",
                 ]
        for f in files:
            out = self.getRootDir().joinpath(f)
            self.log.debug("Removing '%s'.", out.resolve())
            try:
                out.unlink()
            except FileNotFoundError:
                self.log.debug("'%s' was not found.", out.resolve())
                pass

    def preprocess(self):
        self.log.info("Preprocessing sources.")

        # Remove old files.
        self.clean()

        # Create list of source files.
        self._createFileList()

        # Create cscope database.
        cscopeCmd = ["cscope", "-qb"]
        self.log.debug("Building database using '%s'.", cscopeCmd)
        try:
            proc = subprocess.run(cscopeCmd,
                                  cwd=self.getRootDir(),
                                  check=True,
                                  capture_output=True,
                                  text=True)
        except subprocess.CalledProcessError as e:
            raise CscopeError(e.cmd, e.returncode) from None

        self.log.debug("Cscope returned: '%s'.", proc.returncode)

        # -d tells cscope not to update the cross-reference.
        self._args.append("-d")


# make sure cscope is installed.
cscopeVersionCmd = ["cscope", "--version"]
try:
    # Note: For some reason, cscope prints the version to stderr.
    proc = subprocess.run(cscopeVersionCmd,
                          timeout=2,
                          check=True,
                          capture_output=True,
                          text=True)
except OSError:
    raise CscopeNotInstalledError() from None
except subprocess.CalledProcessError as e:
    raise CscopeError(e.cmd, e.returncode) from None
