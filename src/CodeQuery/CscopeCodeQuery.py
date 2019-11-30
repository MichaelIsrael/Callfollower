from CodeQuery.AbstractCodeQuery import AbstractCodeQuery, CodeDefinition
from CodeQuery.AbstractCodeQuery import CodeQueryException
from pathlib import Path
import subprocess
import logging
import re


KNOWN_EXTENSIONS = [r"c", r"cpp", r"h"]
CSCOPE_ENTRY_REGEX = r"(?P<File>.+\.({}))\s+" + \
                     r"(?P<Function>(\S+))\s+" + \
                     r"(?P<Line>\d+)\s+" + \
                     r"(?P<Code>.*)"


def BuildRegex():
    return CSCOPE_ENTRY_REGEX.format("|".join(KNOWN_EXTENSIONS))


class CscopeResultFormatError(CodeQueryException):
    def __init__(self, text, regex):
        self.text = text
        self.regex = regex

    def __str__(self):
        return "Failed to parse '%s' by '%s'." % (self.text, self.regex)


class BadCscopeOut(CodeQueryException):
    def __init__(self, CscopeOut):
        self.file = Path(CscopeOut)

    def __str__(self):
        return "'%s' is not valid." % self.file.resolve()


class CscopeError(CodeQueryException):
    def __init__(self, cmd, ret):
        self.cmd = cmd
        self.ret = ret

    def __str__(self):
        return "Command '%s' returned %d." % (self.cmd, self.ret)


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


class CscopeCodeQuery(AbstractCodeQuery):
    def __init__(self, root_dir=r"."):
        # Calling constructor of AbstractCodeQuery
        super(CscopeCodeQuery, self).__init__(root_dir)
        # A list to store cscope arguments.
        self._args = []
        # Get own logger.
        self.log = self.log.getChild("Cscope.%s" %
                                     self.RootPath.resolve().name)

        try:
            # Look for cscope.out in the root directory.
            CscopeOut = tuple(self.RootPath.glob("cscope.out"))[0]
        except IndexError:
            self.log.debug("cscope.out not found.")
            # None is found. Create a new cscope.files.
            self._createFileList()
        else:
            # Make sure cscope.out is a regular file (or a link to one).
            if CscopeOut.is_file():
                self.log.debug("cscope.out found. Adding '-d' to args.")
                # -d tell cscope to skip recreating cscope.out.
                self._args.append("-d")
            else:
                self.log.critical("cscope.out found but is not a file.")
                raise BadCscopeOut(CscopeOut)

    def _createFileList(self):
        self.log.info("Creating a new cscope.files")
        # Create a new cscope.files.
        with open(self.RootPath.joinpath("cscope.files"), "w+") as files:
            # Add all known files.
            for ext in KNOWN_EXTENSIONS:
                self._addToList(files, r"*." + ext)

    def _addToList(self, File, pattern):
        self.log.info("Adding '%s' to the list of files.", pattern)
        # Looking for the pattern recursively in the root directory.
        lst = self.RootPath.rglob(pattern)
        # Add every found file to cscope.files.
        for f in lst:
            self.log.debug("Found '%s'.", f)
            File.write(str(f.resolve())+"\n")

    def _query(self, num, string):
        query = "-L{num}{string}".format(num=num, string=string)
        cscopeCmd = ["cscope", *self._args, query]
        self.log.debug("Running query: '%s'.", cscopeCmd)
        proc = subprocess.run(cscopeCmd,
                              cwd=self.RootPath,
                              encoding="UTF-8",
                              stdout=subprocess.PIPE)
        self.log.debug("Query returned: '%s'.", proc)

        if proc.returncode != 0:
            raise CscopeError(proc.args, proc.returncode)

        return proc.stdout.splitlines()

    def getCaller(self, function):
        output = self._query(3, function)
        callers = [definition
                   for line in output
                   for definition in
                   self.getDefinition(CscopeResult(line).getFunction())]
        self.log.info("Found %d caller(s) of %s: %s.",
                      len(callers),
                      function,
                      str([c.getName() for c in callers]))
        return callers

    def getCalled(self, function):
        output = self._query(2, function)
        called = [definition
                  for line in output
                  for definition in
                  self.getDefinition(CscopeResult(line).getFunction())]
        self.log.info("Found %d function(s) called by %s: %s.",
                      len(called),
                      function,
                      str([c.getName() for c in called]))
        return called

    def getDefinition(self, function):
        output = self._query(1, function)
        definitions = [CscopeCodeDefinition(line) for line in output]
        self.log.info("Found %d definition(s) for %s: %s.",
                      len(definitions),
                      function,
                      str([d.getLocation() for d in definitions]))
        return definitions
